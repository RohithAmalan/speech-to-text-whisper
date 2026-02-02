const recordBtn = document.getElementById('recordBtn');
const statusText = document.getElementById('status');
const chatHistory = document.getElementById('chatHistory');
const micRings = document.querySelectorAll('.mic-ring');

let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let isProcessing = false;
let isPlaying = false;
let currentAudio = null;
let abortController = null;

// Initialize Audio Context (for autoplay policies generally, but here we just need recorder)
if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Microphone access is not supported in this browser.");
}

async function startRecording() {
    // Interruption Logic: Stop everything if we start recording
    stopAudio();
    cancelProcessing();

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = sendAudio;

        mediaRecorder.start();
        isRecording = true;
        updateUI('recording');
        audioChunks = [];
    } catch (err) {
        console.error("Error accessing microphone:", err);
        alert("Could not access microphone.");
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;

        // Don't mark as processing if we just cancelled it basically, 
        // but here standard stop means we want to process.
        isProcessing = true;
        updateUI('processing');

        // Stop all tracks to release mic
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
}

function stopAudio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    isPlaying = false;
}

function cancelProcessing() {
    if (abortController) {
        abortController.abort();
        abortController = null;
    }
    isProcessing = false;
}

async function sendAudio() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");

    // Create a new controller for this request
    abortController = new AbortController();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            body: formData,
            signal: abortController.signal
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        handleResponse(data);

    } catch (error) {
        if (error.name === 'AbortError') {
            console.log("Request cancelled by user");
        } else {
            console.error("Error:", error);
            addMessage("Error communicating with server.", "ai");
        }
    } finally {
        // Only reset UI if we weren't just interrupted (recording check handles that state)
        if (!isRecording && !isPlaying) {
            // If we finished normally or errored, go to idle. 
            // If we aborted because we started recording, startRecording handles UI.
            // We need to check if we are truly idle.
            if (!abortController || abortController.signal.aborted) {
                // Aborted request means we probably moved to another state, do nothing here
            } else {
                isProcessing = false;
                updateUI('idle');
            }
        }
    }
}

function handleResponse(data) {
    // Add User Message
    if (data.user_text) {
        addMessage(data.user_text, 'user');
    }

    // Add AI Message
    if (data.ai_text) {
        addMessage(data.ai_text, 'ai');
    }

    // Play Audio
    if (data.audio_url) {
        stopAudio(); // Ensure no overlap
        currentAudio = new Audio(data.audio_url);
        isPlaying = true;
        updateUI('playing');

        currentAudio.onended = () => {
            isPlaying = false;
            currentAudio = null;
            updateUI('idle');
        };

        currentAudio.play().catch(e => console.error("Autoplay failed:", e));
    } else {
        updateUI('idle');
    }
}

function addMessage(text, role) {
    const div = document.createElement('div');
    div.classList.add('message', role);
    chatHistory.appendChild(div);

    if (role === 'ai') {
        // Typewriter effect for AI
        let i = 0;
        const speed = 30; // ms per char

        function typeWriter() {
            if (i < text.length) {
                div.textContent += text.charAt(i);
                i++;
                chatHistory.scrollTop = chatHistory.scrollHeight; // Auto-scroll
                setTimeout(typeWriter, speed);
            }
        }
        typeWriter();
    } else {
        // Instant for user
        div.textContent = text;
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

function updateUI(state) {
    recordBtn.classList.remove('recording', 'processing', 'playing');
    recordBtn.disabled = false; // Always enabled for interruption

    // Reset animations
    micRings.forEach(ring => ring.style.animation = 'none');

    if (state === 'idle') {
        statusText.textContent = "Tap to Speak";
    } else if (state === 'recording') {
        statusText.textContent = "Listening...";
        recordBtn.classList.add('recording');
        micRings.forEach(ring => ring.style.animation = 'pulse-ring 2s infinite');
    } else if (state === 'processing') {
        statusText.textContent = "Thinking...";
        recordBtn.classList.add('processing');
    } else if (state === 'playing') {
        statusText.textContent = "Speaking... (Tap to Interrupt)";
        recordBtn.classList.add('playing');
        micRings.forEach(ring => ring.style.animation = 'pulse-ring-green 2s infinite');
    }
}

// Button Handler
recordBtn.addEventListener('click', () => {
    // Logic Table:
    // If Recording -> Stop Recording (Process)
    // If Processing -> Cancel & Start Recording
    // If Playing -> Stop Audio & Start Recording
    // If Idle -> Start Recording

    if (isRecording) {
        stopRecording();
    } else {
        // Interruption / Start
        // If we are playing or processing, this acts as a hard reset + start
        if (isPlaying) stopAudio();
        if (isProcessing) cancelProcessing();

        startRecording();
    }
});
