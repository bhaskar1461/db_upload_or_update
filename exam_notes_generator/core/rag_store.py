from __future__ import annotations

import hashlib
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable

import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from .config import config
from .logger import get_logger
from .pdf_loader import ExtractedPage
from .text_utils import clean_text


logger = get_logger(__name__)
_embedding_model: "SentenceTransformer | None" = None
_collections: dict[str, object] = {}


def _get_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(config.embedding_model, local_files_only=True)
    return _embedding_model


class LocalEmbeddingFunction(EmbeddingFunction[Documents]):
    """Chroma embedding adapter backed by sentence-transformers."""

    def __init__(self, model_name: str = config.embedding_model):
        self.model_name = model_name

    @staticmethod
    def name() -> str:
        return "local_sentence_transformer"

    def __call__(self, input: Documents) -> Embeddings:
        model = _get_model()
        vectors = model.encode(
            list(input),
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return vectors.tolist()

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "LocalEmbeddingFunction":
        return LocalEmbeddingFunction()

    def get_config(self) -> Dict[str, Any]:
        return {"model_name": self.model_name}


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(config.chroma_dir))


_ef_instance: "LocalEmbeddingFunction | None" = None


def get_embedding_function() -> LocalEmbeddingFunction:
    global _ef_instance
    if _ef_instance is None:
        _ef_instance = LocalEmbeddingFunction()
    return _ef_instance


def get_collection(name: str = config.default_collection):
    if name in _collections:
        return _collections[name]
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=name,
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )
    _collections[name] = collection
    return collection


def make_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
    )


def _chunk_id(page: ExtractedPage, chunk_text: str, chunk_index: int) -> str:
    raw = f"{page.source}|{page.page}|{chunk_index}|{chunk_text[:80]}"
    return hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()


def index_pages(
    pages: Iterable[ExtractedPage],
    collection_name: str,
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    """Split extracted pages into overlapping chunks and store them in Chroma."""

    collection = get_collection(collection_name)
    splitter = make_splitter(chunk_size, chunk_overlap)

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for page in pages:
        chunks = splitter.split_text(page.text)
        for chunk_index, chunk in enumerate(chunks):
            chunk = clean_text(chunk)
            if len(chunk) < 40:
                continue
            ids.append(_chunk_id(page, chunk, chunk_index))
            documents.append(chunk)
            metadata = asdict(page)
            metadata.pop("text", None)
            metadata["chunk_index"] = chunk_index
            metadatas.append(metadata)

    if not documents:
        return 0

    batch_size = 256
    for start in range(0, len(documents), batch_size):
        end = start + batch_size
        collection.upsert(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

    logger.info("Indexed %s chunks into collection '%s'", len(documents), collection_name)
    return len(documents)


def retrieve_chunks(
    query: str,
    collection_name: str,
    subject: str | None = None,
    unit: str | None = None,
    top_k: int = config.default_top_k,
) -> list[dict]:
    """Run semantic retrieval with optional subject/unit filters."""

    collection = get_collection(collection_name)
    where_filters: list[dict] = []
    if subject:
        where_filters.append({"subject": subject})
    if unit:
        where_filters.append({"unit": unit})

    if len(where_filters) > 1:
        where = {"$and": where_filters}
    elif len(where_filters) == 1:
        where = where_filters[0]
    else:
        where = None

    result = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    chunks: list[dict] = []
    for document, metadata, distance in zip(
        result.get("documents", [[]])[0],
        result.get("metadatas", [[]])[0],
        result.get("distances", [[]])[0],
    ):
        chunks.append({"text": document, "metadata": metadata, "distance": distance})
    return chunks


def collection_stats(collection_name: str) -> dict:
    collection = get_collection(collection_name)
    count = collection.count()
    return {"collection": collection_name, "chunks": count, "path": str(config.chroma_dir)}


def catalog(collection_name: str, limit: int = 10_000) -> dict[str, list[str]]:
    """Return detected subjects and units from stored metadata."""

    collection = get_collection(collection_name)
    result = collection.get(limit=limit, include=["metadatas"])
    subjects: dict[str, set[str]] = {}

    for metadata in result.get("metadatas", []):
        subject = str(metadata.get("subject") or "General")
        unit = str(metadata.get("unit") or "Unit")
        subjects.setdefault(subject, set()).add(unit)

    return {subject: sorted(units) for subject, units in sorted(subjects.items())}


def delete_collection(collection_name: str) -> None:
    client = get_chroma_client()
    try:
        _collections.pop(collection_name, None)
        client.delete_collection(collection_name)
    except Exception as exc:
        logger.warning("Could not delete collection '%s': %s", collection_name, exc)
