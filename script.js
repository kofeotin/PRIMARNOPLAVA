document.addEventListener('DOMContentLoaded', () => {
    const questionSection = document.querySelector('.question-section');
    const overlay = document.getElementById('dreamcore-overlay');
    const form = document.getElementById('answer-form');
    const thankYouMessage = document.getElementById('thank-you-message');
    const nickInput = document.getElementById('nick');
    const answerInput = document.getElementById('odgovor');
    
    // Modal Elements
    const infoBtn = document.getElementById('info-btn');
    const infoModal = document.getElementById('info-modal');
    const closeModal = document.querySelector('.close-btn');

    // List of local images provided by the user for the dreamcore aesthetic
    const dreamcoreImages = [
        'images/273826979_1091748938058565_8085866126482543463_n.jpg',
        'images/278410030_282317670771630_5560655102082590327_n.jpg',
        'images/278957516_109680008302368_7501577799441767931_n.jpg',
        'images/279001323_533665661801742_1328100440464622725_n.jpg',
        'images/282756356_1188623878560971_6143339502946933370_n (1).jpg',
        'images/282756356_1188623878560971_6143339502946933370_n.jpg',
        'images/283067992_1011144446184666_2981869154837335145_n.jpg',
        'images/311199193_204810458649346_9191301265192801948_n.jpg',
        'images/320806681_1515337352309999_7268222303037674501_n.jpg',
        'images/321319886_141292975388158_3054573911922590685_n.jpg',
        'images/328667933_215320307567766_85536973086725936_n.jpg',
        'images/329574925_5835002969928232_7002627822803082685_n.jpg'
    ];

    let intervalId = null;

    // Preload images to avoid flickering
    dreamcoreImages.forEach(src => {
        const img = new Image();
        img.src = src;
    });

    // Function to change background image randomly
    function flashRandomImage() {
        const randomIndex = Math.floor(Math.random() * dreamcoreImages.length);
        overlay.style.backgroundImage = `url('${dreamcoreImages[randomIndex]}')`;
        // Higher opacity for clearer view of the aesthetic
        overlay.style.opacity = '0.7'; 
    }

    // Hover effect logic on the entire question section for bigger hit area
    questionSection.addEventListener('mouseenter', () => {
        // Start flashing images rapidly
        flashRandomImage(); 
        intervalId = setInterval(flashRandomImage, 120); // Slightly faster
    });

    questionSection.addEventListener('mouseleave', () => {
        // Stop flashing and hide overlay
        clearInterval(intervalId);
        overlay.style.opacity = '0';
        setTimeout(() => {
            overlay.style.backgroundImage = 'none';
        }, 100);
    });
    
    // Auto-resize textarea
    answerInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Modal Logic
    if (infoBtn && infoModal && closeModal) {
        infoBtn.addEventListener('click', () => {
            infoModal.classList.remove('hidden');
        });
        
        closeModal.addEventListener('click', () => {
            infoModal.classList.add('hidden');
        });
        
        // Close on outside click
        infoModal.addEventListener('click', (e) => {
            if (e.target === infoModal) {
                infoModal.classList.add('hidden');
            }
        });
    }

    // --- Voice Memo Logic ---
    const recordBtn = document.getElementById('record-btn');
    const stopBtn = document.getElementById('stop-btn');
    const recordingStatus = document.getElementById('recording-status');
    const audioPlayerContainer = document.getElementById('audio-player-container');
    const audioPlayback = document.getElementById('audio-playback');
    const deleteRecordingBtn = document.getElementById('delete-recording-btn');

    let mediaRecorder;
    let audioChunks = [];

    if (recordBtn) { // Check if elements exist (Voice memo is optional feature)
        recordBtn.addEventListener('click', async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.start();
                
                // UI Updates
                recordBtn.classList.add('hidden');
                stopBtn.classList.remove('hidden');
                recordingStatus.classList.remove('hidden');
                
                audioChunks = [];
                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener("stop", () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioPlayback.src = audioUrl;
                    
                    // UI Updates
                    stopBtn.classList.add('hidden');
                    recordingStatus.classList.add('hidden');
                    audioPlayerContainer.classList.remove('hidden');
                    
                    // Stop all tracks to release microphone
                    stream.getTracks().forEach(track => track.stop());
                });
                
            } catch (err) {
                console.error("Error accessing microphone:", err);
                alert("Could not access microphone. Please allow permissions.");
            }
        });

        stopBtn.addEventListener('click', () => {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
        });

        deleteRecordingBtn.addEventListener('click', () => {
            audioPlayback.src = "";
            audioPlayerContainer.classList.add('hidden');
            recordBtn.classList.remove('hidden');
            audioChunks = [];
        });
    }


    // Form submission logic
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const nick = nickInput.value;
        const answer = answerInput.value;
        const consent = document.getElementById('consent').checked;

        const formData = new FormData();
        formData.append('nick', nick);
        formData.append('odgovor', answer);
        formData.append('consent', consent);

        if (audioChunks.length > 0) {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            formData.append('audio', audioBlob, 'voice_memo.wav');
        }
        
        const button = form.querySelector('#submit-btn');
        const originalText = button.innerText;
        
        // Change button state for "playful" feedback
        button.style.transform = "scale(0.95)";
        button.innerText = "...";
        button.disabled = true;

        try {
            const response = await fetch('/submit', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                 // Success state
                form.style.display = 'none';
                thankYouMessage.classList.remove('hidden');
                console.log('Email successfully sent.');
            } else {
                const errorData = await response.json();
                console.error('Server error:', errorData);
                throw new Error('Server returned ' + response.status + ': ' + (errorData.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error sending form:', error);
            alert('There was a problem sending your answer. Please check if the server is running and configured correctly.\n\nError: ' + error.message);
            
            // Reset button
            button.innerText = originalText;
            button.disabled = false;
            button.style.transform = "none";
        }
    });
});
