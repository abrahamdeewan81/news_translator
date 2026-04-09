from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_lagatar(url, debug):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)

        # Wait for the main article container
        page.wait_for_selector("#articleContent")
        debug.append("articleContent selector loaded")

        html = page.content()
        debug.append(f"HTML downloaded. Size: {len(html)}")

        browser.close()

    # Parse HTML
    soup = BeautifulSoup(html, "html.parser")
    debug.append("HTML parsed")

    # Locate article container
    article = soup.select_one("#articleContent")
    debug.append("articleContent selector located")

    text_list = []

    if article:
        paragraphs = article.select("div.article-visible p, div.article-blurred p")
        debug.append(f"Total paragraph tags found: {len(paragraphs)}")

        for p in paragraphs:
            debug.append(f"Found paragraph: {p}")

            text = p.get_text(strip=True)

            if text and text != "\xa0":
                text_list.append(text)
                debug.append(f"Added text: {text}")

    else:
        debug.append("ERROR: articleContent not found")

    debug.append(f"Total extracted blocks: {len(text_list)}")

    article_text = "\n\n".join(text_list)

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text
