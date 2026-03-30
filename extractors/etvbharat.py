import requests
from bs4 import BeautifulSoup


def extract_etvbharat(url, debug):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    debug.append("HTML parsed")

    container = soup.find("div", id="newsroom-bodyText")
    debug.append("div.newsroom-bodyText selector loaded")

    if not container:
        debug.append("ERROR: newsroom-bodyText container not found")
        return ""

    paragraphs = container.find_all("p")

    text_list = []

    for p in paragraphs:

        text = p.get_text(strip=True)
        debug.append(f"Paragraph: {text}")

        if text:
            text_list.append(text)
            debug.append(f"Added text: {text}")

    debug.append(f"Total extracted blocks: {len(text_list)}")
    article_text = "\n\n".join(text_list)

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text