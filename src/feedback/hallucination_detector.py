"""Detect hallucinations in chatbot responses."""

from typing import Dict, List, Tuple, Any
import re


class HallucinationDetector:
    """Detect potential hallucinations in bot responses."""

    def __init__(self):
        """Initialize hallucination detector."""
        # Patterns that might indicate hallucination
        self.uncertainty_phrases = [
            "i think", "i believe", "probably", "maybe", "perhaps",
            "it seems", "it appears", "might be", "could be"
        ]

        # Phrases that indicate making up information
        self.fabrication_indicators = [
            "as far as i know", "to the best of my knowledge",
            "i'm not entirely sure", "i don't have access",
            "i cannot confirm", "i'm unable to verify"
        ]

        # Specific details that shouldn't be in responses without source
        self.specific_patterns = [
            r'\$\d+\.\d{2}',  # Specific prices
            r'\d{1,2}:\d{2}\s*(am|pm|AM|PM)',  # Specific times
            r'\d{4}-\d{2}-\d{2}',  # Specific dates
            r'\d{3}-\d{3}-\d{4}',  # Phone numbers
            r'\b\d+ (main|street|avenue|road|boulevard)\b',  # Specific addresses
        ]

    def detect(
        self,
        response: str,
        query: str,
        sources: List[Dict[str, Any]],
        context_used: bool
    ) -> Tuple[bool, List[str], float]:
        """
        Detect potential hallucinations in response.

        Args:
            response: Bot's response text
            query: User's query
            sources: Retrieved source documents
            context_used: Whether context was used in generation

        Returns:
            Tuple of (is_hallucination, reasons, confidence_score)
        """
        reasons = []
        hallucination_score = 0.0

        response_lower = response.lower()

        # Check 1: No context used (high risk)
        if not context_used:
            reasons.append("no_context_used")
            hallucination_score += 0.4

        # Check 2: Low source relevance
        if sources:
            avg_relevance = sum(s.get('relevance_score', 0) for s in sources) / len(sources)
            if avg_relevance < 0.5:
                reasons.append("low_source_relevance")
                hallucination_score += 0.3

        # Check 3: Uncertainty phrases
        uncertainty_count = sum(1 for phrase in self.uncertainty_phrases if phrase in response_lower)
        if uncertainty_count > 0:
            reasons.append(f"contains_uncertainty_phrases_{uncertainty_count}")
            hallucination_score += min(uncertainty_count * 0.1, 0.3)

        # Check 4: Fabrication indicators
        fabrication_count = sum(1 for phrase in self.fabrication_indicators if phrase in response_lower)
        if fabrication_count > 0:
            reasons.append(f"contains_fabrication_indicators_{fabrication_count}")
            hallucination_score += min(fabrication_count * 0.15, 0.4)

        # Check 5: Specific details without sources
        specific_details = []
        for pattern in self.specific_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                specific_details.extend(matches)

        if specific_details and len(sources) == 0:
            reasons.append("specific_details_without_sources")
            hallucination_score += 0.5

        # Check 6: Response contradicts common patterns in sources
        if sources and self._check_contradiction(response, sources):
            reasons.append("potential_contradiction_with_sources")
            hallucination_score += 0.6

        # Check 7: Response is too generic
        if self._is_too_generic(response, query):
            reasons.append("response_too_generic")
            hallucination_score += 0.2

        # Check 8: Mentions inability to help
        inability_phrases = [
            "i cannot help", "i'm unable to", "i don't have information",
            "i cannot provide", "sorry, i don't know"
        ]
        if any(phrase in response_lower for phrase in inability_phrases):
            reasons.append("explicit_inability_to_answer")
            hallucination_score += 0.1  # Not really hallucination, but worth noting

        # Normalize score
        hallucination_score = min(hallucination_score, 1.0)

        # Determine if it's a hallucination (threshold: 0.6)
        is_hallucination = hallucination_score >= 0.6

        return is_hallucination, reasons, hallucination_score

    def _check_contradiction(self, response: str, sources: List[Dict[str, Any]]) -> bool:
        """
        Check if response contradicts source information.

        This is a simple heuristic check. In production, you'd use more
        sophisticated NLP techniques.
        """
        # Extract source content
        source_text = " ".join([
            s.get('content', '') for s in sources if 'content' in s
        ]).lower()

        if not source_text:
            return False

        response_lower = response.lower()

        # Simple contradiction patterns
        contradiction_pairs = [
            ('yes', 'no'),
            ('can', 'cannot'),
            ('will', 'will not'),
            ('does', 'does not'),
            ('is', 'is not'),
            ('available', 'unavailable'),
            ('accept', 'not accept'),
            ('offer', 'not offer'),
        ]

        # Check for opposite words
        for word1, word2 in contradiction_pairs:
            if word1 in response_lower and word2 in source_text:
                return True
            if word2 in response_lower and word1 in source_text:
                return True

        return False

    def _is_too_generic(self, response: str, query: str) -> bool:
        """Check if response is too generic/vague."""
        # Very short responses are often too generic
        if len(response.split()) < 10:
            return True

        # Responses that don't mention any keywords from the query
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())

        # Remove common words
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about',
            'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'what',
            'when', 'where', 'who', 'which', 'why', 'how', 'can',
            'could', 'would', 'should', 'may', 'might', 'will',
            'i', 'you', 'your', 'my', 'our'
        }

        query_keywords = query_words - common_words
        response_keywords = response_words - common_words

        # If response doesn't share ANY keywords with query
        if query_keywords and not (query_keywords & response_keywords):
            return True

        return False

    def get_confidence_label(self, score: float) -> str:
        """Get human-readable confidence label."""
        if score >= 0.8:
            return "Very High Risk"
        elif score >= 0.6:
            return "High Risk"
        elif score >= 0.4:
            return "Medium Risk"
        elif score >= 0.2:
            return "Low Risk"
        else:
            return "Very Low Risk"

    def analyze_response_quality(
        self,
        response: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of response quality.

        Returns:
            Dictionary with quality metrics
        """
        word_count = len(response.split())
        sentence_count = len([s for s in response.split('.') if s.strip()])

        source_count = len(sources)
        avg_relevance = (
            sum(s.get('relevance_score', 0) for s in sources) / source_count
            if source_count > 0 else 0
        )

        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'source_count': source_count,
            'avg_source_relevance': avg_relevance,
            'has_uncertainty': any(
                phrase in response.lower()
                for phrase in self.uncertainty_phrases
            ),
            'has_fabrication_indicators': any(
                phrase in response.lower()
                for phrase in self.fabrication_indicators
            )
        }
