import requests
import trafilatura
from goose3 import Goose
from readability import Document
from bs4 import BeautifulSoup


MIN_TEXT_LENGTH = 200   # adjust if needed


def is_valid_text(text, debug, source):
    if not text:
        debug.append(f"{source}: No text extracted")
        return False

    length = len(text.strip())

    debug.append(f"{source}: Extracted length = {length}")

    if length < MIN_TEXT_LENGTH:
        debug.append(f"{source}: Text too short, rejecting")
        return False

    return True


def extract_universal(url, debug):

    debug.append("Using advanced universal extractor")

    html = ""

    # Step 0: Download HTML once
    try:
        debug.append("Downloading HTML via requests")

        headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

        response = requests.get(url, headers=headers, timeout=30)   
        html = response.text

        debug.append(f"Downloaded HTML size: {len(html)}")

    except Exception as e:
        debug.append(f"ERROR downloading page: {str(e)}")
        return ""

    # -------------------------
    # 1. TRAFILATURA
    # -------------------------
    try:
        debug.append("Trying Trafilatura")

        text = trafilatura.extract(html)

        if is_valid_text(text, debug, "Trafilatura"):
            debug.append("SUCCESS: Trafilatura used")
            return text

    except Exception as e:
        debug.append(f"Trafilatura error: {str(e)}")

    # -------------------------
    # 2. GOOSE3
    # -------------------------
    try:
        debug.append("Trying Goose3")

        g = Goose()
        article = g.extract(raw_html=html)

        text = article.cleaned_text

        if is_valid_text(text, debug, "Goose3"):
            debug.append("SUCCESS: Goose3 used")
            return text

    except Exception as e:
        debug.append(f"Goose3 error: {str(e)}")

    # -------------------------
    # 3. READABILITY
    # -------------------------
    try:
        debug.append("Trying Readability")

        doc = Document(html)

        summary_html = doc.summary()

        soup = BeautifulSoup(summary_html, "html.parser")

        text = soup.get_text("\n", strip=True)

        if is_valid_text(text, debug, "Readability"):
            debug.append("SUCCESS: Readability used")
            return text

    except Exception as e:
        debug.append(f"Readability error: {str(e)}")

    # -------------------------
    # FAIL SAFE
    # -------------------------
    debug.append("All extractors failed")

    return ""