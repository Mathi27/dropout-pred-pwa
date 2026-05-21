SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu",
}

LANGUAGE_ALIASES = {
    "tamil": "ta",
    "hindi": "hi",
    "telugu": "te",
    "english": "en",
}


def resolve_language(preferred: str | None, requested: str | None = None) -> str:
    if requested:
        key = requested.lower().strip()
        key = LANGUAGE_ALIASES.get(key, key)
        if key in SUPPORTED_LANGUAGES:
            return key
    if preferred:
        key = preferred.lower().strip()
        key = LANGUAGE_ALIASES.get(key, key)
        if key in SUPPORTED_LANGUAGES:
            return key
    return "en"
