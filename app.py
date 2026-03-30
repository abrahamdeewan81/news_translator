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

    if "lagatar.in" in domain:
        debug_logs.append("Using extractor: lagatar")
        return extract_lagatar

    if "livehindustan.com" in domain:
        debug_logs.append("Using extractor: livehindustan")
        return extract_livehindustan

    if "thefollowup.in" in domain:
        debug_logs.append("Using extractor: thefollowup")
        return extract_thefollowup
    
    if "jagran.com" in domain:
        debug_logs.append("Using extractor: jagran")
        return extract_jagran
    
    if "thenewspost.in" in domain:
        debug_logs.append("Using extractor: thenewspost")
        return extract_thenewspost
    
    if "etvbharat.com" in domain:
        debug_logs.append("Using extractor: etvbharat")
        return extract_etvbharat
    
    if "newsdekho.co.in" in domain:
        debug_logs.append("Using extractor: newsdekho")
        return extract_newsdekho
    
    if "joharlive.com" in domain:
        debug_logs.append("Using extractor: joharlive")
        return extract_joharlive
    
    if "hpbl.co.in" in domain:
        debug_logs.append("Using extractor: hpbl")
        return extract_hpbl

    # fallback extractor
    debug_logs.append("No domain matched. Using universal extractor.")
    return extract_universal


@app.route("/", methods=["GET", "POST"])
def index():

    article_text = ""
    translated_text = ""
    debug_logs = []

    if request.method == "POST":

        url = request.form.get("url")
        debug_logs.append(f"URL received: {url}")

        extractor = get_extractor(url, debug_logs)

        if extractor:

            try:

                debug_logs.append("Starting extraction")

                article_text = extractor(url, debug_logs)

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

    return render_template(
        "index.html",
        article_text=article_text,
        translated_text=translated_text,
        debug_logs=debug_logs
    )


if __name__ == "__main__":
    app.run(debug=True)