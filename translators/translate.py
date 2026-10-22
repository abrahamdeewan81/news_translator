
import requests
from deep_translator import GoogleTranslator

# Google Translate endpoint clients that do not hit the 429 rate limit
GOOGLE_CLIENTS = ["dict-chrome-ex", "at", "it"]
GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
}


def split_text(text, max_chars=3000):
    """Split text into chunks without exceeding the character limit,
    preserving paragraph and sentence boundaries."""
    chunks = []
    remaining = text.strip()

    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break

        # Prefer splitting at paragraph boundary
        split_at = remaining.rfind("\n\n", 0, max_chars)

        # Fall back to single newline
        if split_at < max_chars // 2:
            split_at = remaining.rfind("\n", 0, max_chars)

        # Fall back to sentence boundary
        if split_at < max_chars // 2:
            split_at = remaining.rfind(". ", 0, max_chars)
            if split_at > 0:
                split_at += 1

        # Fall back to word boundary
        if split_at < max_chars // 2:
            split_at = remaining.rfind(" ", 0, max_chars)

        if split_at <= 0:
            split_at = max_chars

        chunk = remaining[:split_at].strip()
        if chunk:
            chunks.append(chunk)

        remaining = remaining[split_at:].strip()

    return chunks


def _translate_chunk_google_api(chunk, source="auto", target="en"):
    """Translate a single chunk using Google's translate_a/single endpoint."""
    last_exc = None
    for client in GOOGLE_CLIENTS:
        try:
            data = {
                "client": client,
                "sl": source,
                "tl": target,
                "dt": "t",
                "q": chunk,
            }
            response = requests.post(
                GOOGLE_TRANSLATE_URL,
                data=data,
                headers=HEADERS,
                timeout=15,
            )
            if response.status_code == 200:
                res_json = response.json()
                if res_json and len(res_json) > 0 and res_json[0]:
                    translated_parts = [
                        seg[0] for seg in res_json[0] if seg and seg[0]
                    ]
                    translated = "".join(translated_parts).strip()
                    if translated:
                        return translated
        except Exception as exc:
            last_exc = exc
            continue

    raise RuntimeError(
        f"Google Translate API request failed: {last_exc}"
    ) from last_exc


def _translate_chunk_deep_translator(chunk, source="auto", target="en"):
    """Fallback translator using deep_translator."""
    translator = GoogleTranslator(source=source, target=target)
    result = translator.translate(chunk)
    if not result:
        raise RuntimeError("deep_translator returned empty text.")
    return result


def translate_to_english(text):
    """Translate short or long news articles into English."""
    if not text or not text.strip():
        return ""

    chunks = split_text(text)
    translated_chunks = []

    for index, chunk in enumerate(chunks, start=1):
        translated_chunk = None

        # 1. Primary: Direct Google Translate RPC (reliable, avoids 429 on cloud servers)
        try:
            translated_chunk = _translate_chunk_google_api(chunk, source="auto", target="en")
        except Exception as api_err:
            # 2. Secondary fallback: deep_translator
            try:
                translated_chunk = _translate_chunk_deep_translator(chunk, source="auto", target="en")
            except Exception as dt_err:
                raise RuntimeError(
                    f"Translation failed at chunk {index}/{len(chunks)}. "
                    f"Primary error: {api_err} | Fallback error: {dt_err}"
                ) from dt_err

        if translated_chunk:
            translated_chunks.append(translated_chunk)

    return "\n\n".join(translated_chunks)

