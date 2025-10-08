"""Manage user feedback and learning from interactions."""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from pathlib import Path


class FeedbackEntry:
    """Represents a single feedback entry."""

    def __init__(
        self,
        message_id: str,
        session_id: str,
        user_query: str,
        bot_response: str,
        feedback: str,  # 'positive' or 'negative'
        sources: List[Dict[str, Any]],
        context_used: bool,
        hallucination_detected: bool = False,
        hallucination_reasons: List[str] = None,
        timestamp: datetime = None
    ):
        self.message_id = message_id
        self.session_id = session_id
        self.user_query = user_query
        self.bot_response = bot_response
        self.feedback = feedback
        self.sources = sources
        self.context_used = context_used
        self.hallucination_detected = hallucination_detected
        self.hallucination_reasons = hallucination_reasons or []
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'message_id': self.message_id,
            'session_id': self.session_id,
            'user_query': self.user_query,
            'bot_response': self.bot_response,
            'feedback': self.feedback,
            'sources': self.sources,
            'context_used': self.context_used,
            'hallucination_detected': self.hallucination_detected,
            'hallucination_reasons': self.hallucination_reasons,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeedbackEntry':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class FeedbackManager:
    """Manage feedback collection and learning."""

    def __init__(self, feedback_dir: str = "./data/feedback"):
        """
        Initialize feedback manager.

        Args:
            feedback_dir: Directory to store feedback data
        """
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

        self.feedback_file = self.feedback_dir / "feedback.jsonl"
        self.stats_file = self.feedback_dir / "stats.json"

        # In-memory cache for quick access
        self.feedback_cache: List[FeedbackEntry] = []
        self._load_feedback()

    def _load_feedback(self):
        """Load existing feedback from disk."""
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.feedback_cache.append(FeedbackEntry.from_dict(data))

    def add_feedback(
        self,
        message_id: str,
        session_id: str,
        user_query: str,
        bot_response: str,
        feedback: str,
        sources: List[Dict[str, Any]],
        context_used: bool,
        hallucination_detected: bool = False,
        hallucination_reasons: List[str] = None
    ) -> FeedbackEntry:
        """
        Add new feedback entry.

        Args:
            message_id: Unique message identifier
            session_id: Session identifier
            user_query: User's query
            bot_response: Bot's response
            feedback: 'positive' or 'negative'
            sources: Retrieved sources used
            context_used: Whether context was used
            hallucination_detected: Whether hallucination was detected
            hallucination_reasons: Reasons for hallucination detection

        Returns:
            Created FeedbackEntry
        """
        entry = FeedbackEntry(
            message_id=message_id,
            session_id=session_id,
            user_query=user_query,
            bot_response=bot_response,
            feedback=feedback,
            sources=sources,
            context_used=context_used,
            hallucination_detected=hallucination_detected,
            hallucination_reasons=hallucination_reasons
        )

        # Add to cache
        self.feedback_cache.append(entry)

        # Append to file (JSONL format for easy streaming)
        with open(self.feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')

        # Update statistics
        self._update_stats()

        return entry

    def get_feedback_by_message(self, message_id: str) -> Optional[FeedbackEntry]:
        """Get feedback for a specific message."""
        for entry in self.feedback_cache:
            if entry.message_id == message_id:
                return entry
        return None

    def get_feedback_by_session(self, session_id: str) -> List[FeedbackEntry]:
        """Get all feedback for a session."""
        return [e for e in self.feedback_cache if e.session_id == session_id]

    def get_negative_feedback(self) -> List[FeedbackEntry]:
        """Get all negative feedback entries."""
        return [e for e in self.feedback_cache if e.feedback == 'negative']

    def get_hallucinations(self) -> List[FeedbackEntry]:
        """Get all entries marked as hallucinations."""
        return [e for e in self.feedback_cache if e.hallucination_detected]

    def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        total = len(self.feedback_cache)
        if total == 0:
            return {
                'total_feedback': 0,
                'positive_count': 0,
                'negative_count': 0,
                'positive_rate': 0.0,
                'hallucination_count': 0,
                'hallucination_rate': 0.0,
                'context_usage_rate': 0.0
            }

        positive = sum(1 for e in self.feedback_cache if e.feedback == 'positive')
        negative = sum(1 for e in self.feedback_cache if e.feedback == 'negative')
        hallucinations = sum(1 for e in self.feedback_cache if e.hallucination_detected)
        context_used = sum(1 for e in self.feedback_cache if e.context_used)

        return {
            'total_feedback': total,
            'positive_count': positive,
            'negative_count': negative,
            'positive_rate': positive / total if total > 0 else 0.0,
            'hallucination_count': hallucinations,
            'hallucination_rate': hallucinations / total if total > 0 else 0.0,
            'context_usage_rate': context_used / total if total > 0 else 0.0,
            'common_hallucination_reasons': self._get_common_hallucination_reasons()
        }

    def _get_common_hallucination_reasons(self) -> Dict[str, int]:
        """Get most common hallucination reasons."""
        reasons = {}
        for entry in self.feedback_cache:
            if entry.hallucination_detected:
                for reason in entry.hallucination_reasons:
                    reasons[reason] = reasons.get(reason, 0) + 1

        # Sort by frequency
        return dict(sorted(reasons.items(), key=lambda x: x[1], reverse=True))

    def _update_stats(self):
        """Update statistics file."""
        stats = self.get_stats()
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

    def get_problematic_queries(self, min_negative_rate: float = 0.5) -> List[Dict[str, Any]]:
        """
        Find queries that frequently get negative feedback.

        Args:
            min_negative_rate: Minimum negative feedback rate to consider problematic

        Returns:
            List of problematic query patterns
        """
        query_feedback = {}

        for entry in self.feedback_cache:
            query = entry.user_query.lower().strip()
            if query not in query_feedback:
                query_feedback[query] = {'positive': 0, 'negative': 0}

            if entry.feedback == 'positive':
                query_feedback[query]['positive'] += 1
            else:
                query_feedback[query]['negative'] += 1

        problematic = []
        for query, counts in query_feedback.items():
            total = counts['positive'] + counts['negative']
            negative_rate = counts['negative'] / total if total > 0 else 0

            if negative_rate >= min_negative_rate and total >= 2:  # At least 2 feedback entries
                problematic.append({
                    'query': query,
                    'total_feedback': total,
                    'negative_count': counts['negative'],
                    'negative_rate': negative_rate
                })

        return sorted(problematic, key=lambda x: x['negative_rate'], reverse=True)

    def export_feedback(self, output_file: str = None) -> str:
        """
        Export all feedback to a JSON file.

        Args:
            output_file: Output file path (optional)

        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.feedback_dir / f"feedback_export_{timestamp}.json"

        data = {
            'export_date': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'feedback_entries': [e.to_dict() for e in self.feedback_cache]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return str(output_file)
