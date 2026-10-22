from flask import Flask, render_template, request
from urllib.parse import urlparse

from extractors.lagatar import extract_lagatar
from extractors.livehindustan import extract_livehindustan
from extractors.thefollowup import extract_thefollowup
from extractors.etvbharat import extract_etvbharat
from extractors.newsdekho import extract_newsdekho
from extractors.jagran import extract_jagran
from extractors.joharlive import extract_joharlive
from extractors.thenewspost import extract_thenewspost
from extractors.hpbl import extract_hpbl
from extractors.universal import extract_universal

from translators.translate import translate_to_english

app = Flask(__name__)


def get_extractor(url, debug_logs):

    domain = urlparse(url).netloc
    debug_logs.append(f"Detected domain: {domain}")
    if "thefollowup.in" in domain:
        debug_logs.append("Using extractor: thefollowup")
        return extract_thefollowup

    if "lagatar.in" in domain:
        debug_logs.append("Using extractor: lagatar")
        return extract_lagatar
        
    # fallback extractor
    debug_logs.append("Using universal extractor")
    return extract_universal


@app.route("/", methods=["GET", "POST"])
def index():

    article_text = ""
    translated_text = ""
    debug_logs = []
    url = ""

    # Support both POST form submission and GET query parameter (e.g. ?url=https://...)
    if request.method == "POST":
        url = (request.form.get("url") or "").strip()
    else:
        url = (request.args.get("url") or "").strip()

    if url:
        debug_logs.append(f"URL received: {url}")
        extractor = get_extractor(url, debug_logs)

        if extractor:
            try:
                debug_logs.append("Starting extraction")
                article_text = extractor(url, debug_logs)

                # Fallback to universal extractor if specific extractor returned empty
                if not article_text and extractor != extract_universal:
                    debug_logs.append("Specific extractor returned empty text. Trying universal extractor...")
                    article_text = extract_universal(url, debug_logs)

                if article_text:
                    debug_logs.append(f"Extraction successful. Characters: {len(article_text)}")

                    try:
                        translated_text = translate_to_english(article_text)
                        debug_logs.append("Translation successful")

                    except Exception as e:
                        translated_text = "⚠ Translation failed."
                        debug_logs.append(f"Translation error: {str(e)}")

                else:
                    translated_text = ""
                    debug_logs.append("Extractor returned empty text")

            except Exception as e:
                article_text = ""
                translated_text = ""
                debug_logs.append(f"Extractor crashed: {str(e)}")

        else:
            article_text = "Website not supported yet."
            debug_logs.append("Unsupported website")

    # If requested as JSON via query param or header, return structured JSON
    if request.args.get("format") == "json" or request.headers.get("Accept") == "application/json":
        return {
            "url": url,
            "article_text": article_text,
            "translated_text": translated_text,
            "debug_logs": debug_logs,
        }

    return render_template(
        "index.html",
        url=url,
        article_text=article_text,
        translated_text=translated_text,
        debug_logs=debug_logs
    )


if __name__ == "__main__":
    app.run(debug=True)