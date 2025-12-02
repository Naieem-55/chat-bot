"""Utility modules for the RAG chatbot."""

from .language_detector import (
    LanguageDetector,
    language_detector,
    detect_and_get_instruction,
    LANGUAGE_NAMES,
)

from .web_search import (
    WebSearcher,
    web_searcher,
    search_web,
)

__all__ = [
    'LanguageDetector',
    'language_detector',
    'detect_and_get_instruction',
    'LANGUAGE_NAMES',
    'WebSearcher',
    'web_searcher',
    'search_web',
]
