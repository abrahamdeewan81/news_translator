from deep_translator import GoogleTranslator

def translate_to_english(text):

    if not text:
        return ""

    try:
        translated = GoogleTranslator(
            source='auto',
            target='en'
        ).translate(text)

        return translated

    except Exception:
        return "⚠ Translation failed. Some error occurred during translation."