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
function addBotMessage(message, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.textContent = message;

    // Add sources if available
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'message-sources';
        sourcesDiv.innerHTML = '<strong>Sources:</strong><br>';

        sources.forEach(source => {
            const badge = document.createElement('span');
            badge.className = 'source-badge';
            badge.textContent = source.category || source.source;
            sourcesDiv.appendChild(badge);
        });

        messageDiv.appendChild(sourcesDiv);
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

        // Remove loading and add bot response
        removeLoading();
        addBotMessage(data.response, data.sources);

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
