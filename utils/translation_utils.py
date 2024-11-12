import argostranslate.package
import argostranslate.translate

def translate_text(text, from_lang, to_lang):
    return argostranslate.translate.translate(text, from_lang, to_lang)
