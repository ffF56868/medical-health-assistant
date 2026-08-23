"""Cleaning and chunking rules used only when building the vector index."""

from __future__ import annotations

import re
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


TEXT_CLEANING_VERSION = "medical-text-clean-v1"
CHUNKING_STRATEGY = "recursive-chinese-v1"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120

TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    # Prefer paragraph and Chinese sentence boundaries before splitting by
    # smaller punctuation, so each chunk stays readable on its own.
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", "",],
    add_start_index=True,
)


@dataclass(frozen=True)
class CleanedText:
    text: str
    original_character_count: int
    removed_blank_line_count: int
    removed_duplicate_line_count: int


def clean_text_for_embedding(text: str) -> CleanedText:
    """Remove formatting noise while preserving the stored source text."""
    original = text or ""
    normalized = (
        original.replace("\ufeff", "")
        .replace("\u200b", "")
        .replace("\u00a0", " ")
        .replace("\u3000", " ")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    cleaned_lines: list[str] = []
    previous_nonempty_line: str | None = None
    blank_line_kept = False
    removed_blank_line_count = 0
    removed_duplicate_line_count = 0

    for raw_line in normalized.split("\n"):
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line:
            if cleaned_lines and not blank_line_kept:
                cleaned_lines.append("")
                blank_line_kept = True
            else:
                removed_blank_line_count += 1
            previous_nonempty_line = None
            continue

        if line == previous_nonempty_line:
            removed_duplicate_line_count += 1
            continue

        cleaned_lines.append(line)
        previous_nonempty_line = line
        blank_line_kept = False

    return CleanedText(
        text="\n".join(cleaned_lines).strip(),
        original_character_count=len(original),
        removed_blank_line_count=removed_blank_line_count,
        removed_duplicate_line_count=removed_duplicate_line_count,
    )


def split_document_for_embedding(document: Document) -> list[Document]:
    """Clean one source record, then add traceable metadata to each chunk."""
    cleaned = clean_text_for_embedding(document.page_content)
    if not cleaned.text:
        return []

    cleaned_document = Document(
        page_content=cleaned.text,
        metadata={
            **document.metadata,
            "text_cleaning_version": TEXT_CLEANING_VERSION,
            "original_character_count": cleaned.original_character_count,
            "cleaned_character_count": len(cleaned.text),
            "removed_blank_line_count": cleaned.removed_blank_line_count,
            "removed_duplicate_line_count": cleaned.removed_duplicate_line_count,
        },
    )
    chunks = TEXT_SPLITTER.split_documents([cleaned_document])
    chunk_count = len(chunks)

    for chunk_index, chunk in enumerate(chunks):
        start_index = int(chunk.metadata.pop("start_index", 0))
        chunk.metadata.update(
            {
                "chunk_index": chunk_index,
                "chunk_count": chunk_count,
                "chunk_start_index": start_index,
                "chunk_end_index": start_index + len(chunk.page_content),
                "chunk_character_count": len(chunk.page_content),
                "chunking_strategy": CHUNKING_STRATEGY,
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
            }
        )
    return chunks


def get_text_processing_config() -> dict[str, str | int]:
    return {
        "text_cleaning_version": TEXT_CLEANING_VERSION,
        "chunking_strategy": CHUNKING_STRATEGY,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
    }
