"""Session management for multi-turn conversations."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid


class ConversationSession:
    """Represents a single conversation session."""

    def __init__(self, session_id: str):
        """Initialize conversation session."""
        self.session_id = session_id
        self.messages: List[Dict[str, str]] = []
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.metadata: Dict[str, any] = {}

    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        self.last_active = datetime.now()

    def get_history(self, max_messages: int = None) -> List[Dict[str, str]]:
        """
        Get conversation history.

        Args:
            max_messages: Maximum number of messages to return (most recent)

        Returns:
            List of messages
        """
        if max_messages and len(self.messages) > max_messages:
            return self.messages[-max_messages:]
        return self.messages

    def clear_history(self):
        """Clear conversation history."""
        self.messages = []

    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if session is expired."""
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_active > timeout


class SessionManager:
    """Manage conversation sessions."""

    def __init__(self, max_history: int = 10, session_timeout: int = 60):
        """
        Initialize session manager.

        Args:
            max_history: Maximum messages to keep in history
            session_timeout: Session timeout in minutes
        """
        self.sessions: Dict[str, ConversationSession] = {}
        self.max_history = max_history
        self.session_timeout = session_timeout

    def create_session(self) -> str:
        """
        Create a new session.

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ConversationSession(session_id)
        return session_id

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            ConversationSession or None if not found
        """
        session = self.sessions.get(session_id)

        if session and session.is_expired(self.session_timeout):
            # Clean up expired session
            del self.sessions[session_id]
            return None

        return session

    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """
        Add a message to a session.

        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content

        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.add_message(role, content)

        # Limit history size
        if len(session.messages) > self.max_history * 2:  # *2 for user+assistant pairs
            session.messages = session.messages[-(self.max_history * 2):]

        return True

    def get_history(
        self,
        session_id: str,
        max_messages: int = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier
            max_messages: Maximum number of messages to return

        Returns:
            List of messages or empty list if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return []

        return session.get_history(max_messages or self.max_history * 2)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def cleanup_expired_sessions(self):
        """Remove all expired sessions."""
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]

        for sid in expired:
            del self.sessions[sid]

        return len(expired)

    def get_session_count(self) -> int:
        """Get total number of active sessions."""
        return len(self.sessions)
