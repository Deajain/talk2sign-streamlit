let isRecognizing = false;
const assetsFolder = 'assets/';
const videoContainer = document.getElementById('video-container');
let videoPaths = [];

const stopWords = new Set(['is', 'are', 'am', 'the', 'in', 'on', 'a', 'an', 'of', 'to', 'and', 'but', 'or', 'if', 'then', 'so', 'as', 'was', 'were', 'has', 'have', 'had']);

function startRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech recognition not supported in this browser.");
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = true;

    recognition.onstart = () => {
        resetTranscript();
        isRecognizing = true;
        document.getElementById('status').innerText = 'Listening...';
    };

    recognition.onresult = (event) => {
        let fullTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
            fullTranscript += event.results[i][0].transcript + ' ';
        }
        document.getElementById('transcript').innerText = fullTranscript.trim();
    };
    

    recognition.onerror = (event) => {
        document.getElementById('status').innerText = 'Error: ' + event.error;
    };

    recognition.onend = () => {
        isRecognizing = false;
        document.getElementById('status').innerText = 'Press "Start Voice Recognition" and speak...';
    };

    recognition.start();
}

function stopRecognition() {
    if (isRecognizing && recognition) {
        recognition.stop();
        isRecognizing = false;
        recognition = null;
    }
}


function playSignLanguage() {
    if (isRecognizing) {
        stopRecognition(); // stop listening
    }

    const transcript = document.getElementById('transcript').innerText.trim();

    if (!transcript) {
        document.getElementById('status').innerText = 'No speech detected. Please speak before playing.';
        return;
    }

    // Clear previous video + queue
    videoPaths = [];
    isPlaying = false;
    videoElement = null;
    document.getElementById('video-container').innerHTML = '';

    displaySignLanguageVideos(transcript);
}


async function displaySignLanguageVideos(text) {
    const cleanedText = text.toLowerCase().replace(/[^\w\s]/gi, '');
    const words = cleanedText.split(' ');

    // Remove stop words
    const filteredWords = words.filter(word => !stopWords.has(word));

    // Stem the words to their base forms
    const baseFormWords = filteredWords.map(stemWord);

    // Clear previous video paths
    videoPaths = [];

    // Display loading state
    document.getElementById('status').innerText = 'Loading videos...';

    for (let word of baseFormWords) {
        let videoName = capitalizeFirstLetter(word);
        let videoPath = `${assetsFolder}${videoName}.mp4`;

        try {
            const response = await fetch(videoPath);
            if (response.ok) {
                console.log(`Adding video to queue: ${videoName}.mp4`);
                videoPaths.push(videoPath);
            } else {
                // If the video is not found, use letter videos
                for (const letter of word.toUpperCase()) {
                    let letterVideoPath = `${assetsFolder}${letter}.mp4`;
                    console.log(`Adding video to queue: ${letter}.mp4`);
                    videoPaths.push(letterVideoPath);
                }
            }
        } catch (error) {
            console.error(`Error fetching video for ${word}:`, error);
        }
    }

    if (videoPaths.length > 0) {
        playVideoQueue();
    } else {
        document.getElementById('status').innerText = 'No videos available for the given input.';
    }
}

function stemWord(word) {
    if (word.endsWith('ing')) {
        return word.slice(0, -3);
    } else if (word.endsWith('ed')) {
        return word.slice(0, -2);
    } else if (word.endsWith('s')) {
        return word.slice(0, -1);
    }
    return word;
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

let videoElement;
let isPlaying = false;

function playVideoQueue() {
    if (isPlaying) return; // prevent double-starting
    isPlaying = true;

    let currentVideoIndex = 0;

    if (!videoElement) {
        videoElement = document.createElement('video');
        videoElement.autoplay = true;
        videoElement.loop = false;
        videoElement.muted = true;
        videoElement.controls = false;
        videoElement.style.display = 'block';
        videoElement.width = videoContainer.clientWidth;

        videoElement.addEventListener('ended', () => {
            currentVideoIndex++;
            if (currentVideoIndex < videoPaths.length) {
                videoElement.src = videoPaths[currentVideoIndex];
                videoElement.load();
                videoElement.play().catch(error => console.error("Error playing:", error));
            } else {
                document.getElementById('status').innerText = 'All videos played.';
                isPlaying = false;
            }
        });

        videoContainer.innerHTML = '';
        videoContainer.appendChild(videoElement);
    }

    if (videoPaths.length > 0) {
        videoElement.src = videoPaths[currentVideoIndex];
        videoElement.load();
        videoElement.play().catch(error => console.error("Error playing:", error));
    } else {
        document.getElementById('status').innerText = 'No videos available.';
        isPlaying = false;
    }
}


function downloadTranscript() {
    const transcript = document.getElementById('transcript').innerText;
    const blob = new Blob([transcript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcript.txt';
    a.click();
    URL.revokeObjectURL(url);
}

function resetTranscript() {
    document.getElementById('transcript').innerText = ' ';
    document.getElementById('results').innerHTML = '';
    document.getElementById('video-container').innerHTML = '';
    document.getElementById('status').innerText = 'Press "Start Voice Recognition" and speak...';
    videoPaths = [];
    videoElement = null;
}
