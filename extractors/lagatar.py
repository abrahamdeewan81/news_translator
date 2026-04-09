import requests
from bs4 import BeautifulSoup

def extract_lagatar(url, debug):

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/"
    }

    response = requests.get(url, headers=headers, timeout=10)
    debug.append(f"HTTP status: {response.status_code}")

    html = response.text
    debug.append(f"HTML downloaded. Size: {len(html)}")

    soup = BeautifulSoup(html, "html.parser")
    debug.append("HTML parsed")

    article = soup.select_one("#articleContent")

    text_list = []

    if article:

        paragraphs = article.select(
            "div.article-visible p, div.article-blurred p"
        )

        debug.append(f"Paragraphs found: {len(paragraphs)}")

        for p in paragraphs:

            text = p.get_text(strip=True)

            if text and text != "\xa0":
                text_list.append(text)
                debug.append(f"Added text: {text}")

    else:
        debug.append("ERROR: articleContent not found")

    article_text = "\n\n".join(text_list)

    debug.append(f"Total extracted blocks: {len(text_list)}")

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text
