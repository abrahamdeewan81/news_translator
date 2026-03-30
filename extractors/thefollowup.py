from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_thefollowup(url, debug):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)
        debug.append("URL opened")

        # wait until article body loads
        page.wait_for_selector("div.contents")
        debug.append("div.contents selector loaded")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
       
        html = page.content()

        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    debug.append("HTML parsed")

    article = soup.select_one("div.contents")
    debug.append("div.contents selector loaded")

    # remove images
    for img in article.find_all("img"):
        debug.append(f"Removing image: {img}")
        img.decompose()

    text_list = []

    paragraphs = article.find_all("p")
    debug.append(f"Found {len(paragraphs)} paragraphs")

    for p in paragraphs:

        text = p.get_text(" ", strip=True)
        debug.append(f"Paragraph: {text}")

        if text:
            text_list.append(text)
            debug.append(f"Added text: {text}")

    debug.append(f"Total extracted blocks: {len(text_list)}")
    article_text = "\n\n".join(text_list)

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text