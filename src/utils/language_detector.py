"""Language detection utility for multi-language support."""

from langdetect import detect, detect_langs, LangDetectException
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# Language code to full name mapping
LANGUAGE_NAMES = {
    'en': 'English',
    'bn': 'Bengali (বাংলা)',
    'hi': 'Hindi (हिंदी)',
    'es': 'Spanish (Español)',
    'fr': 'French (Français)',
    'de': 'German (Deutsch)',
    'it': 'Italian (Italiano)',
    'pt': 'Portuguese (Português)',
    'ru': 'Russian (Русский)',
    'ja': 'Japanese (日本語)',
    'ko': 'Korean (한국어)',
    'zh-cn': 'Chinese Simplified (简体中文)',
    'zh-tw': 'Chinese Traditional (繁體中文)',
    'ar': 'Arabic (العربية)',
    'tr': 'Turkish (Türkçe)',
    'nl': 'Dutch (Nederlands)',
    'pl': 'Polish (Polski)',
    'sv': 'Swedish (Svenska)',
    'da': 'Danish (Dansk)',
    'fi': 'Finnish (Suomi)',
    'no': 'Norwegian (Norsk)',
    'th': 'Thai (ไทย)',
    'vi': 'Vietnamese (Tiếng Việt)',
    'id': 'Indonesian (Bahasa Indonesia)',
    'ms': 'Malay (Bahasa Melayu)',
    'ta': 'Tamil (தமிழ்)',
    'te': 'Telugu (తెలుగు)',
    'mr': 'Marathi (मराठी)',
    'gu': 'Gujarati (ગુજરાતી)',
    'ur': 'Urdu (اردو)',
    'fa': 'Persian (فارسی)',
    'he': 'Hebrew (עברית)',
    'el': 'Greek (Ελληνικά)',
    'cs': 'Czech (Čeština)',
    'ro': 'Romanian (Română)',
    'hu': 'Hungarian (Magyar)',
    'uk': 'Ukrainian (Українська)',
}

# Language-specific response instructions
LANGUAGE_INSTRUCTIONS = {
    'bn': 'বাংলায় উত্তর দিন। Use Bengali script.',
    'hi': 'हिंदी में जवाब दें। Use Hindi/Devanagari script.',
    'ar': 'أجب بالعربية. Use Arabic script, right-to-left.',
    'ja': '日本語で回答してください。Use Japanese script.',
    'ko': '한국어로 답변해 주세요. Use Korean script.',
    'zh-cn': '请用简体中文回答。Use Simplified Chinese.',
    'zh-tw': '請用繁體中文回答。Use Traditional Chinese.',
    'ru': 'Ответьте на русском языке. Use Cyrillic script.',
    'th': 'กรุณาตอบเป็นภาษาไทย. Use Thai script.',
    'ta': 'தமிழில் பதிலளிக்கவும். Use Tamil script.',
    'te': 'తెలుగులో సమాధానం ఇవ్వండి. Use Telugu script.',
    'ur': 'اردو میں جواب دیں۔ Use Urdu/Arabic script.',
    'he': 'ענה בעברית. Use Hebrew script, right-to-left.',
    'el': 'Απαντήστε στα Ελληνικά. Use Greek script.',
}


class LanguageDetector:
    """Detect language and provide multi-language support."""

    def __init__(self, default_language: str = 'en'):
        """
        Initialize language detector.

        Args:
            default_language: Default language code if detection fails
        """
        self.default_language = default_language

    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of input text.

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (language_code, confidence_score)
        """
        if not text or len(text.strip()) < 3:
            return self.default_language, 0.0

        try:
            # Get language with probabilities
            langs = detect_langs(text)
            if langs:
                top_lang = langs[0]
                return str(top_lang.lang), top_lang.prob
            return self.default_language, 0.0
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}")
            return self.default_language, 0.0

    def get_language_name(self, lang_code: str) -> str:
        """
        Get human-readable language name from code.

        Args:
            lang_code: ISO 639-1 language code

        Returns:
            Human-readable language name
        """
        return LANGUAGE_NAMES.get(lang_code, f'Unknown ({lang_code})')

    def get_response_instruction(self, lang_code: str) -> str:
        """
        Get language-specific instruction for the LLM.

        Args:
            lang_code: Detected language code

        Returns:
            Instruction string for the LLM to respond in that language
        """
        if lang_code == 'en':
            return "Respond in English."

        # Get specific instruction if available
        specific_instruction = LANGUAGE_INSTRUCTIONS.get(lang_code, '')
        lang_name = self.get_language_name(lang_code)

        if specific_instruction:
            return f"IMPORTANT: The user is writing in {lang_name}. {specific_instruction}"
        else:
            return f"IMPORTANT: The user is writing in {lang_name}. Please respond in the same language ({lang_code})."

    def get_language_info(self, text: str) -> Dict:
        """
        Get complete language information for a text.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with language code, name, confidence, and instruction
        """
        lang_code, confidence = self.detect_language(text)

        return {
            'code': lang_code,
            'name': self.get_language_name(lang_code),
            'confidence': round(confidence, 3),
            'instruction': self.get_response_instruction(lang_code),
            'is_rtl': lang_code in ['ar', 'he', 'ur', 'fa'],  # Right-to-left languages
        }


# Global instance
language_detector = LanguageDetector()


def detect_and_get_instruction(text: str) -> Tuple[str, str, Dict]:
    """
    Convenience function to detect language and get response instruction.

    Args:
        text: User input text

    Returns:
        Tuple of (language_code, instruction_for_llm, full_language_info)
    """
    info = language_detector.get_language_info(text)
    return info['code'], info['instruction'], info
