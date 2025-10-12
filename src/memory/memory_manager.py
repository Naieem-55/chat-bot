"""
Long-Term Memory Manager for RAG Chatbot
Handles persistent memory storage, retrieval, and context fusion
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib


class MemoryManager:
    """Manages long-term memory storage and retrieval"""

    def __init__(self, storage_dir: str = "data/memory"):
        """
        Initialize memory manager

        Args:
            storage_dir: Directory to store memory files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Memory types
        self.user_facts_file = self.storage_dir / "user_facts.json"
        self.preferences_file = self.storage_dir / "preferences.json"
        self.conversation_summaries_file = self.storage_dir / "conversation_summaries.json"

        # Initialize storage files
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize storage files if they don't exist"""
        for file_path in [self.user_facts_file, self.preferences_file, self.conversation_summaries_file]:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump({}, f, indent=2)

    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_json(self, file_path: Path, data: Dict):
        """Save JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def store_user_fact(self, session_id: str, fact: str, category: str = "general"):
        """
        Store a fact about the user

        Args:
            session_id: User session ID
            fact: Fact to store
            category: Category of the fact (e.g., "preferences", "personal", "interests")
        """
        facts = self._load_json(self.user_facts_file)

        if session_id not in facts:
            facts[session_id] = []

        fact_entry = {
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "id": hashlib.md5(fact.encode()).hexdigest()[:8]
        }

        # Avoid duplicates
        if not any(f["fact"].lower() == fact.lower() for f in facts[session_id]):
            facts[session_id].append(fact_entry)
            self._save_json(self.user_facts_file, facts)

    def get_user_facts(self, session_id: str, category: Optional[str] = None) -> List[Dict]:
        """
        Retrieve facts about the user

        Args:
            session_id: User session ID
            category: Filter by category (optional)

        Returns:
            List of user facts
        """
        facts = self._load_json(self.user_facts_file)
        user_facts = facts.get(session_id, [])

        if category:
            user_facts = [f for f in user_facts if f["category"] == category]

        # Sort by timestamp (most recent first)
        user_facts.sort(key=lambda x: x["timestamp"], reverse=True)
        return user_facts

    def store_preference(self, session_id: str, key: str, value: Any):
        """
        Store user preference

        Args:
            session_id: User session ID
            key: Preference key
            value: Preference value
        """
        preferences = self._load_json(self.preferences_file)

        if session_id not in preferences:
            preferences[session_id] = {}

        preferences[session_id][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

        self._save_json(self.preferences_file, preferences)

    def get_preference(self, session_id: str, key: str) -> Optional[Any]:
        """Get user preference"""
        preferences = self._load_json(self.preferences_file)
        user_prefs = preferences.get(session_id, {})

        if key in user_prefs:
            return user_prefs[key]["value"]
        return None

    def get_all_preferences(self, session_id: str) -> Dict:
        """Get all user preferences"""
        preferences = self._load_json(self.preferences_file)
        return preferences.get(session_id, {})

    def store_conversation_summary(self, session_id: str, summary: str, topic: str = "general"):
        """
        Store conversation summary

        Args:
            session_id: User session ID
            summary: Conversation summary
            topic: Main topic of conversation
        """
        summaries = self._load_json(self.conversation_summaries_file)

        if session_id not in summaries:
            summaries[session_id] = []

        summary_entry = {
            "summary": summary,
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "id": hashlib.md5(f"{summary}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        }

        summaries[session_id].append(summary_entry)

        # Keep only last 50 summaries per user
        if len(summaries[session_id]) > 50:
            summaries[session_id] = summaries[session_id][-50:]

        self._save_json(self.conversation_summaries_file, summaries)

    def get_conversation_summaries(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation summaries"""
        summaries = self._load_json(self.conversation_summaries_file)
        user_summaries = summaries.get(session_id, [])

        # Sort by timestamp (most recent first)
        user_summaries.sort(key=lambda x: x["timestamp"], reverse=True)
        return user_summaries[:limit]

    def extract_facts_from_conversation(self, user_message: str, bot_response: str) -> List[str]:
        """
        Extract potential facts from conversation
        Uses simple heuristics to identify user information

        Args:
            user_message: User's message
            bot_response: Bot's response

        Returns:
            List of extracted facts
        """
        facts = []
        user_lower = user_message.lower()

        # Detect preferences
        preference_patterns = [
            ("i like", "likes"),
            ("i love", "loves"),
            ("i prefer", "prefers"),
            ("i enjoy", "enjoys"),
            ("my favorite", "favorite is"),
            ("i hate", "dislikes"),
            ("i dislike", "dislikes")
        ]

        for pattern, label in preference_patterns:
            if pattern in user_lower:
                # Extract what comes after the pattern
                parts = user_lower.split(pattern)
                if len(parts) > 1:
                    preference = parts[1].split('.')[0].split(',')[0].strip()
                    if preference:
                        facts.append(f"User {label} {preference}")

        # Detect personal info (be careful with PII)
        personal_patterns = [
            ("my name is", "name is"),
            ("i am a", "is a"),
            ("i work as", "works as"),
            ("i live in", "lives in"),
            ("i'm from", "is from")
        ]

        for pattern, label in personal_patterns:
            if pattern in user_lower:
                parts = user_lower.split(pattern)
                if len(parts) > 1:
                    info = parts[1].split('.')[0].split(',')[0].strip()
                    if info and len(info) < 50:  # Reasonable length
                        facts.append(f"User {label} {info}")

        return facts

    def fuse_context(self, query: str, retrieved_docs: List[Dict], session_id: str) -> str:
        """
        Fuse context from multiple sources: retrieved documents + long-term memory

        Args:
            query: User query
            retrieved_docs: Documents retrieved from vector store
            session_id: User session ID

        Returns:
            Fused context string
        """
        context_parts = []

        # 1. Add retrieved documents context
        if retrieved_docs:
            try:
                doc_context = "\n\n".join([
                    f"Document: {doc.get('metadata', {}).get('source', doc.get('source', 'Unknown'))}\n{doc.get('content', '')}"
                    for doc in retrieved_docs[:3]  # Top 3 documents
                ])
                context_parts.append(f"## Retrieved Information:\n{doc_context}")
            except Exception as e:
                # Fallback if structure is different
                doc_context = "\n\n".join([str(doc) for doc in retrieved_docs[:3]])
                context_parts.append(f"## Retrieved Information:\n{doc_context}")

        # 2. Add relevant user facts
        user_facts = self.get_user_facts(session_id)
        if user_facts:
            facts_text = "\n".join([f"- {fact['fact']}" for fact in user_facts[:5]])
            context_parts.append(f"## User Context (What I know about you):\n{facts_text}")

        # 3. Add user preferences
        preferences = self.get_all_preferences(session_id)
        if preferences:
            prefs_text = "\n".join([
                f"- {key}: {pref['value']}"
                for key, pref in list(preferences.items())[:5]
            ])
            context_parts.append(f"## User Preferences:\n{prefs_text}")

        # 4. Add relevant conversation summaries
        summaries = self.get_conversation_summaries(session_id, limit=3)
        if summaries:
            summaries_text = "\n".join([
                f"- [{s['topic']}] {s['summary']}"
                for s in summaries
            ])
            context_parts.append(f"## Previous Conversations:\n{summaries_text}")

        # Combine all context
        fused_context = "\n\n".join(context_parts)
        return fused_context

    def get_memory_stats(self, session_id: str) -> Dict[str, int]:
        """Get memory statistics for a user"""
        return {
            "facts_count": len(self.get_user_facts(session_id)),
            "preferences_count": len(self.get_all_preferences(session_id)),
            "summaries_count": len(self.get_conversation_summaries(session_id, limit=100))
        }

    def clear_user_memory(self, session_id: str):
        """Clear all memory for a specific user"""
        # Clear facts
        facts = self._load_json(self.user_facts_file)
        if session_id in facts:
            del facts[session_id]
            self._save_json(self.user_facts_file, facts)

        # Clear preferences
        preferences = self._load_json(self.preferences_file)
        if session_id in preferences:
            del preferences[session_id]
            self._save_json(self.preferences_file, preferences)

        # Clear summaries
        summaries = self._load_json(self.conversation_summaries_file)
        if session_id in summaries:
            del summaries[session_id]
            self._save_json(self.conversation_summaries_file, summaries)
