from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def extract_thenewspost(url, debug):

    debug.append("Starting Playwright browser")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        debug.append(f"Opening URL: {url}")

        page.goto(url, timeout=60000)

        page.wait_for_selector("#full-article")

        debug.append("full-article selector loaded")

        html = page.content()

        debug.append(f"HTML downloaded. Size: {len(html)}")

        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    container = soup.select_one("#full-article")

    if not container:
        debug.append("ERROR: full-article container not found")
        return ""

    debug.append("full-article container found")

    text_list = []

    paragraphs = container.find_all("p")

    debug.append(f"Total paragraphs found: {len(paragraphs)}")

    for p in paragraphs:

        text = p.get_text(" ", strip=True)

        debug.append(f"Paragraph text length: {len(text)}")

        # skip reporter credit
        if text.lower().startswith("रिपोर्ट"):
            debug.append("Skipping reporter credit line")
            continue

        if text:
            text_list.append(text)

    debug.append(f"Total extracted paragraphs: {len(text_list)}")

    article_text = "\n\n".join(text_list)

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text