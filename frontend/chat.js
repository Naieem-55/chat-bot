// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State management
let sessionId = null;

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loadingTemplate = document.getElementById('loadingTemplate');

// Initialize
async function initialize() {
    try {
        // Create a new session
        const response = await fetch(`${API_BASE_URL}/session/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        sessionId = data.session_id;
        console.log('Session created:', sessionId);

        // Add welcome message
        addBotMessage('Hello! I\'m your customer support assistant. How can I help you today?');

    } catch (error) {
        console.error('Failed to initialize:', error);
        addBotMessage('Sorry, I\'m having trouble connecting. Please refresh the page.');
    }
}

// Add user message to chat
function addUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(message, sources = null, messageId = null, messageData = null, hallucinationRisk = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.textContent = message;

    // Add hallucination warning if detected
    if (hallucinationRisk && hallucinationRisk.detected) {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'hallucination-warning';
        warningDiv.innerHTML = `
            ⚠️ <strong>${hallucinationRisk.risk_level}</strong> of Hallucination
            <small>(Confidence: ${(hallucinationRisk.confidence_score * 100).toFixed(0)}%)</small>
        `;
        messageDiv.insertBefore(warningDiv, messageDiv.firstChild);
    }

    // Add sources if available
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'message-sources';
        sourcesDiv.innerHTML = '<strong>Sources:</strong><br>';

        sources.forEach(source => {
            const badge = document.createElement('span');
            badge.className = 'source-badge';
            badge.textContent = source.category || source.source;
            badge.title = `Relevance: ${(source.relevance_score * 100).toFixed(0)}%`;
            sourcesDiv.appendChild(badge);
        });

        messageDiv.appendChild(sourcesDiv);
    }

    // Add feedback buttons if messageId is provided
    if (messageId && messageData) {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'feedback-buttons';
        feedbackDiv.innerHTML = `
            <button class="feedback-btn thumbs-up" data-message-id="${messageId}" data-feedback="positive" title="Helpful response">
                👍
            </button>
            <button class="feedback-btn thumbs-down" data-message-id="${messageId}" data-feedback="negative" title="Not helpful">
                👎
            </button>
        `;

        // Add click handlers
        feedbackDiv.querySelectorAll('.feedback-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const feedback = e.target.dataset.feedback;
                const msgId = e.target.dataset.messageId;
                await submitFeedback(msgId, feedback, messageData);

                // Visual feedback
                feedbackDiv.querySelectorAll('.feedback-btn').forEach(b => b.classList.remove('selected'));
                e.target.classList.add('selected');
                e.target.disabled = true;
            });
        });

        messageDiv.appendChild(feedbackDiv);
    }

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Show loading indicator
function showLoading() {
    const loadingEl = loadingTemplate.content.cloneNode(true);
    chatMessages.appendChild(loadingEl);
    scrollToBottom();
}

// Remove loading indicator
function removeLoading() {
    const loading = chatMessages.querySelector('.loading');
    if (loading) {
        loading.remove();
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Submit feedback
async function submitFeedback(messageId, feedback, messageData) {
    try {
        const response = await fetch(`${API_BASE_URL}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message_id: messageId,
                session_id: messageData.session_id,
                user_query: messageData.user_query,
                bot_response: messageData.response,
                feedback: feedback,
                sources: messageData.sources,
                context_used: messageData.context_used
            })
        });

        if (response.ok) {
            console.log('Feedback submitted successfully');
        } else {
            console.error('Failed to submit feedback');
        }
    } catch (error) {
        console.error('Error submitting feedback:', error);
    }
}

// Send message to API
async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) return;

    // Disable input
    messageInput.disabled = true;
    sendButton.disabled = true;

    // Add user message to chat
    addUserMessage(message);
    messageInput.value = '';

    // Show loading
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                stream: false
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Remove loading and add bot response with feedback buttons
        removeLoading();

        // Prepare message data for feedback
        const messageData = {
            user_query: message,
            response: data.response,
            session_id: data.session_id,
            sources: data.sources,
            context_used: data.context_used
        };

        addBotMessage(
            data.response,
            data.sources,
            data.message_id,
            messageData,
            data.hallucination_risk
        );

    } catch (error) {
        console.error('Error sending message:', error);
        removeLoading();

        // Show more detailed error message
        let errorMessage = 'Sorry, I encountered an error. Please try again.';
        if (error.message) {
            errorMessage += ` (${error.message})`;
            console.error('Error details:', error);
        }

        addBotMessage(errorMessage);
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Initialize on page load
window.addEventListener('DOMContentLoaded', initialize);
