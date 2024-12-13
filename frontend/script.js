const startButton = document.getElementById('startButton');
const transcriptionDiv = document.getElementById('transcription');

let mediaRecorder;
let audioChunks = [];
const socket = new WebSocket('ws://localhost:8765');

socket.onmessage = (event) => {
    transcriptionDiv.textContent = event.data;
};

startButton.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(event.data);
        }
    };

    mediaRecorder.start(1000);  // 1秒ごとにデータを送信
});