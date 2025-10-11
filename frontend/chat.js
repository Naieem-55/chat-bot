// Configuration
const API_BASE_URL = 'http://localhost:8002';

// State management
let sessionId = null;

// DOM elements (initialized after DOM loads)
let chatMessages;
let messageInput;
let sendButton;
let loadingTemplate;

// Initialize
function initialize() {
    console.log('✅ Initialize function called');

    // Get DOM elements (now that DOM is loaded)
    chatMessages = document.getElementById('chatMessages');
    messageInput = document.getElementById('messageInput');
    sendButton = document.getElementById('sendButton');
    loadingTemplate = document.getElementById('loadingTemplate');

    console.log('✅ Elements found:', {
        chatMessages: !!chatMessages,
        messageInput: !!messageInput,
        sendButton: !!sendButton,
        loadingTemplate: !!loadingTemplate
    });

    if (!messageInput || !sendButton || !chatMessages) {
        console.error('❌ Required elements not found!');
        return;
    }

    // Setup event listeners FIRST (synchronously)
    sendButton.addEventListener('click', () => {
        console.log('🖱️ Send button clicked!');
        sendMessage();
    });

    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            console.log('⌨️ Enter key pressed!');
            const autocompleteDropdown = document.getElementById('autocompleteDropdown');
            if (!autocompleteDropdown || autocompleteDropdown.style.display === 'none') {
                e.preventDefault();
                sendMessage();
            }
        }
    });

    console.log('✅ Event listeners attached');

    // Initialize session asynchronously (don't await, let it run in background)
    initializeSession();
}

// Separate async function for session initialization
async function initializeSession() {
    try {
        // Check if we have a saved session in localStorage
        const savedSessionId = localStorage.getItem('currentSessionId');

        if (savedSessionId) {
            // Try to load the saved session
            try {
                const historyResponse = await fetch(`${API_BASE_URL}/session/${savedSessionId}/history`);
                if (historyResponse.ok) {
                    const data = await historyResponse.json();
                    sessionId = savedSessionId;
                    console.log('✅ Restored session from localStorage:', sessionId);

                    // Load chat history
                    if (data.history && data.history.length > 0) {
                        data.history.forEach(msg => {
                            if (msg.role === 'user') {
                                addUserMessage(msg.content);
                            } else if (msg.role === 'assistant') {
                                addBotMessage(msg.content);
                            }
                        });
                    } else {
                        addBotMessage('Hello! I\'m your AI assistant. How can I help you today?');
                    }

                    // Load suggestions (from suggestions.js)
                    if (typeof loadSuggestedQuestions !== 'undefined') {
                        await loadSuggestedQuestions();
                    }

                    // Setup autocomplete (from suggestions.js)
                    if (typeof setupAutocomplete !== 'undefined') {
                        setupAutocomplete();
                    }

                    return; // Successfully restored session
                }
            } catch (err) {
                console.log('⚠️ Failed to restore saved session, creating new one');
                localStorage.removeItem('currentSessionId');
            }
        }

        // Create a new session
        const response = await fetch(`${API_BASE_URL}/session/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        sessionId = data.session_id;

        // Save to localStorage
        localStorage.setItem('currentSessionId', sessionId);
        console.log('✅ Session created:', sessionId);

        // Add welcome message
        addBotMessage('Hello! I\'m your AI assistant. How can I help you today?');

        // Load suggestions (from suggestions.js)
        if (typeof loadSuggestedQuestions !== 'undefined') {
            await loadSuggestedQuestions();
        }

        // Setup autocomplete (from suggestions.js)
        if (typeof setupAutocomplete !== 'undefined') {
            setupAutocomplete();
        }

    } catch (error) {
        console.error('❌ Failed to initialize session:', error);
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

// Add bot message to chat (with streaming support)
function addBotMessage(message, sources = null, messageId = null, messageData = null, hallucinationRisk = null, reformulatedQuery = null, streaming = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (!streaming) {
        // Format message with paragraphs and markdown-like formatting
        contentDiv.innerHTML = formatMessage(message);
    }

    messageDiv.appendChild(contentDiv);

    // Add query reformulation notice if query was reformulated
    if (reformulatedQuery) {
        const reformulationDiv = document.createElement('div');
        reformulationDiv.className = 'reformulation-notice';
        reformulationDiv.innerHTML = `
            🔄 <small>Interpreted as: "${reformulatedQuery}"</small>
        `;
        messageDiv.insertBefore(reformulationDiv, messageDiv.firstChild);
    }

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

    // Add sources if available (with emojis and better formatting)
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'message-sources';
        sourcesDiv.innerHTML = '<div class="sources-header">📚 <strong>Sources:</strong></div>';

        const sourcesListDiv = document.createElement('div');
        sourcesListDiv.className = 'sources-list';

        // Group sources and remove duplicates
        const uniqueSources = [];
        const seenSources = new Set();

        sources.forEach(source => {
            const key = `${source.source}-${source.category || ''}`;
            if (!seenSources.has(key)) {
                seenSources.add(key);
                uniqueSources.push(source);
            }
        });

        uniqueSources.slice(0, 5).forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';

            const emoji = getSourceEmoji(source.source, source.category);
            const relevance = Math.round(source.relevance_score * 100);
            const sourceName = source.category || extractFilename(source.source);

            sourceItem.innerHTML = `
                <span class="source-emoji">${emoji}</span>
                <span class="source-name">${sourceName}</span>
                <span class="source-relevance" title="Relevance score">${relevance}%</span>
            `;

            sourcesListDiv.appendChild(sourceItem);
        });

        sourcesDiv.appendChild(sourcesListDiv);
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

// Get emoji for source based on category or filename
function getSourceEmoji(source, category) {
    if (category) {
        const categoryLower = category.toLowerCase();
        if (categoryLower.includes('payment')) return '💳';
        if (categoryLower.includes('ship')) return '📦';
        if (categoryLower.includes('return')) return '↩️';
        if (categoryLower.includes('order')) return '🛒';
        if (categoryLower.includes('account')) return '👤';
    }

    // Check for URLs first
    if (source.startsWith('http://') || source.startsWith('https://')) {
        if (source.includes('w3schools')) return '📚';
        if (source.includes('github')) return '💻';
        if (source.includes('stackoverflow')) return '💬';
        if (source.includes('docs.') || source.includes('documentation')) return '📖';
        return '🌐'; // Generic web link
    }

    // Check file extensions
    if (source.includes('.pdf')) return '📄';
    if (source.includes('.txt')) return '📝';
    if (source.includes('.html')) return '📝';
    if (source.includes('.md')) return '📝';
    if (source.includes('faq')) return '❓';
    if (source.includes('api')) return '⚙️';
    if (source.includes('mediaconvert')) return '🎬';

    return '📌';
}

// Extract filename from path or URL
function extractFilename(path) {
    if (!path) return 'Document';

    // Handle URLs
    if (path.startsWith('http://') || path.startsWith('https://')) {
        try {
            const url = new URL(path);
            // Get the last part of the pathname
            const pathParts = url.pathname.split('/').filter(p => p);
            if (pathParts.length > 0) {
                const lastPart = pathParts[pathParts.length - 1];
                // Remove file extension and format nicely
                return lastPart
                    .replace(/\.[^/.]+$/, '')
                    .replace(/[-_]/g, ' ')
                    .replace(/\.html?$/i, '')
                    .trim();
            }
            return url.hostname.replace('www.', '');
        } catch (e) {
            return 'Web Page';
        }
    }

    // Handle file paths
    const parts = path.split(/[\\/]/);
    const filename = parts[parts.length - 1];
    return filename.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
}

// Format message with paragraphs, lists, headings, code blocks
function formatMessage(text) {
    if (!text) return '';

    // Step 1: Extract code blocks first (```language\ncode\n```)
    const codeBlocks = [];
    const codeBlockPlaceholder = '___CODE_BLOCK___';

    text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, language, code) => {
        const blockId = codeBlocks.length;
        codeBlocks.push({
            language: language || 'text',
            code: code.trim()
        });
        return `${codeBlockPlaceholder}${blockId}${codeBlockPlaceholder}`;
    });

    // Step 2: Handle inline code (`code`)
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Step 3: Clean up extra whitespace
    text = text.replace(/\n\n\s+\n/g, '\n\n');
    text = text.replace(/\n{3,}/g, '\n\n');

    // Step 4: Split into paragraphs
    let paragraphs = text.split('\n\n');

    // Step 5: Format each paragraph
    paragraphs = paragraphs.map(p => {
        p = p.trim();
        if (!p) return '';

        // Check if this is a code block placeholder
        const codeBlockMatch = p.match(/___CODE_BLOCK___(\d+)___CODE_BLOCK___/);
        if (codeBlockMatch) {
            const blockIndex = parseInt(codeBlockMatch[1]);
            const block = codeBlocks[blockIndex];
            return createCodeBlock(block.language, block.code);
        }

        // Handle headings
        if (p.startsWith('###')) {
            const lines = p.split('\n');
            const heading = lines[0];
            const rest = lines.slice(1).join('\n').trim();
            let result = `<h4 class="response-heading">${heading.substring(3).trim()}</h4>`;
            if (rest) result += `<p>${rest}</p>`;
            return result;
        }
        if (p.startsWith('##')) {
            const lines = p.split('\n');
            const heading = lines[0];
            const rest = lines.slice(1).join('\n').trim();
            let result = `<h3 class="response-heading">${heading.substring(2).trim()}</h3>`;
            if (rest) {
                if (rest.includes('\n*') || rest.startsWith('*')) {
                    const restLines = rest.split('\n');
                    const listItems = restLines
                        .filter(line => line.trim().startsWith('*'))
                        .map(line => `<li>${line.trim().substring(1).trim()}</li>`)
                        .join('');
                    if (listItems) result += `<ul class="formatted-list">${listItems}</ul>`;
                } else {
                    result += `<p>${rest}</p>`;
                }
            }
            return result;
        }

        // Handle bold text
        p = p.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Handle numbered lists
        if (p.includes('\n1.') || p.startsWith('1.')) {
            const lines = p.split('\n');
            const listItems = [];
            let regularText = '';

            lines.forEach(line => {
                line = line.trim();
                const numberedMatch = line.match(/^(\d+)\.\s+(.+)/);
                if (numberedMatch) {
                    if (regularText) {
                        listItems.push(`<p>${regularText}</p>`);
                        regularText = '';
                    }
                    listItems.push(`<li>${numberedMatch[2]}</li>`);
                } else if (line) {
                    regularText += (regularText ? ' ' : '') + line;
                }
            });

            if (regularText) listItems.push(`<p>${regularText}</p>`);
            const listContent = listItems.filter(item => item.startsWith('<li>')).join('');
            const textContent = listItems.filter(item => item.startsWith('<p>')).join('');
            if (listContent) return textContent + `<ol class="formatted-list">${listContent}</ol>`;
            return textContent;
        }

        // Handle bullet points
        if (p.includes('\n*') || p.includes('\n-') || p.startsWith('*') || p.startsWith('-')) {
            const lines = p.split('\n');
            const listItems = [];
            let regularText = '';

            lines.forEach(line => {
                line = line.trim();
                if (line.startsWith('*') || line.startsWith('-')) {
                    if (regularText) {
                        listItems.push(`<p>${regularText}</p>`);
                        regularText = '';
                    }
                    let itemText = line.substring(1).trim();
                    itemText = itemText.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
                    listItems.push(`<li>${itemText}</li>`);
                } else if (line) {
                    regularText += (regularText ? ' ' : '') + line;
                }
            });

            if (regularText) listItems.push(`<p>${regularText}</p>`);
            const listContent = listItems.filter(item => item.startsWith('<li>')).join('');
            const textContent = listItems.filter(item => item.startsWith('<p>')).join('');
            if (listContent) return textContent + `<ul class="formatted-list">${listContent}</ul>`;
            return textContent;
        }

        // Regular paragraph
        return `<p>${p}</p>`;
    });

    return paragraphs.join('');
}

// Create a code block with syntax highlighting and copy button
function createCodeBlock(language, code) {
    const escapedCode = code
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    const blockId = 'code-' + Math.random().toString(36).substr(2, 9);

    return `
        <div class="code-block-wrapper">
            <div class="code-block-header">
                <span class="code-language">${language}</span>
                <button class="code-copy-btn" onclick="copyCode('${blockId}')">
                    <span>Copy code</span>
                </button>
            </div>
            <div class="code-block-content">
                <pre><code id="${blockId}">${escapedCode}</code></pre>
            </div>
        </div>
    `;
}

// Copy code to clipboard
function copyCode(blockId) {
    const codeElement = document.getElementById(blockId);
    if (!codeElement) return;

    const code = codeElement.textContent;
    navigator.clipboard.writeText(code).then(() => {
        // Find the copy button and update its state
        const codeBlock = codeElement.closest('.code-block-wrapper');
        const btn = codeBlock.querySelector('.code-copy-btn');
        const originalHTML = btn.innerHTML;

        btn.innerHTML = '<span>✓ Copied!</span>';
        btn.classList.add('copied');

        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy code:', err);
    });
}

// Create a streaming bot message element
function createStreamingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message streaming';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<span class="typing-cursor">|</span>';

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    return { messageDiv, contentDiv };
}

// Stream text with typing effect (character by character like ChatGPT)
async function streamText(contentDiv, text, speed = 30) {
    const cursor = contentDiv.querySelector('.typing-cursor');
    if (cursor) cursor.remove();

    let currentText = '';

    // Type character by character for more human-like effect
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        currentText += char;

        // Update display with cursor
        contentDiv.innerHTML = formatMessage(currentText) + '<span class="typing-cursor">|</span>';
        scrollToBottom();

        // Variable speed based on character for human-like typing
        let delay = speed;

        // Longer pauses for natural rhythm
        if (char === '.' || char === '!' || char === '?') {
            delay = speed * 15; // Long pause after sentences (450ms)
        } else if (char === ',' || char === ';') {
            delay = speed * 8; // Medium pause after commas (240ms)
        } else if (char === ':') {
            delay = speed * 6; // Shorter pause after colons (180ms)
        } else if (char === '\n') {
            delay = speed * 10; // Pause at line breaks (300ms)
        } else if (char === ' ') {
            delay = speed * 1.5; // Slightly longer for spaces (45ms)
        } else {
            // Add some randomness for human-like typing (25-35ms)
            delay = speed + (Math.random() * 10 - 5);
        }

        await new Promise(resolve => setTimeout(resolve, delay));
    }

    // Remove cursor after complete
    const finalCursor = contentDiv.querySelector('.typing-cursor');
    if (finalCursor) finalCursor.remove();

    contentDiv.innerHTML = formatMessage(text);
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

// Send message to API with streaming typing effect
async function sendMessage() {
    console.log('🚀 sendMessage() function called');
    console.log('messageInput element:', messageInput);
    console.log('messageInput value:', messageInput ? messageInput.value : 'NULL');

    const message = messageInput.value.trim();
    console.log('Message to send:', message);

    if (!message) {
        console.log('⚠ Empty message, aborting send');
        return;
    }

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

        // Remove loading
        removeLoading();

        // Create streaming message element
        const { messageDiv, contentDiv } = createStreamingMessage();

        // Add reformulation notice if present
        if (data.reformulated_query) {
            const reformulationDiv = document.createElement('div');
            reformulationDiv.className = 'reformulation-notice';
            reformulationDiv.innerHTML = `
                🔄 <small>Interpreted as: "${data.reformulated_query}"</small>
            `;
            messageDiv.insertBefore(reformulationDiv, contentDiv);
        }

        // Stream the response with typing effect (slower for readability)
        await streamText(contentDiv, data.response, 35);

        // Speak the response if voice mode is enabled
        speakText(data.response);

        // Add sources after streaming completes
        if (data.sources && data.sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            sourcesDiv.innerHTML = '<div class="sources-header">📚 <strong>Sources:</strong></div>';

            const sourcesListDiv = document.createElement('div');
            sourcesListDiv.className = 'sources-list';

            // Group sources and remove duplicates
            const uniqueSources = [];
            const seenSources = new Set();

            data.sources.forEach(source => {
                const key = `${source.source}-${source.category || ''}`;
                if (!seenSources.has(key)) {
                    seenSources.add(key);
                    uniqueSources.push(source);
                }
            });

            uniqueSources.slice(0, 5).forEach((source, index) => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';

                const emoji = getSourceEmoji(source.source, source.category);
                const relevance = Math.round(source.relevance_score * 100);

                // Show actual file path/name or category
                let displayName = '';
                let fullPath = '';

                if (source.source.includes('\\') || source.source.includes('/')) {
                    // It's a file path - show full path and extracted name
                    fullPath = source.source;
                    displayName = extractFilename(source.source);
                } else if (source.category) {
                    // It's a category from FAQ
                    displayName = source.category;
                    fullPath = `FAQ - ${source.category}`;
                } else {
                    displayName = source.source;
                    fullPath = source.source;
                }

                sourceItem.innerHTML = `
                    <span class="source-emoji">${emoji}</span>
                    <div class="source-details">
                        <div class="source-name">${displayName}</div>
                        <div class="source-path" title="${fullPath}">${fullPath}</div>
                    </div>
                    <span class="source-relevance" title="Relevance score">${relevance}%</span>
                `;

                sourcesListDiv.appendChild(sourceItem);
            });

            sourcesDiv.appendChild(sourcesListDiv);
            messageDiv.appendChild(sourcesDiv);
        }

        // Add feedback buttons
        if (data.message_id) {
            const messageData = {
                user_query: message,
                response: data.response,
                session_id: data.session_id,
                sources: data.sources,
                context_used: data.context_used
            };

            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'feedback-buttons';
            feedbackDiv.innerHTML = `
                <button class="feedback-btn thumbs-up" data-message-id="${data.message_id}" data-feedback="positive" title="Helpful response">
                    👍
                </button>
                <button class="feedback-btn thumbs-down" data-message-id="${data.message_id}" data-feedback="negative" title="Not helpful">
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

        // Remove streaming class
        messageDiv.classList.remove('streaming');

        // Hide suggested questions after first message
        if (typeof hideSuggestedQuestions !== 'undefined') {
            hideSuggestedQuestions();
        }

        // Show "People Also Asked" or follow-up suggestions
        if (typeof showPeopleAlsoAsked !== 'undefined') {
            await showPeopleAlsoAsked(message, data.response, data.sources);
        }

    } catch (error) {
        console.error('Error sending message:', error);
        removeLoading();

        // Show more detailed error message
        let errorMessage = '❌ Sorry, I encountered an error. Please try again.';
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

// ===== SIDEBAR FUNCTIONALITY =====

// Sidebar state
let sidebarOpen = false;
let currentSessionId = null;
let sessions = [];

// Initialize sidebar
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarClose = document.getElementById('sidebarClose');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const newChatBtn = document.getElementById('newChatBtn');
    const sidebar = document.getElementById('chatSidebar');

    // Toggle button click
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => toggleSidebar());
    }

    // Close button click
    if (sidebarClose) {
        sidebarClose.addEventListener('click', () => closeSidebar());
    }

    // Overlay click (mobile)
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => closeSidebar());
    }

    // New chat button
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => createNewChat());
    }

    // Load sessions from API
    loadSessions();

    console.log('✅ Sidebar initialized');
}

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (sidebarOpen) {
        closeSidebar();
    } else {
        sidebar.classList.add('open');
        overlay.classList.add('active');
        document.body.classList.add('sidebar-open');
        sidebarOpen = true;

        // Reload sessions when opening
        loadSessions();
    }
}

// Close sidebar
function closeSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    const overlay = document.getElementById('sidebarOverlay');

    sidebar.classList.remove('open');
    overlay.classList.remove('active');
    document.body.classList.remove('sidebar-open');
    sidebarOpen = false;
}

// Load sessions from API
async function loadSessions() {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions/list`);
        if (!response.ok) {
            throw new Error('Failed to load sessions');
        }

        const data = await response.json();
        sessions = data.sessions || [];

        renderSessions();
    } catch (error) {
        console.error('Error loading sessions:', error);
        renderEmptyState();
    }
}

// Render sessions list
function renderSessions() {
    const sessionsList = document.getElementById('sessionsList');

    if (!sessionsList) return;

    if (sessions.length === 0) {
        renderEmptyState();
        return;
    }

    sessionsList.innerHTML = '';

    sessions.forEach(session => {
        const sessionItem = createSessionItem(session);
        sessionsList.appendChild(sessionItem);
    });
}

// Create session item element
function createSessionItem(session) {
    const item = document.createElement('div');
    item.className = 'session-item';
    item.dataset.sessionId = session.session_id;

    // Mark active session
    if (session.session_id === sessionId) {
        item.classList.add('active');
    }

    const timeAgo = formatTimeAgo(session.last_active);

    item.innerHTML = `
        <div class="session-title">${session.title}</div>
        <div class="session-metadata">
            <span class="session-time"><i class="far fa-clock"></i> ${timeAgo}</span>
            <span class="session-message-count"><i class="far fa-comments"></i> ${session.message_count}</span>
        </div>
        <button class="session-delete" title="Delete conversation">
            <i class="fas fa-trash-alt"></i>
        </button>
    `;

    // Click to switch session
    item.addEventListener('click', (e) => {
        // Check if click was on delete button or its icon
        if (!e.target.closest('.session-delete')) {
            switchToSession(session.session_id);
        }
    });

    // Delete button
    const deleteBtn = item.querySelector('.session-delete');
    deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteSession(session.session_id);
    });

    return item;
}

// Render empty state
function renderEmptyState() {
    const sessionsList = document.getElementById('sessionsList');

    if (!sessionsList) return;

    sessionsList.innerHTML = `
        <div class="sessions-empty">
            <div class="sessions-empty-icon">
                <i class="far fa-comments"></i>
            </div>
            <div class="sessions-empty-text">No conversations yet.<br>Start a new chat!</div>
        </div>
    `;
}

// Format time ago
function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return time.toLocaleDateString();
}

// Create new chat
async function createNewChat() {
    try {
        // Clear current chat
        chatMessages.innerHTML = '';
        sessionId = null;

        // Remove saved session from localStorage
        localStorage.removeItem('currentSessionId');

        // Create new session
        await initializeSession();

        // Reload sessions list
        await loadSessions();

        // Close sidebar
        closeSidebar();

        console.log('✅ New chat created');
    } catch (error) {
        console.error('Error creating new chat:', error);
        addBotMessage('Sorry, I couldn\'t create a new chat. Please try again.');
    }
}

// Switch to existing session
async function switchToSession(newSessionId) {
    try {
        // Don't switch if already active
        if (newSessionId === sessionId) {
            closeSidebar();
            return;
        }

        // Clear current chat
        chatMessages.innerHTML = '';

        // Load session history
        const response = await fetch(`${API_BASE_URL}/session/${newSessionId}/history`);

        if (!response.ok) {
            throw new Error('Failed to load session history');
        }

        const data = await response.json();
        sessionId = newSessionId;

        // Save to localStorage
        localStorage.setItem('currentSessionId', sessionId);

        // Render chat history
        if (data.history && data.history.length > 0) {
            data.history.forEach(msg => {
                if (msg.role === 'user') {
                    addUserMessage(msg.content);
                } else if (msg.role === 'assistant') {
                    addBotMessage(msg.content);
                }
            });
        } else {
            addBotMessage('Hello! I\'m your AI assistant. How can I help you today?');
        }

        // Update sidebar active state
        document.querySelectorAll('.session-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.sessionId === newSessionId) {
                item.classList.add('active');
            }
        });

        // Close sidebar
        closeSidebar();

        console.log('✅ Switched to session:', newSessionId);
    } catch (error) {
        console.error('Error switching session:', error);
        addBotMessage('Sorry, I couldn\'t load that conversation. Please try again.');
    }
}

// Delete session
async function deleteSession(sessionIdToDelete) {
    // Confirm deletion
    if (!confirm('Delete this conversation? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/session/${sessionIdToDelete}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete session');
        }

        // If deleting current session, create new one
        if (sessionIdToDelete === sessionId) {
            await createNewChat();
        } else {
            // Just reload sessions list
            await loadSessions();
        }

        console.log('✅ Session deleted:', sessionIdToDelete);
    } catch (error) {
        console.error('Error deleting session:', error);
        alert('Sorry, I couldn\'t delete that conversation. Please try again.');
    }
}

// ===== VOICE CHAT FUNCTIONALITY =====

// Voice state
let voiceModeEnabled = false;
let isListening = false;
let recognition = null;
let synthesis = window.speechSynthesis;

// Initialize speech recognition
function initializeVoiceRecognition() {
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn('⚠️ Speech recognition not supported in this browser');
        return false;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        console.log('🎤 Voice recognition started');
        isListening = true;
        updateVoiceUI(true);
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('📝 Transcript:', transcript);

        // Fill input with transcript
        messageInput.value = transcript;

        // Auto-send if voice mode is enabled
        if (voiceModeEnabled) {
            setTimeout(() => sendMessage(), 500);
        }
    };

    recognition.onerror = (event) => {
        console.error('❌ Speech recognition error:', event.error);
        isListening = false;
        updateVoiceUI(false);

        if (event.error === 'not-allowed') {
            alert('Microphone access denied. Please enable microphone permissions in your browser settings.');
        }
    };

    recognition.onend = () => {
        console.log('🎤 Voice recognition ended');
        isListening = false;
        updateVoiceUI(false);
    };

    return true;
}

// Start voice recognition
function startVoiceRecognition() {
    if (!recognition) {
        const initialized = initializeVoiceRecognition();
        if (!initialized) {
            alert('Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }
    }

    if (isListening) {
        recognition.stop();
        return;
    }

    try {
        recognition.start();
    } catch (error) {
        console.error('Error starting recognition:', error);
        if (error.name === 'InvalidStateError') {
            // Recognition is already running, stop it first
            recognition.stop();
            setTimeout(() => recognition.start(), 100);
        }
    }
}

// Update voice UI
function updateVoiceUI(listening) {
    const voiceInputBtn = document.getElementById('voiceInputBtn');
    const voiceStatus = document.getElementById('voiceStatus');

    if (listening) {
        voiceInputBtn.classList.add('listening');
        voiceStatus.style.display = 'block';
    } else {
        voiceInputBtn.classList.remove('listening');
        voiceStatus.style.display = 'none';
    }
}

// Toggle voice mode (auto text-to-speech)
function toggleVoiceMode() {
    voiceModeEnabled = !voiceModeEnabled;

    const voiceToggle = document.getElementById('voiceToggle');
    const voiceIcon = voiceToggle.querySelector('.voice-icon');

    if (voiceModeEnabled) {
        voiceToggle.classList.add('active');
        voiceIcon.className = 'fas fa-volume-up voice-icon';
        document.body.classList.add('voice-mode-active');
        console.log('🔊 Voice mode enabled');
    } else {
        voiceToggle.classList.remove('active');
        voiceIcon.className = 'fas fa-volume-mute voice-icon';
        document.body.classList.remove('voice-mode-active');

        // Stop any ongoing speech
        if (synthesis.speaking) {
            synthesis.cancel();
        }
        console.log('🔇 Voice mode disabled');
    }
}

// Text-to-speech function
function speakText(text) {
    if (!voiceModeEnabled) return;

    // Cancel any ongoing speech
    if (synthesis.speaking) {
        synthesis.cancel();
    }

    // Clean text for speech (remove markdown, code blocks, etc.)
    let cleanText = text
        .replace(/```[\s\S]*?```/g, ' code block ') // Replace code blocks
        .replace(/`[^`]+`/g, ' code ') // Replace inline code
        .replace(/\*\*(.+?)\*\*/g, '$1') // Remove bold
        .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1') // Convert links
        .replace(/#+\s+/g, '') // Remove heading markers
        .replace(/[*_~]/g, '') // Remove other markdown
        .trim();

    // Split into sentences for better pacing
    const sentences = cleanText.match(/[^.!?]+[.!?]+/g) || [cleanText];

    sentences.forEach((sentence, index) => {
        const utterance = new SpeechSynthesisUtterance(sentence.trim());
        utterance.rate = 1.1; // Slightly faster
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Select a good voice (prefer female voice for consistency)
        const voices = synthesis.getVoices();
        const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Microsoft Zira'));
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        if (index === sentences.length - 1) {
            utterance.onend = () => {
                console.log('✅ Speech completed');
            };
        }

        synthesis.speak(utterance);
    });
}

// Initialize voice controls
function initializeVoiceControls() {
    const voiceInputBtn = document.getElementById('voiceInputBtn');
    const voiceToggle = document.getElementById('voiceToggle');

    // Voice input button click
    if (voiceInputBtn) {
        voiceInputBtn.addEventListener('click', () => {
            startVoiceRecognition();
        });
    }

    // Voice mode toggle click
    if (voiceToggle) {
        voiceToggle.addEventListener('click', () => {
            toggleVoiceMode();
        });
    }

    // Load voices (required for some browsers)
    if (synthesis.onvoiceschanged !== undefined) {
        synthesis.onvoiceschanged = () => {
            synthesis.getVoices();
        };
    }

    console.log('✅ Voice controls initialized');
}

// Modify the existing sendMessage to include voice output
const originalSendMessage = sendMessage;

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    initialize();
    initializeSidebar();
    initializeVoiceControls();
});
