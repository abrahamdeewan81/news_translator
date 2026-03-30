from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_jagran(url, debug):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)

        # wait for article body
        page.wait_for_selector("div.ArticleBody")
        debug.append("div.ArticleBody selector loaded")

        html = page.content()
        debug.append(f"HTML downloaded. Size: {len(html)}")

        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    debug.append("HTML parsed")

    article = soup.select_one("div.ArticleBody")
    debug.append("div.ArticleBody selector loaded")

    # remove images
    for img in article.find_all("img"):
        debug.append(f"Removing image: {img}")
        img.decompose()

    text_list = []

    # extract paragraphs and headings
    for tag in article.find_all(["p","h2"]):
        debug.append(f"Found tag: {tag}")

        text = tag.get_text(" ", strip=True)
        debug.append(f"Paragraph: {text}")

        if text:
            text_list.append(text)
            debug.append(f"Added text: {text}")

    debug.append(f"Total extracted blocks: {len(text_list)}")
    article_text = "\n\n".join(text_list)

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text