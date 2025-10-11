/**
 * Smart suggestions functionality for the chatbot
 * - Suggested questions
 * - Autocomplete
 * - People also asked
 * - Follow-up suggestions
 */

const API_BASE_URL = 'http://localhost:8002';

// Load and display suggested questions
async function loadSuggestedQuestions() {
    try {
        const response = await fetch(`${API_BASE_URL}/suggestions/common-questions?max_questions=8`);
        const data = await response.json();

        const suggestionsList = document.getElementById('suggestionsList');
        suggestionsList.innerHTML = '';

        data.questions.forEach(question => {
            const chip = document.createElement('div');
            chip.className = 'suggestion-chip';
            chip.textContent = question;
            chip.addEventListener('click', () => {
                // Fill input and trigger send
                const input = document.getElementById('messageInput');
                input.value = question;
                // Trigger the send button click
                document.getElementById('sendButton').click();
            });
            suggestionsList.appendChild(chip);
        });

        console.log(`✓ Loaded ${data.count} suggested questions`);
    } catch (error) {
        console.error('Failed to load suggestions:', error);
    }
}

// Setup autocomplete functionality
function setupAutocomplete() {
    const messageInput = document.getElementById('messageInput');
    const autocompleteDropdown = document.getElementById('autocompleteDropdown');
    let debounceTimer;
    let selectedIndex = -1;

    messageInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();

        // Clear previous timer
        clearTimeout(debounceTimer);

        if (query.length < 3) {
            autocompleteDropdown.style.display = 'none';
            return;
        }

        // Debounce autocomplete requests
        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/suggestions/autocomplete`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ partial_query: query })
                });

                const data = await response.json();

                if (data.suggestions.length > 0) {
                    displayAutocomplete(data.suggestions);
                } else {
                    autocompleteDropdown.style.display = 'none';
                }
            } catch (error) {
                console.error('Autocomplete error:', error);
            }
        }, 300); // 300ms debounce
    });

    // Handle arrow keys and enter
    messageInput.addEventListener('keydown', (e) => {
        const items = autocompleteDropdown.querySelectorAll('.autocomplete-item');

        // Only handle keys if autocomplete is visible
        if (items.length === 0 || autocompleteDropdown.style.display === 'none') {
            return; // Let default behavior happen (including Enter for send)
        }

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateSelectedItem(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            updateSelectedItem(items);
        } else if (e.key === 'Enter' && selectedIndex >= 0) {
            e.preventDefault();
            items[selectedIndex].click();
        } else if (e.key === 'Escape') {
            autocompleteDropdown.style.display = 'none';
            selectedIndex = -1;
        }
    });

    // Close autocomplete when clicking outside
    document.addEventListener('click', (e) => {
        if (!messageInput.contains(e.target) && !autocompleteDropdown.contains(e.target)) {
            autocompleteDropdown.style.display = 'none';
            selectedIndex = -1;
        }
    });

    function displayAutocomplete(suggestions) {
        autocompleteDropdown.innerHTML = '';
        selectedIndex = -1;

        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.textContent = suggestion;
            item.addEventListener('click', () => {
                messageInput.value = suggestion;
                autocompleteDropdown.style.display = 'none';
                messageInput.focus();
            });
            autocompleteDropdown.appendChild(item);
        });

        autocompleteDropdown.style.display = 'block';
    }

    function updateSelectedItem(items) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }
}

// Display "People Also Asked" after a response
async function showPeopleAlsoAsked(userQuery, botResponse, sources) {
    try {
        const response = await fetch(`${API_BASE_URL}/suggestions/people-also-asked`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_query: userQuery,
                bot_response: botResponse,
                sources: sources || []
            })
        });

        const data = await response.json();

        if (data.questions.length > 0) {
            const paaContainer = document.getElementById('peopleAlsoAsked');
            const paaList = document.getElementById('paaList');

            paaList.innerHTML = '';

            data.questions.forEach(question => {
                const item = document.createElement('div');
                item.className = 'paa-question';
                item.textContent = question;
                item.addEventListener('click', () => {
                    // Send this question
                    document.getElementById('messageInput').value = question;
                    document.getElementById('sendButton').click();
                    paaContainer.style.display = 'none';
                });
                paaList.appendChild(item);
            });

            paaContainer.style.display = 'block';
            console.log(`✓ Showing ${data.count} related questions`);
        }
    } catch (error) {
        console.error('Failed to load PAA:', error);
    }
}

// Show follow-up suggestions (alternative to PAA)
async function showFollowUpSuggestions(userQuery, botResponse, sources) {
    try {
        const response = await fetch(`${API_BASE_URL}/suggestions/follow-ups`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_query: userQuery,
                bot_response: botResponse,
                sources: sources || []
            })
        });

        const data = await response.json();

        if (data.follow_ups.length > 0) {
            const paaContainer = document.getElementById('peopleAlsoAsked');
            const paaList = document.getElementById('paaList');

            // Change header text
            document.querySelector('.paa-header').textContent = '💡 Follow-up questions:';

            paaList.innerHTML = '';

            data.follow_ups.forEach(question => {
                const item = document.createElement('div');
                item.className = 'paa-question';
                item.textContent = question;
                item.addEventListener('click', () => {
                    document.getElementById('messageInput').value = question;
                    document.getElementById('sendButton').click();
                    paaContainer.style.display = 'none';
                });
                paaList.appendChild(item);
            });

            paaContainer.style.display = 'block';
            console.log(`✓ Showing ${data.count} follow-up suggestions`);
        }
    } catch (error) {
        console.error('Failed to load follow-ups:', error);
    }
}

// Hide suggested questions when user starts chatting
function hideSuggestedQuestions() {
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.classList.add('has-messages');
}

// Export functions for use in chat.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadSuggestedQuestions,
        setupAutocomplete,
        showPeopleAlsoAsked,
        showFollowUpSuggestions,
        hideSuggestedQuestions
    };
}
