from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_lagatar(url, debug):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)
        page.wait_for_selector("div.div-article-content")
        debug.append("div-article-content selector loaded")

        html = page.content()
        debug.append(f"HTML downloaded. Size: {len(html)}")

        browser.close()

    soup = BeautifulSoup(html,"html.parser")
    debug.append("HTML parsed")

    article = soup.select_one("div.div-article-content")
    debug.append("div-article-content selector loaded")

    text_list = []

    for p in article.find_all("p"):
        debug.append(f"Found paragraph: {p}")

        text = p.get_text(strip=True)

        if text and text != "\xa0":
            text_list.append(text)
            debug.append(f"Added text: {text}")

    debug.append(f"Total extracted blocks: {len(text_list)}")
    article_text = "\n\n".join(text_list)

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text