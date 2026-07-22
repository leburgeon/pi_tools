""" Translation script for translating text between languages. """
import argparse

VALID_LANGUAGE_TAGS = [
    "ar-SA", "bn-BD", "bn-IN", "cs-CZ", "da-DK", "de-AT", "de-CH", "de-DE",
    "el-GR", "en-AU", "en-CA", "en-GB", "en-IE", "en-IN", "en-NZ", "en-US",
    "en-ZA", "es-AR", "es-CL", "es-CO", "es-ES", "es-MX", "es-US", "fi-FI",
    "fr-BE", "fr-CA", "fr-CH", "fr-FR", "he-IL", "hi-IN", "hu-HU", "id-ID",
    "it-CH", "it-IT", "ja-JP", "ko-KR", "nl-BE", "nl-NL", "no-NO", "pl-PL",
    "pt-BR", "pt-PT", "ro-RO", "ru-RU", "sk-SK", "sv-SE", "ta-IN", "ta-LK",
    "th-TH", "tr-TR", "zh-CN", "zh-HK", "zh-TW"
]


def validate_language_tag(tag: str) -> str:
    """
    Validates if the provided language tag is in the list of valid language tags.

    Args:
        tag (str): The language tag to validate.

    Raises ValueError: If the language tag is not valid.

    Returns:
        str: The validated language tag.
   """
    if tag not in VALID_LANGUAGE_TAGS:
        raise ValueError(f"Invalid language tag: {tag}")
    return tag


def generate_argument_parser():
    """
    Generates an argument parser for the translation script.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description='Translate text')
    parser.add_argument(
        'source_lang', help='Source language code (e.g., en, es, fr)', type=validate_language_tag)
    parser.add_argument(
        'target_lang', help='Target language code (e.g., en, es, fr)', type=validate_language_tag)
    parser.add_argument('text', help='Text to translate', type=str)

    return parser


def translate_text(source_lang: str, target_lang: str, text: str) -> str:
    """
    Translates the given text from the source language to the target language.

    Args:
        source_lang (str): The source language code.
        target_lang (str): The target language code.
        text (str): The text to translate.

    Returns:
        str: The translated text.
    """
    # Placeholder for translation logic. In a real implementation, you would call a translation API or library here.
    # For demonstration purposes, we'll just return a formatted string.
    return f"Translated '{text}' from {source_lang} to {target_lang}"


if __name__ == "__main__":
    parser = generate_argument_parser()
    args = parser.parse_args()

    source_lang = args.source_lang
    target_lang = args.target_lang
    text = args.text

    # Here you would implement the translation logic using the provided arguments.
    # For example, you might call a translation API or use a local translation library.
    # This is a placeholder for demonstration purposes.
    translated_text = translate_text(source_lang, target_lang, text)
    print(translated_text)
