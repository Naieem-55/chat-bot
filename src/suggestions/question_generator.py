"""Generate suggested questions based on document content."""

from typing import List, Dict, Set
import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generate smart question suggestions from documents."""

    def __init__(self):
        """Initialize question generator."""
        # Common question starters
        self.question_starters = [
            "What is", "What are", "How does", "How do", "How to",
            "Why is", "Why does", "When should", "Where can",
            "Which is", "Can I", "Should I", "Is it", "Are there"
        ]

        # Common topics to extract
        self.topic_patterns = [
            r'\b[A-Z][A-Za-z]+\b',  # Capitalized words (proper nouns)
        ]

    def generate_from_documents(
        self,
        documents: List[Dict],
        max_questions: int = 10
    ) -> List[str]:
        """
        Generate suggested questions from document content.

        Args:
            documents: List of documents with 'page_content' and 'metadata'
            max_questions: Maximum number of questions to generate

        Returns:
            List of suggested questions
        """
        if not documents:
            return self._get_default_questions()

        # Extract topics from documents
        topics = self._extract_topics(documents)

        # Generate questions based on topics
        questions = self._generate_questions_from_topics(topics)

        # Add document-specific questions
        questions.extend(self._extract_existing_questions(documents))

        # Remove duplicates and limit
        unique_questions = list(dict.fromkeys(questions))[:max_questions]

        return unique_questions if unique_questions else self._get_default_questions()

    def generate_follow_ups(
        self,
        user_query: str,
        bot_response: str,
        context_docs: List[Dict]
    ) -> List[str]:
        """
        Generate follow-up questions based on current conversation.

        Args:
            user_query: User's question
            bot_response: Bot's response
            context_docs: Documents used in response

        Returns:
            List of follow-up questions
        """
        follow_ups = []

        # Extract main topic from query
        query_lower = user_query.lower()

        # Pattern-based follow-ups
        if any(word in query_lower for word in ['what is', 'what are', 'define']):
            # User asked "what is X" -> suggest "how to use X", "examples of X"
            topic = self._extract_main_topic(user_query)
            if topic:
                follow_ups.append(f"How to use {topic}?")
                follow_ups.append(f"What are examples of {topic}?")
                follow_ups.append(f"What are the benefits of {topic}?")

        elif any(word in query_lower for word in ['how to', 'how do', 'how does']):
            # User asked "how to X" -> suggest "why X", "alternatives to X"
            topic = self._extract_main_topic(user_query)
            if topic:
                follow_ups.append(f"Why use {topic}?")
                follow_ups.append(f"What are alternatives to {topic}?")
                follow_ups.append(f"What are common {topic} mistakes?")

        elif any(word in query_lower for word in ['why', 'reason']):
            # User asked "why" -> suggest practical applications
            topic = self._extract_main_topic(user_query)
            if topic:
                follow_ups.append(f"How to implement {topic}?")
                follow_ups.append(f"What are {topic} best practices?")

        # Extract topics from response for related questions
        response_topics = self._extract_topics_from_text(bot_response)
        for topic in response_topics[:2]:  # Top 2 topics
            if topic.lower() not in query_lower:
                follow_ups.append(f"Tell me more about {topic}")
                follow_ups.append(f"How does {topic} work?")

        # Limit to 5 follow-ups
        return follow_ups[:5]

    def generate_autocomplete(
        self,
        partial_query: str,
        documents: List[Dict],
        max_suggestions: int = 5
    ) -> List[str]:
        """
        Generate autocomplete suggestions based on partial query.

        Args:
            partial_query: Partial user input
            documents: Available documents
            max_suggestions: Max number of suggestions

        Returns:
            List of autocomplete suggestions
        """
        if len(partial_query) < 3:
            return []

        suggestions = []
        partial_lower = partial_query.lower()

        # Get common questions
        common_questions = self.generate_from_documents(documents, max_questions=20)

        # Filter questions that start with or contain partial query
        for question in common_questions:
            question_lower = question.lower()
            if question_lower.startswith(partial_lower):
                suggestions.append(question)
            elif partial_lower in question_lower and len(suggestions) < max_suggestions:
                suggestions.append(question)

        # If no matches, suggest question completions
        if not suggestions:
            suggestions = self._suggest_question_completions(partial_query)

        return suggestions[:max_suggestions]

    def _extract_topics(self, documents: List[Dict]) -> List[str]:
        """Extract main topics from documents."""
        topics = []

        for doc in documents[:10]:  # First 10 docs
            content = doc.get('page_content', '')

            # Extract capitalized words (potential topics)
            capitalized = re.findall(r'\b[A-Z][A-Za-z]{2,}\b', content)
            topics.extend(capitalized)

            # Extract from metadata
            metadata = doc.get('metadata', {})
            if 'category' in metadata:
                topics.append(metadata['category'])

        # Count frequency and return most common
        topic_counts = Counter(topics)
        common_topics = [topic for topic, count in topic_counts.most_common(10)]

        return common_topics

    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from text."""
        # Extract capitalized words (proper nouns)
        topics = re.findall(r'\b[A-Z][A-Za-z]{2,}\b', text)

        # Count frequency
        topic_counts = Counter(topics)
        return [topic for topic, count in topic_counts.most_common(5)]

    def _extract_main_topic(self, query: str) -> str:
        """Extract main topic from query."""
        # Remove common question words
        topic = query.lower()
        remove_words = [
            'what is', 'what are', 'how to', 'how do', 'how does',
            'why is', 'why does', 'where can', 'when should',
            'can i', 'should i', 'tell me about', '?'
        ]

        for word in remove_words:
            topic = topic.replace(word, '')

        return topic.strip()

    def _generate_questions_from_topics(self, topics: List[str]) -> List[str]:
        """Generate questions based on extracted topics."""
        questions = []

        for topic in topics[:5]:  # Top 5 topics
            questions.append(f"What is {topic}?")
            questions.append(f"How to use {topic}?")
            questions.append(f"What are {topic} best practices?")

        return questions

    def _extract_existing_questions(self, documents: List[Dict]) -> List[str]:
        """Extract questions that appear in documents."""
        questions = []

        for doc in documents[:5]:
            content = doc.get('page_content', '')

            # Find sentences ending with ?
            potential_questions = re.findall(r'([A-Z][^.!?]*\?)', content)

            for q in potential_questions:
                # Filter out too long or too short
                if 10 < len(q) < 100:
                    questions.append(q.strip())

        return questions[:5]

    def _suggest_question_completions(self, partial: str) -> List[str]:
        """Suggest question completions for partial input."""
        completions = []
        partial_lower = partial.lower()

        # Pattern matching
        if partial_lower.startswith('what'):
            completions = [
                "What is HTML?",
                "What are the main features?",
                "What is the difference between?",
                "What are best practices?",
            ]
        elif partial_lower.startswith('how'):
            completions = [
                "How to get started?",
                "How does it work?",
                "How to implement?",
                "How to troubleshoot?",
            ]
        elif partial_lower.startswith('why'):
            completions = [
                "Why is it important?",
                "Why should I use it?",
                "Why does it matter?",
            ]
        else:
            completions = self._get_default_questions()

        return completions

    def _get_default_questions(self) -> List[str]:
        """Get default questions when no documents available."""
        return [
            "What can you help me with?",
            "How does this work?",
            "What topics are available?",
            "Can you give me an overview?",
            "What are the main features?",
        ]


class PeopleAlsoAsked:
    """Generate 'People Also Asked' suggestions."""

    def __init__(self):
        """Initialize PAA generator."""
        self.question_templates = {
            'definition': [
                "What does {topic} mean?",
                "How would you define {topic}?",
                "What is the purpose of {topic}?",
            ],
            'usage': [
                "How is {topic} used?",
                "When should I use {topic}?",
                "What are {topic} use cases?",
            ],
            'comparison': [
                "What is the difference between {topic} and alternatives?",
                "How does {topic} compare to others?",
                "{topic} vs alternatives?",
            ],
            'examples': [
                "Can you show {topic} examples?",
                "What are some {topic} examples?",
                "How to implement {topic}?",
            ]
        }

    def generate(
        self,
        user_query: str,
        response: str,
        max_questions: int = 4
    ) -> List[str]:
        """
        Generate 'People Also Asked' questions.

        Args:
            user_query: Original user query
            response: Bot's response
            max_questions: Max questions to generate

        Returns:
            List of related questions
        """
        paa_questions = []

        # Extract main topic
        topic = self._extract_topic(user_query)

        if not topic:
            return []

        # Determine query type
        query_lower = user_query.lower()

        if any(word in query_lower for word in ['what is', 'what are', 'define']):
            # Definition query -> suggest usage, examples
            paa_questions.extend([
                f"How to use {topic}?",
                f"What are {topic} examples?",
                f"What are the benefits of {topic}?",
                f"When should I use {topic}?",
            ])

        elif any(word in query_lower for word in ['how to', 'how do']):
            # How-to query -> suggest examples, best practices
            paa_questions.extend([
                f"What are {topic} best practices?",
                f"What are common {topic} mistakes?",
                f"Can you show {topic} examples?",
                f"What is {topic}?",
            ])

        elif any(word in query_lower for word in ['why', 'reason']):
            # Why query -> suggest how-to, benefits
            paa_questions.extend([
                f"How to implement {topic}?",
                f"What are the benefits of {topic}?",
                f"What is {topic}?",
                f"When should I use {topic}?",
            ])

        else:
            # Generic questions
            paa_questions.extend([
                f"What is {topic}?",
                f"How to use {topic}?",
                f"What are {topic} examples?",
                f"Why use {topic}?",
            ])

        return paa_questions[:max_questions]

    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query."""
        # Remove question words
        topic = query.lower()
        remove_words = [
            'what is', 'what are', 'how to', 'how do', 'how does',
            'why is', 'why does', 'where can', 'when should',
            'can i', 'should i', 'tell me about', '?', 'the', 'a', 'an'
        ]

        for word in remove_words:
            topic = topic.replace(word, '')

        # Capitalize first letter
        topic = topic.strip()
        if topic:
            topic = topic[0].upper() + topic[1:]

        return topic
