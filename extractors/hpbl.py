from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def extract_hpbl(url, debug):

    debug.append("Starting Playwright browser")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        debug.append(f"Opening URL: {url}")

        page.goto(url, timeout=60000)

        page.wait_for_selector("div.entry-content")

        debug.append("entry-content selector loaded")

        html = page.content()

        debug.append(f"HTML downloaded. Size: {len(html)}")

        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    container = soup.select_one("div.entry-content")

    if not container:
        debug.append("ERROR: entry-content container not found")
        return ""

    debug.append("entry-content container found")

    # remove advertisement blocks
    for ad in container.select(".stream-item"):
        ad.decompose()

    debug.append("Ad blocks removed")

    # remove bottom tags section
    bottom_meta = container.select_one(".post-bottom-meta")
    if bottom_meta:
        bottom_meta.decompose()
        debug.append("Post bottom meta removed")

    text_list = []

    for element in container.children:

        if element.name is None:
            continue

        debug.append(f"Inspecting element: {element.name}")

        if element.name in ["p", "h2", "h3", "h4"]:

            text = element.get_text(" ", strip=True)

            if text:
                text_list.append(text)

    debug.append(f"Total extracted blocks: {len(text_list)}")

    article_text = "\n\n".join(text_list)

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text