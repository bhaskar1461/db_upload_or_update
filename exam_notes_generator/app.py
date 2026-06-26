from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

from core.config import config
from core.generator import generate_notes
from core.llm_client import check_llm
from core.pdf_exporter import export_notes_to_pdf
from core.pdf_loader import discover_pdfs, extract_many, save_uploaded_pdfs
from core.rag_store import catalog, collection_stats, delete_collection, index_pages


if sys.platform == "win32":
    # Keeps Windows console/log output from failing on Unicode paths or Hindi text.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


st.set_page_config(page_title="Proxima-Level Exam Notes Generator", layout="wide")

st.title("Proxima-Level AI Exam Notes Generator")
st.caption("High-quality RAG notes from PDFs using OpenAI GPT-4o, ChromaDB, and sentence-transformers.")

with st.sidebar:
    st.header("Cloud API Model")
    ok, message = check_llm()
    st.success(message) if ok else st.error(message)
    if not ok:
        st.code("$env:OPENAI_API_KEY='your-key-here'", language="powershell")

    st.header("Settings")
    collection_name = st.text_input("Chroma collection", value=config.default_collection)
    chunk_size = st.slider("Chunk size", 600, 2400, config.default_chunk_size, 100)
    chunk_overlap = st.slider("Chunk overlap", 50, 500, config.default_chunk_overlap, 10)
    top_k = st.slider("Retrieved chunks", 3, 30, config.default_top_k, 1)
    context_length = st.select_slider("LLM context", [4096, 8192, 12000, 16000, 32000], value=config.default_context_length)
    max_tokens = st.slider("Max output tokens", 800, 8000, config.default_max_tokens, 100)
    temperature = st.slider("Temperature", 0.0, 1.0, config.default_temperature, 0.05)

    if st.button("Clear current vector index", type="secondary"):
        delete_collection(collection_name)
        st.success(f"Deleted collection: {collection_name}")

stats = collection_stats(collection_name)
st.info(f"Vector store: {stats['chunks']} chunks in `{stats['collection']}` at `{stats['path']}`")
detected_catalog = catalog(collection_name) if stats["chunks"] else {}

tab_ingest, tab_generate = st.tabs(["1. Ingest PDFs", "2. Generate Notes"])

with tab_ingest:
    st.subheader("Add Study Material")
    subject = st.text_input("Subject name", value="General")

    upload_col, folder_col = st.columns(2)
    with upload_col:
        st.markdown("**Upload PDFs**")
        uploaded_files = st.file_uploader(
            "Choose one or more PDFs",
            type=["pdf"],
            accept_multiple_files=True,
        )
        if st.button("Index uploaded PDFs", disabled=not uploaded_files):
            with st.spinner("Saving, extracting, chunking, and embedding uploaded PDFs..."):
                saved = save_uploaded_pdfs(uploaded_files, subject=subject)
                pages = extract_many(saved, subject=subject)
                chunks = index_pages(pages, collection_name, chunk_size, chunk_overlap)
            st.success(f"Indexed {chunks} chunks from {len(saved)} PDFs.")

    with folder_col:
        st.markdown("**Scan a local folder**")
        folder_input = st.text_input(
            "Folder path",
            value=str(Path.cwd().parent),
            help="Example: C:\\Users\\bhask\\Desktop\\New folder\\English\\8th class",
        )
        if st.button("Index folder PDFs"):
            folder = Path(folder_input).expanduser()
            pdfs = discover_pdfs(folder)
            if not pdfs:
                st.error("No PDFs found in that folder.")
            else:
                progress = st.progress(0, text="Extracting PDFs...")
                pages = []
                for index, pdf_path in enumerate(pdfs, start=1):
                    pages.extend(extract_many([pdf_path], subject=subject, root=folder))
                    progress.progress(index / len(pdfs), text=f"Extracted {index}/{len(pdfs)} PDFs")
                with st.spinner("Chunking and embedding into ChromaDB..."):
                    chunks = index_pages(pages, collection_name, chunk_size, chunk_overlap)
                st.success(f"Indexed {chunks} chunks from {len(pdfs)} PDFs.")

with tab_generate:
    st.subheader("Generate Exam-Oriented Notes")
    if detected_catalog:
        with st.expander("Detected subjects and units from indexed PDFs"):
            for detected_subject, units in detected_catalog.items():
                st.write(f"**{detected_subject}**")
                st.caption(", ".join(units[:30]) + (" ..." if len(units) > 30 else ""))

    gen_col_1, gen_col_2 = st.columns(2)
    with gen_col_1:
        subjects = list(detected_catalog.keys())
        if subjects:
            gen_subject = st.selectbox("Subject", subjects, key="gen_subject")
            units = detected_catalog.get(gen_subject, [])
            unit = st.selectbox("Detected unit / chapter", units or ["Unit 1"])
            custom_unit = st.text_input("Or type a custom unit/topic", value="")
            unit = custom_unit.strip() or unit
        else:
            gen_subject = st.text_input("Subject", value=subject, key="gen_subject")
            unit = st.text_input("Unit / chapter / topic", value="Unit 1")
    with gen_col_2:
        mode = st.selectbox(
            "Mode",
            ["Full Exam Notes", "Quick Revision", "Long Answer Mode", "Cheat Sheet", "Question Bank"],
        )
        extra_instruction = st.text_area("Extra instruction", placeholder="Example: Focus on 2-mark questions and formulas.")

    if st.button("Generate notes with OpenAI", type="primary"):
        if not ok:
            st.error("OpenAI API key is missing. Set it first.")
        elif stats["chunks"] == 0:
            st.error("Index PDFs first. The vector store is empty.")
        else:
            with st.spinner("Retrieving chunks and generating notes..."):
                notes, chunks = generate_notes(
                    subject=gen_subject,
                    unit=unit,
                    mode=mode,
                    collection_name=collection_name,
                    top_k=top_k,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    context_length=context_length,
                    extra_instruction=extra_instruction,
                )
                pdf_path = export_notes_to_pdf(notes, gen_subject, unit)
                st.session_state["notes"] = notes
                st.session_state["pdf_path"] = str(pdf_path)
                st.session_state["chunks"] = chunks

    if "notes" in st.session_state:
        st.markdown(st.session_state["notes"])
        st.success(f"PDF saved automatically: {st.session_state['pdf_path']}")
        with st.expander("Retrieved source chunks"):
            for chunk in st.session_state.get("chunks", []):
                meta = chunk["metadata"]
                st.write(f"{meta.get('source')} | page {meta.get('page')} | PYQ: {meta.get('is_pyq')}")
                st.caption(chunk["text"][:700])
