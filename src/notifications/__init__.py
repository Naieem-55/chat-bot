"""Notification system for webhooks and email alerts."""

from .email_notifier import EmailNotifier
from .webhook_manager import WebhookManager

__all__ = ['EmailNotifier', 'WebhookManager']
