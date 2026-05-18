import re
from collections import Counter

import httpx

from api.models.schemas import AnalysisRequest, IngestOutput

STOP_WORDS = {
    "about", "after", "again", "against", "also", "because", "before",
    "being", "between", "could", "during", "expected", "from", "have",
    "into", "more", "other", "over", "said", "should", "than", "that",
    "their", "there", "these", "this", "those", "through", "under",
    "while", "with", "would", "your",
}


def _fetch_url(url: str) -> str:
    try:
        response = httpx.get(url, timeout=8, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ValueError(f"Could not fetch URL: {exc}") from exc

    text = re.sub(r"<(script|style).*?</\1>", " ", response.text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _clean_content(request: AnalysisRequest) -> str:
    content = request.content.strip()
    if request.content_type == "url":
        return _fetch_url(content)
    return re.sub(r"\s+", " ", content)


def _sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]


def _keywords(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text.lower())
    counts = Counter(word for word in words if word not in STOP_WORDS)
    return [word.title() for word, _ in counts.most_common(8)]


def _entities(text: str) -> list[str]:
    matches = re.findall(r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,}))*\b", text)
    entities = []
    for match in matches:
        cleaned = match.strip()
        if len(cleaned) > 2 and cleaned not in entities:
            entities.append(cleaned)
    return entities[:8]


def _summary(text: str) -> str:
    sentences = _sentences(text)
    if not sentences:
        return "No readable content was found."

    scored = []
    keywords = {keyword.lower() for keyword in _keywords(text)[:5]}
    for sentence in sentences[:12]:
        lower = sentence.lower()
        score = sum(1 for keyword in keywords if keyword.lower() in lower)
        score += len(re.findall(r"\b\d+(?:\.\d+)?%?\b", sentence))
        scored.append((score, sentence))

    top = [sentence for _, sentence in sorted(scored, reverse=True)[:2]]
    summary = " ".join(reversed(top)) if len(top) > 1 else top[0]
    return summary[:450]


def run_ingest_agent(request: AnalysisRequest) -> IngestOutput:
    text = _clean_content(request)
    keywords = _keywords(text)
    entities = _entities(text)
    combined = entities + [keyword for keyword in keywords if keyword not in entities]

    return IngestOutput(
        summary=_summary(text),
        entities=combined[:8] or ["Market", "Consumer", "Income"],
    )
