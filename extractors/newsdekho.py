from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def extract_newsdekho(url, debug):

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

    first_ul = container.find("ul")

    if not first_ul:
        debug.append("ERROR: First UL element not found")
        return ""

    debug.append("First UL element located")

    text_list = []

    for element in first_ul.find_next_siblings():

        debug.append(f"Inspecting element: {element.name}")

        # Normal text blocks
        if element.name in ["p", "h2", "h4", "h5", "blockquote"]:

            text = element.get_text(" ", strip=True)

            if text:
                text_list.append(text)

        # Handle UL lists
        elif element.name == "ul":

            debug.append("Processing UL list")

            for li in element.find_all("li"):

                li_text = li.get_text(" ", strip=True)

                if li_text:
                    text_list.append(li_text)

    debug.append(f"Total extracted blocks: {len(text_list)}")

    article_text = "\n\n".join(text_list)

    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text