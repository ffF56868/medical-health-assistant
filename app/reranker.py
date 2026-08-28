"""Lightweight second-stage reranking for retrieved knowledge records.

The first stage gathers candidates with vector and keyword retrieval. This
module scores the question against each candidate again, giving direct title
and content matches more weight before the answer model sees the context.
It is deliberately local and deterministic; a pretrained cross-encoder can
be added later without changing the retrieval contract.
"""

from __future__ import annotations

import re

from langchain_core.documents import Document


ORIGINAL_SCORE_WEIGHT = 0.45
TEXT_MATCH_WEIGHT = 0.35
TITLE_MATCH_WEIGHT = 0.20

RERANK_STOP_WORDS = {
    "什么",
    "怎么",
    "如何",
    "可以",
    "是否",
    "有没有",
    "请问",
    "一下",
    "相关",
    "资料",
    "问题",
    "哪些",
    "哪里",
    "这个",
    "那个",
    "以及",
    "还有",
}

# These title fragments identify a document format rather than a medical
# topic, so they should not elevate every specialty overview during reranking.
GENERIC_TITLE_PHRASES = (
    "专科概览",
    "常见病概览",
    "健康教育",
    "就医警示",
)


def _normalize_text(value: object) -> str:
    return re.sub(r"\s+", "", str(value or "").casefold())


def _is_generic_title_fragment(term: str) -> bool:
    return any(term in phrase for phrase in GENERIC_TITLE_PHRASES)


def _extract_terms(query: str) -> list[str]:
    normalized_query = _normalize_text(query)
    for phrase in GENERIC_TITLE_PHRASES:
        normalized_query = normalized_query.replace(phrase, "")
    terms: set[str] = set()
    for token in re.findall(
        r"[a-z0-9][a-z0-9_+.-]*|[\u4e00-\u9fff]+",
        normalized_query,
    ):
        if token in RERANK_STOP_WORDS or _is_generic_title_fragment(token):
            continue
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            if len(token) >= 2 and not _is_generic_title_fragment(token):
                terms.add(token)
            for size in range(2, min(6, len(token)) + 1):
                for start in range(0, len(token) - size + 1):
                    term = token[start : start + size]
                    if (
                        term not in RERANK_STOP_WORDS
                        and not _is_generic_title_fragment(term)
                    ):
                        terms.add(term)
        elif len(token) >= 2 or token.isdigit():
            terms.add(token)
    return sorted(terms, key=lambda term: (-len(term), term))


def _bounded_score(value: object) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _overlap_score(terms: list[str], text: str) -> float:
    useful_terms = [term for term in terms if len(term) >= 2]
    if not useful_terms:
        return 0.0
    matched_weight = sum(len(term) for term in useful_terms if term in text)
    total_weight = sum(len(term) for term in useful_terms)
    return min(1.0, matched_weight / max(1, total_weight))


def _title_score(terms: list[str], title: str) -> float:
    if not title:
        return 0.0
    title_terms = [term for term in terms if len(term) >= 2 and term in title]
    if not title_terms:
        return 0.0
    longest_match = max(len(term) for term in title_terms)
    return min(1.0, 0.55 + longest_match / max(10, len(title) * 2))


def rerank_matches(
    query: str,
    matches: list[tuple[object, float]],
) -> list[tuple[Document, float]]:
    """Re-score candidates and preserve the existing ``(Document, score)`` API."""
    terms = _extract_terms(query)
    reranked: list[tuple[Document, float]] = []

    for document, raw_score in matches:
        if not isinstance(document, Document):
            continue
        original_score = _bounded_score(raw_score)
        metadata = dict(document.metadata)
        text = _normalize_text(document.page_content)
        title = _normalize_text(metadata.get("name", ""))

        if terms:
            text_score = _overlap_score(terms, text)
            title_score = _title_score(terms, title)
            lexical_score = (
                TEXT_MATCH_WEIGHT * text_score
                + TITLE_MATCH_WEIGHT * title_score
            ) / (TEXT_MATCH_WEIGHT + TITLE_MATCH_WEIGHT)
            final_score = (
                ORIGINAL_SCORE_WEIGHT * original_score
                + (1 - ORIGINAL_SCORE_WEIGHT) * lexical_score
            )
        else:
            text_score = 0.0
            title_score = 0.0
            lexical_score = 0.0
            final_score = original_score

        metadata.update(
            {
                "rerank_applied": True,
                "initial_score": round(original_score, 4),
                "rerank_text_score": round(text_score, 4),
                "rerank_title_score": round(title_score, 4),
                "rerank_lexical_score": round(lexical_score, 4),
                "rerank_score": round(final_score, 4),
            }
        )
        final_score = round(final_score, 4)
        reranked.append(
            (
                Document(page_content=document.page_content, metadata=metadata),
                final_score,
            )
        )

    return sorted(reranked, key=lambda item: item[1], reverse=True)
