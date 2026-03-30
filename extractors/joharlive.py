from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def extract_joharlive(url, debug):

    debug.append("Starting Playwright browser")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        debug.append(f"Opening URL: {url}")

        page.goto(url, timeout=60000)

        page.wait_for_selector("div.post-content")

        debug.append("post-content selector loaded")

        html = page.content()

        debug.append(f"HTML downloaded. Size: {len(html)}")

        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    container = soup.select_one("div.post-content")

    if not container:
        debug.append("ERROR: post-content container not found")
        return ""

    debug.append("post-content container found")

    # remove ads and code blocks
    for ad in container.select(".code-block, .a-wrap, .johar-entity-placement"):
        ad.decompose()

    debug.append("Advertisement blocks removed")

    text_list = []

    for element in container.children:

        if element.name is None:
            continue

        debug.append(f"Inspecting element: {element.name}")

        # paragraph
        if element.name == "p":

            text = element.get_text(" ", strip=True)

            # skip "Also Read"
            if text.lower().startswith("also read"):
                debug.append("Skipping 'Also Read' block")
                continue

            if text:
                text_list.append(text)

        # section heading
        elif element.name in ["h2", "h3", "h4"]:

            heading = element.get_text(" ", strip=True)

            if heading:
                text_list.append(heading)

    debug.append(f"Total extracted blocks: {len(text_list)}")

    article_text = "\n\n".join(text_list)

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text