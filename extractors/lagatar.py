import requests
from bs4 import BeautifulSoup

def extract_lagatar(url, debug):

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

    response = requests.get(url, headers=headers, timeout=15)
    debug.append(f"HTTP status: {response.status_code}")

    html = response.text
    debug.append(f"HTML downloaded. Size: {len(html)}")

    soup = BeautifulSoup(html, "html.parser")
    debug.append("HTML parsed")

    article = soup.select_one("#articleContent") or soup.select_one(".div-article-content")

    text_list = []

    if article:

        paragraphs = article.find_all("p")
        debug.append(f"Paragraphs found: {len(paragraphs)}")

        for p in paragraphs:
            text = p.get_text(" ", strip=True)

            if text and text != "\xa0":
                text_list.append(text)

    else:
        debug.append("ERROR: article container not found")

    article_text = "\n\n".join(text_list)

    debug.append(f"Total extracted blocks: {len(text_list)}")

    return article_text
