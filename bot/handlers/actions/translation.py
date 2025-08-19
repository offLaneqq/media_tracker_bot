import deepl
import os
from typing import Optional

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
if DEEPL_API_KEY is None:
    raise ValueError("DEEPL_API_KEY environment variable is not set")
translator = deepl.Translator(DEEPL_API_KEY)


def translate(text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
    if source_lang:
        result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
    else:
        result = translator.translate_text(text, target_lang=target_lang)
    if isinstance(result, list):
        return result[0].text
    return result.text