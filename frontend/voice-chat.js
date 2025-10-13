/**
 * Full Duplex Voice Chat System
 * Supports simultaneous listening and speaking
 */

class VoiceChatManager {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isSpeaking = false;
        this.isVoiceModeActive = false;
        this.currentUtterance = null;
        this.interimTranscript = '';
        this.finalTranscript = '';
        this.voiceEnabled = false;
        this.autoListen = true; // Continue listening after AI responds

        this.initSpeechRecognition();
        this.setupEventListeners();
    }

    initSpeechRecognition() {
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.error('Speech Recognition not supported');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true; // Keep listening
        this.recognition.interimResults = true; // Show interim results
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;

        // Recognition event handlers
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateVoiceUI('listening');
            console.log('🎤 Voice recognition started');
        };

        this.recognition.onresult = (event) => {
            this.interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;

                if (event.results[i].isFinal) {
                    this.finalTranscript += transcript + ' ';
                    this.handleFinalTranscript(transcript);
                } else {
                    this.interimTranscript += transcript;
                    this.updateInterimTranscript(this.interimTranscript);
                }
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);

            if (event.error === 'no-speech') {
                // No speech detected, restart if in voice mode
                if (this.isVoiceModeActive && this.autoListen) {
                    setTimeout(() => this.startListening(), 1000);
                }
            } else if (event.error === 'aborted') {
                // Aborted by user interruption (speaking while listening)
                console.log('Recognition aborted - likely due to interruption');
            }
        };

        this.recognition.onend = () => {
            this.isListening = false;

            // Restart listening if voice mode is active and we should auto-listen
            if (this.isVoiceModeActive && this.autoListen && !this.isSpeaking) {
                setTimeout(() => this.startListening(), 500);
            } else {
                this.updateVoiceUI('idle');
            }
        };
    }

    setupEventListeners() {
        // Voice mode toggle button
        const voiceModeBtn = document.getElementById('voiceModeBtn');
        if (voiceModeBtn) {
            voiceModeBtn.addEventListener('click', () => this.toggleVoiceMode());
        }

        // Stop speaking button
        const stopSpeakingBtn = document.getElementById('stopSpeakingBtn');
        if (stopSpeakingBtn) {
            stopSpeakingBtn.addEventListener('click', () => this.stopSpeaking());
        }

        // Push to talk button
        const pushToTalkBtn = document.getElementById('pushToTalkBtn');
        if (pushToTalkBtn) {
            pushToTalkBtn.addEventListener('mousedown', () => this.startListening());
            pushToTalkBtn.addEventListener('mouseup', () => this.stopListening());
            pushToTalkBtn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.startListening();
            });
            pushToTalkBtn.addEventListener('touchend', (e) => {
                e.preventDefault();
                this.stopListening();
            });
        }

        // Listen to speech synthesis events
        if (this.synthesis) {
            // Note: synthesis events are on individual utterances, not the synthesis object
        }
    }

    toggleVoiceMode() {
        if (this.isVoiceModeActive) {
            this.deactivateVoiceMode();
        } else {
            this.activateVoiceMode();
        }
    }

    activateVoiceMode() {
        this.isVoiceModeActive = true;
        this.voiceEnabled = true;
        this.autoListen = true;
        this.startListening();

        // Show voice chat modal
        const modal = document.getElementById('voiceChatModal');
        if (modal) {
            modal.style.display = 'flex';
        }

        // Update button state
        const btn = document.getElementById('voiceModeBtn');
        if (btn) {
            btn.classList.add('active');
            const textEl = btn.querySelector('.voice-mode-text');
            if (textEl) {
                textEl.textContent = 'Voice Mode: ON';
            }
        }

        // Update floating voice button
        const floatingBtn = document.getElementById('floatingVoiceBtn');
        if (floatingBtn) {
            floatingBtn.classList.add('active');
        }

        console.log('✓ Voice mode activated');
    }

    deactivateVoiceMode() {
        this.isVoiceModeActive = false;
        this.voiceEnabled = false;
        this.autoListen = false;
        this.stopListening();
        this.stopSpeaking();

        // Hide voice chat modal
        const modal = document.getElementById('voiceChatModal');
        if (modal) {
            modal.style.display = 'none';
        }

        // Update button state
        const btn = document.getElementById('voiceModeBtn');
        if (btn) {
            btn.classList.remove('active');
            const textEl = btn.querySelector('.voice-mode-text');
            if (textEl) {
                textEl.textContent = 'Voice Mode: OFF';
            }
        }

        // Update floating voice button
        const floatingBtn = document.getElementById('floatingVoiceBtn');
        if (floatingBtn) {
            floatingBtn.classList.remove('active');
        }

        console.log('✓ Voice mode deactivated');
    }

    startListening() {
        if (!this.recognition) {
            alert('Speech recognition not supported in your browser');
            return;
        }

        if (this.isListening) return;

        try {
            this.finalTranscript = '';
            this.interimTranscript = '';
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
        }
    }

    stopListening() {
        if (!this.recognition || !this.isListening) return;

        try {
            this.recognition.stop();
        } catch (error) {
            console.error('Error stopping recognition:', error);
        }
    }

    handleFinalTranscript(transcript) {
        transcript = transcript.trim();

        if (!transcript) return;

        console.log('📝 Final transcript:', transcript);

        // Update UI with final transcript
        this.updateFinalTranscript(transcript);

        // Send to chatbot
        this.sendMessageToBot(transcript);

        // Clear transcripts
        this.interimTranscript = '';
        this.finalTranscript = '';
    }

    updateInterimTranscript(text) {
        const element = document.getElementById('interimTranscript');
        if (element) {
            element.textContent = text;
        }
    }

    updateFinalTranscript(text) {
        const element = document.getElementById('userTranscript');
        if (element) {
            element.textContent = text;
        }
    }

    async sendMessageToBot(message) {
        try {
            this.updateVoiceUI('processing');

            // Get current session ID from the main chat
            const sessionId = window.currentSessionId || null;

            // Send message to backend
            const response = await fetch('http://localhost:8002/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId,
                    stream: false
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get response from bot');
            }

            const data = await response.json();

            // Update session ID if new
            if (data.session_id && !window.currentSessionId) {
                window.currentSessionId = data.session_id;
            }

            // Update UI with bot response
            this.updateBotResponse(data.response);

            // Speak the response
            if (this.voiceEnabled) {
                this.speak(data.response);
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.updateVoiceUI('error');

            if (this.voiceEnabled) {
                this.speak('Sorry, I encountered an error processing your request.');
            }
        }
    }

    updateBotResponse(text) {
        const element = document.getElementById('botResponse');
        if (element) {
            element.textContent = text;
        }
    }

    speak(text) {
        // Stop any ongoing speech first
        this.stopSpeaking();

        if (!this.synthesis) {
            console.error('Speech synthesis not supported');
            return;
        }

        // Create utterance
        this.currentUtterance = new SpeechSynthesisUtterance(text);

        // Configure voice
        const voices = this.synthesis.getVoices();
        const preferredVoice = voices.find(v =>
            v.lang.startsWith('en') && v.name.includes('Google')
        ) || voices.find(v => v.lang.startsWith('en'));

        if (preferredVoice) {
            this.currentUtterance.voice = preferredVoice;
        }

        this.currentUtterance.rate = 1.1; // Slightly faster
        this.currentUtterance.pitch = 1.0;
        this.currentUtterance.volume = 1.0;

        // Event handlers
        this.currentUtterance.onstart = () => {
            this.isSpeaking = true;
            this.updateVoiceUI('speaking');
            console.log('🔊 AI speaking...');
        };

        this.currentUtterance.onend = () => {
            this.isSpeaking = false;

            // Resume listening after AI finishes speaking
            if (this.isVoiceModeActive && this.autoListen) {
                setTimeout(() => {
                    this.updateVoiceUI('listening');
                    this.startListening();
                }, 500);
            } else {
                this.updateVoiceUI('idle');
            }

            console.log('✓ AI finished speaking');
        };

        this.currentUtterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            this.isSpeaking = false;
            this.updateVoiceUI('error');
        };

        // Speak
        this.synthesis.speak(this.currentUtterance);
    }

    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel(); // Stop all speech
        }

        this.isSpeaking = false;
        this.currentUtterance = null;

        // Resume listening if in voice mode
        if (this.isVoiceModeActive && !this.isListening) {
            this.startListening();
        }
    }

    updateVoiceUI(state) {
        const statusElement = document.getElementById('voiceStatusIndicator');
        const statusText = document.getElementById('voiceStatusText');

        if (!statusElement || !statusText) return;

        // Remove all state classes
        statusElement.classList.remove('listening', 'speaking', 'processing', 'idle', 'error');

        // Add current state class
        statusElement.classList.add(state);

        // Update text
        const stateTexts = {
            'idle': 'Ready - Say something...',
            'listening': 'Listening...',
            'processing': 'Processing...',
            'speaking': 'AI Speaking...',
            'error': 'Error occurred'
        };

        statusText.textContent = stateTexts[state] || 'Ready';

        // Update visual indicator
        const visualIndicator = document.getElementById('voiceVisualIndicator');
        if (visualIndicator) {
            if (state === 'listening') {
                visualIndicator.classList.add('active');
            } else if (state === 'speaking') {
                visualIndicator.classList.add('speaking');
                visualIndicator.classList.remove('active');
            } else {
                visualIndicator.classList.remove('active', 'speaking');
            }
        }
    }
}

// Initialize voice chat manager
let voiceChatManager;

document.addEventListener('DOMContentLoaded', () => {
    voiceChatManager = new VoiceChatManager();
    console.log('✓ Voice Chat Manager initialized');
});
