"""Email notification system for chatbot events."""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Handles email notifications for chatbot events."""

    def __init__(
        self,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_username: str = "",
        smtp_password: str = "",
        from_email: str = "",
        enabled: bool = False
    ):
        """
        Initialize email notifier.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            smtp_username: SMTP username
            smtp_password: SMTP password
            from_email: Sender email address
            enabled: Whether email notifications are enabled
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email or smtp_username
        self.enabled = enabled

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        Send an email notification.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            html: Whether body is HTML

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Email notifications disabled, skipping email")
            return False

        if not all([self.smtp_username, self.smtp_password, to_email]):
            logger.warning("Email configuration incomplete, cannot send email")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"✓ Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed - check username/password")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def notify_new_message(
        self,
        to_email: str,
        session_id: str,
        user_message: str,
        bot_response: str
    ) -> bool:
        """
        Send notification for new chat message.

        Args:
            to_email: Recipient email
            session_id: Chat session ID
            user_message: User's message
            bot_response: Bot's response

        Returns:
            True if sent successfully
        """
        subject = "💬 New Chat Message - AI Chatbot"

        body = f"""
New message received in your chatbot:

Session ID: {session_id}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

User Message:
{user_message}

Bot Response:
{bot_response[:200]}{'...' if len(bot_response) > 200 else ''}

---
This is an automated notification from your AI Chatbot.
        """

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #3498db; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .message-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }}
        .footer {{ color: #999; font-size: 12px; margin-top: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>💬 New Chat Message</h2>
        </div>
        <div class="content">
            <p><strong>Session ID:</strong> {session_id}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="message-box">
                <h4>User Message:</h4>
                <p>{user_message}</p>
            </div>

            <div class="message-box">
                <h4>Bot Response:</h4>
                <p>{bot_response[:200]}{'...' if len(bot_response) > 200 else ''}</p>
            </div>
        </div>
        <div class="footer">
            <p>This is an automated notification from your AI Chatbot</p>
        </div>
    </div>
</body>
</html>
        """

        return self.send_email(to_email, subject, html_body, html=True)

    def notify_error(
        self,
        to_email: str,
        error_type: str,
        error_message: str,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Send notification for errors.

        Args:
            to_email: Recipient email
            error_type: Type of error
            error_message: Error details
            session_id: Optional session ID

        Returns:
            True if sent successfully
        """
        subject = f"⚠️ Chatbot Error: {error_type}"

        session_info = f"\nSession ID: {session_id}" if session_id else ""

        body = f"""
An error occurred in your chatbot:

Error Type: {error_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{session_info}

Error Details:
{error_message}

---
This is an automated error notification from your AI Chatbot.
        """

        return self.send_email(to_email, subject, body, html=False)

    def notify_feedback(
        self,
        to_email: str,
        session_id: str,
        message_id: str,
        feedback_type: str,
        query: str
    ) -> bool:
        """
        Send notification for user feedback.

        Args:
            to_email: Recipient email
            session_id: Session ID
            message_id: Message ID
            feedback_type: thumbs_up or thumbs_down
            query: User's query

        Returns:
            True if sent successfully
        """
        emoji = "👍" if feedback_type == "thumbs_up" else "👎"
        subject = f"{emoji} User Feedback - AI Chatbot"

        body = f"""
User provided feedback on a response:

Feedback: {emoji} {feedback_type.replace('_', ' ').title()}
Session ID: {session_id}
Message ID: {message_id}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

User Query:
{query}

---
This is an automated notification from your AI Chatbot.
        """

        return self.send_email(to_email, subject, body, html=False)

    def test_connection(self, to_email: str) -> Dict[str, any]:
        """
        Test email configuration by sending a test email.

        Args:
            to_email: Email address to send test to

        Returns:
            Dictionary with success status and message
        """
        subject = "✅ Test Email - AI Chatbot Notifications"
        body = f"""
This is a test email from your AI Chatbot notification system.

Configuration:
- SMTP Server: {self.smtp_server}:{self.smtp_port}
- From Email: {self.from_email}
- To Email: {to_email}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you received this email, your email notifications are working correctly! 🎉

---
AI Chatbot Notification System
        """

        success = self.send_email(to_email, subject, body, html=False)

        return {
            "success": success,
            "message": "Test email sent successfully" if success else "Failed to send test email",
            "timestamp": datetime.now().isoformat()
        }
