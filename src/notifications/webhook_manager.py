"""Webhook manager for handling notification subscriptions."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WebhookManager:
    """Manages webhook configurations and subscriptions."""

    def __init__(self, storage_dir: str = "data/webhooks"):
        """
        Initialize webhook manager.

        Args:
            storage_dir: Directory to store webhook configurations
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.storage_dir / "webhooks.json"
        self.webhooks = self._load_webhooks()

    def _load_webhooks(self) -> Dict:
        """Load webhook configurations from storage."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load webhooks: {e}")
                return {}
        return {}

    def _save_webhooks(self):
        """Save webhook configurations to storage."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.webhooks, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save webhooks: {e}")

    def add_email_webhook(
        self,
        webhook_id: str,
        email: str,
        events: List[str],
        enabled: bool = True
    ) -> Dict:
        """
        Add or update an email webhook.

        Args:
            webhook_id: Unique webhook identifier
            email: Email address to send notifications to
            events: List of events to subscribe to
            enabled: Whether webhook is enabled

        Returns:
            Updated webhook configuration
        """
        webhook_config = {
            "id": webhook_id,
            "type": "email",
            "email": email,
            "events": events,
            "enabled": enabled,
            "created_at": self.webhooks.get(webhook_id, {}).get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat()
        }

        self.webhooks[webhook_id] = webhook_config
        self._save_webhooks()

        logger.info(f"✓ Email webhook configured: {webhook_id} -> {email}")
        return webhook_config

    def remove_webhook(self, webhook_id: str) -> bool:
        """
        Remove a webhook configuration.

        Args:
            webhook_id: Webhook identifier to remove

        Returns:
            True if removed, False if not found
        """
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            self._save_webhooks()
            logger.info(f"✓ Webhook removed: {webhook_id}")
            return True
        return False

    def get_webhook(self, webhook_id: str) -> Optional[Dict]:
        """
        Get webhook configuration by ID.

        Args:
            webhook_id: Webhook identifier

        Returns:
            Webhook configuration or None
        """
        return self.webhooks.get(webhook_id)

    def list_webhooks(self, webhook_type: Optional[str] = None) -> List[Dict]:
        """
        List all webhooks, optionally filtered by type.

        Args:
            webhook_type: Optional type filter (e.g., "email")

        Returns:
            List of webhook configurations
        """
        webhooks = list(self.webhooks.values())

        if webhook_type:
            webhooks = [w for w in webhooks if w.get("type") == webhook_type]

        return webhooks

    def enable_webhook(self, webhook_id: str) -> bool:
        """
        Enable a webhook.

        Args:
            webhook_id: Webhook identifier

        Returns:
            True if enabled successfully
        """
        if webhook_id in self.webhooks:
            self.webhooks[webhook_id]["enabled"] = True
            self.webhooks[webhook_id]["updated_at"] = datetime.now().isoformat()
            self._save_webhooks()
            logger.info(f"✓ Webhook enabled: {webhook_id}")
            return True
        return False

    def disable_webhook(self, webhook_id: str) -> bool:
        """
        Disable a webhook.

        Args:
            webhook_id: Webhook identifier

        Returns:
            True if disabled successfully
        """
        if webhook_id in self.webhooks:
            self.webhooks[webhook_id]["enabled"] = False
            self.webhooks[webhook_id]["updated_at"] = datetime.now().isoformat()
            self._save_webhooks()
            logger.info(f"✓ Webhook disabled: {webhook_id}")
            return True
        return False

    def get_webhooks_for_event(self, event_type: str) -> List[Dict]:
        """
        Get all enabled webhooks subscribed to a specific event.

        Args:
            event_type: Event type (e.g., "new_message", "error", "feedback")

        Returns:
            List of webhook configurations subscribed to this event
        """
        matching_webhooks = []

        for webhook in self.webhooks.values():
            if webhook.get("enabled", False) and event_type in webhook.get("events", []):
                matching_webhooks.append(webhook)

        return matching_webhooks

    def update_webhook_events(self, webhook_id: str, events: List[str]) -> bool:
        """
        Update events for a webhook.

        Args:
            webhook_id: Webhook identifier
            events: New list of events to subscribe to

        Returns:
            True if updated successfully
        """
        if webhook_id in self.webhooks:
            self.webhooks[webhook_id]["events"] = events
            self.webhooks[webhook_id]["updated_at"] = datetime.now().isoformat()
            self._save_webhooks()
            logger.info(f"✓ Webhook events updated: {webhook_id}")
            return True
        return False

    def get_available_events(self) -> List[Dict[str, str]]:
        """
        Get list of available events that can be subscribed to.

        Returns:
            List of event definitions with name and description
        """
        return [
            {
                "name": "new_message",
                "description": "Triggered when a new chat message is received",
                "icon": "💬"
            },
            {
                "name": "error",
                "description": "Triggered when an error occurs",
                "icon": "⚠️"
            },
            {
                "name": "feedback",
                "description": "Triggered when user provides feedback (thumbs up/down)",
                "icon": "📊"
            },
            {
                "name": "session_created",
                "description": "Triggered when a new chat session is created",
                "icon": "🆕"
            },
            {
                "name": "session_deleted",
                "description": "Triggered when a chat session is deleted",
                "icon": "🗑️"
            }
        ]

    def get_stats(self) -> Dict:
        """
        Get webhook statistics.

        Returns:
            Dictionary with webhook stats
        """
        total = len(self.webhooks)
        enabled = sum(1 for w in self.webhooks.values() if w.get("enabled", False))
        email_webhooks = sum(1 for w in self.webhooks.values() if w.get("type") == "email")

        return {
            "total_webhooks": total,
            "enabled_webhooks": enabled,
            "disabled_webhooks": total - enabled,
            "email_webhooks": email_webhooks,
            "last_updated": max(
                (w.get("updated_at", w.get("created_at", "")) for w in self.webhooks.values()),
                default=None
            ) if self.webhooks else None
        }
