import re
from typing import Tuple

# Unicode script ranges
TELUGU_RANGE = re.compile(r'[\u0C00-\u0C7F]')
DEVANAGARI_RANGE = re.compile(r'[\u0900-\u097F]')
TAMIL_RANGE = re.compile(r'[\u0B80-\u0BFF]')
KANNADA_RANGE = re.compile(r'[\u0C80-\u0CFF]')
MALAYALAM_RANGE = re.compile(r'[\u0D00-\u0D7F]')

# Romanized regional markers (chosen to avoid colliding with common English words)
TELUGU_MARKERS = {
    "juttu", "aaharam", "tinali", "cheppandi", "enti", "kavalenu", "kavalsina",
    "raktham", "thotakura", "palakura", "ragulu", "dhanyavadamulu", "dhanyavadalu",
    "bhojanam", "baruvu", "thaggali", "peragali", "balam", "jeernam", "yem",
    "manchidi", "pettandi", "cheppu", "kooda", "lavu", "sannaga", "guddu",
    "unnavu", "unnaru", "chestunnav", "chestunnavu", "naku", "naaku", "bagunnara"
}

HINDI_MARKERS = {
    "khana", "chahiye", "batao", "kaise", "kya", "sehat", "baal", "khoon",
    "khao", "namaste", "dawa", "vajan", "badhana", "ghatana", "bataiye",
    "motapa", "patla", "aahar", "bhojan", "shakti", "doodh", "mujhe", "humko",
    "shukriya", "dhanyawad", "kaisa"
}

TAMIL_MARKERS = {
    "sappadu", "enna", "sollunga", "udambu", "koondhal", "raththam", "vanakkam",
    "edai", "kuraikka", "athikarikka", "unavu", "nandri", "kudikka", "maruthuvar",
    "valarppu", "eppadi", "irukkeenga", "panreenga"
}

KANNADA_MARKERS = {
    "oota", "thinnabeku", "aahara", "heli", "yenu", "kannada", "beku", "deha",
    "koodalu", "thooka", "iliyalu", "hechhisalu", "namaskara", "dhanyavada",
    "shakthi", "balavada", "hegiddira", "maadthiddira"
}


class LanguageDetectionService:
    @staticmethod
    def detect_language(text: str, fallback_lang: str = "en") -> Tuple[str, float, bool]:
        """
        Detects primary language of user query.
        Returns: (language_code, confidence, is_mixed_query)
        """
        if not text or not text.strip():
            return (fallback_lang or "en"), 1.0, False

        clean_text = text.strip()
        lower_text = clean_text.lower()

        # 1. Native Script Matching
        telugu_chars = len(TELUGU_RANGE.findall(clean_text))
        hindi_chars = len(DEVANAGARI_RANGE.findall(clean_text))
        tamil_chars = len(TAMIL_RANGE.findall(clean_text))
        kannada_chars = len(KANNADA_RANGE.findall(clean_text))
        malayalam_chars = len(MALAYALAM_RANGE.findall(clean_text))
        total_chars = max(len(clean_text.replace(" ", "")), 1)

        english_words = re.findall(r'[a-zA-Z]+', clean_text)
        has_english_tokens = len(english_words) > 0

        if telugu_chars > 0:
            is_mixed = has_english_tokens or (telugu_chars / total_chars < 0.8)
            return "te", 0.96, is_mixed

        if hindi_chars > 0:
            is_mixed = has_english_tokens or (hindi_chars / total_chars < 0.8)
            return "hi", 0.96, is_mixed

        if tamil_chars > 0:
            is_mixed = has_english_tokens or (tamil_chars / total_chars < 0.8)
            return "ta", 0.96, is_mixed

        if kannada_chars > 0:
            is_mixed = has_english_tokens or (kannada_chars / total_chars < 0.8)
            return "kn", 0.96, is_mixed

        if malayalam_chars > 0:
            is_mixed = has_english_tokens or (malayalam_chars / total_chars < 0.8)
            return "ml", 0.96, is_mixed

        # 2. Romanized Regional Vocabulary (Tenglish, Hinglish, Tanglish, Kanglish)
        tokens = set(re.findall(r'\b\w+\b', lower_text))

        if (tokens & TELUGU_MARKERS) or any(p in lower_text for p in ["em chestunnav", "em tinali", "ela unnav", "baruvu peragali", "baruvu thaggali"]):
            return "te", 0.88, True

        if (tokens & HINDI_MARKERS) or any(p in lower_text for p in ["kya khana", "bataiye", "sehat ke liye", "kam karna", "kya haal", "kar rahe"]):
            return "hi", 0.88, True

        if (tokens & TAMIL_MARKERS) or any(p in lower_text for p in ["enna unavu", "eppadi irukkeenga"]):
            return "ta", 0.88, True

        if (tokens & KANNADA_MARKERS) or any(p in lower_text for p in ["enu maadthiddira", "thooka ilike"]):
            return "kn", 0.88, True

        # 3. English whenever Latin words exist and no regional markers matched
        if english_words:
            return "en", 0.95, False

        if fallback_lang and fallback_lang in ["te", "hi", "ta", "kn", "en"]:
            return fallback_lang, 0.75, False

        return "en", 0.95, False


language_detector = LanguageDetectionService()
