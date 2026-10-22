import requests
from bs4 import BeautifulSoup


def extract_thefollowup(url, debug):
    debug.append("Using thefollowup extractor")

    # Fast path: direct requests + BeautifulSoup (works seamlessly on Render)
    try:
        debug.append("Attempting extraction via requests")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            article = soup.select_one("div.contents")
            if article:
                for img in article.find_all("img"):
                    img.decompose()
                paragraphs = [
                    p.get_text(" ", strip=True)
                    for p in article.find_all("p")
                    if p.get_text(strip=True)
                ]
                if paragraphs:
                    debug.append(f"Direct requests extracted {len(paragraphs)} paragraphs")
                    return "\n\n".join(paragraphs)
    except Exception as e:
        debug.append(f"Direct requests extraction failed: {str(e)}")

    # Fallback to Playwright if available in the environment
    try:
        from playwright.sync_api import sync_playwright

        debug.append("Attempting extraction via Playwright fallback")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_selector("div.contents", timeout=10000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        article = soup.select_one("div.contents")
        if article:
            for img in article.find_all("img"):
                img.decompose()
            paragraphs = [
                p.get_text(" ", strip=True)
                for p in article.find_all("p")
                if p.get_text(strip=True)
            ]
            if paragraphs:
                return "\n\n".join(paragraphs)
    except Exception as e:
        debug.append(f"Playwright extraction failed: {str(e)}")

    return ""