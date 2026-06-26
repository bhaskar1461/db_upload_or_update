from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


ROOT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AppConfig:
    """Central configuration for paths, model names, and generation defaults."""

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    chroma_dir: Path = ROOT_DIR / os.getenv("CHROMA_DIR", "data/chroma_db")
    uploads_dir: Path = ROOT_DIR / "data/uploads"
    output_dir: Path = (ROOT_DIR / os.getenv("OUTPUT_DIR", "../Generated_Exam_PDFs")).resolve()
    logs_dir: Path = ROOT_DIR / "logs"
    default_collection: str = "exam_notes"
    default_chunk_size: int = 1200
    default_chunk_overlap: int = 180
    default_top_k: int = 8
    default_temperature: float = 0.25
    default_max_tokens: int = 2500
    default_context_length: int = int(os.getenv("OLLAMA_CONTEXT_LENGTH", "8192"))

    def ensure_dirs(self) -> None:
        for directory in [self.chroma_dir, self.uploads_dir, self.output_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)


config = AppConfig()
config.ensure_dirs()
