import re
import logging
from dataclasses import dataclass

log = logging.getLogger(__name__)

CHUNK_SIZE = 512       # target tokens per chunk
CHUNK_OVERLAP = 64     # overlap tokens between chunks
CHARS_PER_TOKEN = 4    # rough estimate: 1 token ≈ 4 chars

# Separators tried in order (most → least structural)
SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]


@dataclass
class Chunk:
    chunk_index: int
    text: str
    start_char: int
    end_char: int
    page_number: int | None
    token_estimate: int


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def _split_text(text: str, size: int, overlap: int) -> list[tuple[str, int, int]]:
    """
    Recursive character splitter.
    Returns list of (chunk_text, start_char, end_char).
    """
    size_chars = size * CHARS_PER_TOKEN
    overlap_chars = overlap * CHARS_PER_TOKEN

    if len(text) <= size_chars:
        return [(text, 0, len(text))]

    results: list[tuple[str, int, int]] = []

    # Try each separator in priority order
    for sep in SEPARATORS:
        if sep and sep not in text:
            continue

        splits = text.split(sep) if sep else list(text)
        chunks: list[str] = []
        cur = ""

        for part in splits:
            candidate = (cur + sep + part).lstrip(sep) if cur else part
            if _estimate_tokens(candidate) <= size:
                cur = candidate
            else:
                if cur:
                    chunks.append(cur)
                cur = part

        if cur:
            chunks.append(cur)

        # Build offset-tracked results with overlap
        pos = 0
        for i, chunk in enumerate(chunks):
            start = text.find(chunk, pos)
            if start == -1:
                start = pos
            end = start + len(chunk)

            results.append((chunk, start, end))

            # Advance pos but allow overlap
            pos = max(pos + 1, end - overlap_chars)

        if results:
            return results

    # Fallback: hard split by character
    pos = 0
    while pos < len(text):
        end = min(pos + size_chars, len(text))
        results.append((text[pos:end], pos, end))
        pos = end - overlap_chars if end < len(text) else end

    return results


def _extract_page_number(text: str) -> int | None:
    """Extract [Page N] marker injected by the PDF parser."""
    m = re.search(r"\[Page (\d+)\]", text)
    return int(m.group(1)) if m else None


def chunk_document(extracted_text: str) -> list[Chunk]:
    """
    Main entry point. Returns a list of Chunk dataclasses.
    Handles page-aware splitting for PDFs (text contains [Page N] markers).
    """
    if not extracted_text or not extracted_text.strip():
        return []

    # Split on page boundaries first if markers exist
    has_pages = bool(re.search(r"\[Page \d+\]", extracted_text))

    if has_pages:
        page_blocks = re.split(r"(?=\[Page \d+\])", extracted_text)
        raw_splits: list[tuple[str, int, int, int | None]] = []
        global_offset = 0

        for block in page_blocks:
            if not block.strip():
                global_offset += len(block)
                continue
            page_num = _extract_page_number(block)
            sub = _split_text(block, CHUNK_SIZE, CHUNK_OVERLAP)
            for text, local_start, local_end in sub:
                if text.strip():
                    raw_splits.append((
                        text,
                        global_offset + local_start,
                        global_offset + local_end,
                        page_num,
                    ))
            global_offset += len(block)
    else:
        sub = _split_text(extracted_text, CHUNK_SIZE, CHUNK_OVERLAP)
        raw_splits = [(t, s, e, None) for t, s, e in sub if t.strip()]

    chunks = []
    for idx, (text, start, end, page) in enumerate(raw_splits):
        chunks.append(Chunk(
            chunk_index=idx,
            text=text.strip(),
            start_char=start,
            end_char=end,
            page_number=page,
            token_estimate=_estimate_tokens(text),
        ))

    log.info("Chunked into %d chunks (page-aware=%s)", len(chunks), has_pages)
    return chunks
