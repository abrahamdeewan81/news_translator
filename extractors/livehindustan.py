from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_livehindustan(url, debug):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)

        # wait until article body loads
        page.wait_for_selector("#story-content")
        debug.append("entry-content selector loaded")
        
        html = page.content()
        debug.append(f"HTML downloaded. Size: {len(html)}")

        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    article = soup.select_one("#story-content")
    debug.append("entry-content selector loaded")

    # remove advertisement blocks
    for ad in article.select(".story-ads-prlads"):
        debug.append(f"Removing ad block: {ad}")
        ad.decompose()

    text_list = []

    paragraphs = article.find_all("p")
    debug.append(f"Found {len(paragraphs)} paragraphs")

    for p in paragraphs:
        text = p.get_text(strip=True)
        debug.append(f"Paragraph: {text}")  


        if text:
            text_list.append(text)  

    debug.append(f"Total extracted blocks: {len(text_list)}")
    article_text = "\n\n".join(text_list)


    if not article_text:
        debug.append("WARNING: Extraction produced empty text")

    return article_text