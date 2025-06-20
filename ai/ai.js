// voiceAssistant.js

let recognition;
let isListening = false;

function startDictation() {
    window.speechSynthesis.cancel();

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";
        recognition.start();
        isListening = true;

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript.toLowerCase();
            console.log("Heard:", transcript);

            document.getElementById('questionInput').value = transcript;
            recognition.stop();
            isListening = false;

            const form = document.getElementById('voiceForm');
            if(form) form.submit();
        };

        recognition.onerror = function (event) {
            recognition.stop();
            isListening = false;
        };

        recognition.onend = function () {
            isListening = false;
        };
    } else {
        alert("Your browser does not support speech recognition.");
    }
}

function stopDictation() {
    window.speechSynthesis.cancel();
    if (recognition) {
        recognition.stop();
    }
}

document.addEventListener("keydown", function(event) {
    if (event.code === "Space") {
        if(!isListening) {
            startDictation();
        }
    }
});

setInterval(() => {
    const startBtn = document.getElementById("start");
    if(startBtn) {
        startBtn.disabled = isListening;
    }
}, 200);
