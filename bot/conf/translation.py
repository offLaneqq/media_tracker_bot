import deepl
import os

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
if DEEPL_API_KEY is None:
    raise ValueError("DEEPL_API_KEY environment variable is not set")
translator = deepl.Translator(DEEPL_API_KEY)

async def translate_to_english(text: str) -> str:
    result = translator.translate_text(text, source_lang="UK", target_lang="EN-US")
    if isinstance(result, list):
        return result[0].text
    return result.text