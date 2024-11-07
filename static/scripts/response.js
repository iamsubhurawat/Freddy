var audioChunks = [];
document.getElementById('loader').style.display = 'none';
if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(function(stream) {
        var mediaRecorder = new MediaRecorder(stream);
        console.log("Media Started !");
        document.getElementById('startRecording').onclick = function() {
        mediaRecorder.start();
        console.log("Recording Started !");
        document.getElementById('startRecording').disabled = true;
        document.getElementById('stopRecording').disabled = false;
        }
        document.getElementById('stopRecording').onclick = function() {
        mediaRecorder.stop();
        console.log("Recording Stopped !");
        document.getElementById('startRecording').disabled = false;
        document.getElementById('stopRecording').disabled = true;
        document.getElementById('loader').style.display = 'block';
        mediaRecorder.ondataavailable = function(e) {audioChunks.push(e.data);}
        mediaRecorder.onstop = function(e) {
            var audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            var formData = new FormData();
            formData.append('audio', audioBlob);
            fetch('/audio_response', { method: 'POST', body: formData })
            .then(response => response.blob())
            .then(blob => {
                var audio = new Audio(URL.createObjectURL(blob));
                audio.play();
                audio.onplaying = function() {
                    document.getElementById('conversation-container').style.display = 'block';
                    fetch('/text_response', { method: 'GET' })
                    .then(response => response.text())
                    .then(llmResponse => {
                        const parsedResponse = JSON.parse(llmResponse);
                        document.getElementById('user-query').textContent = parsedResponse.user_query;
                        document.getElementById('llm-response').textContent = parsedResponse.llm_response;
                        document.getElementById('loader').style.display = 'none';
                    })
                    .catch(error => console.error('Error:', error));
                };
            })
            .catch(error => console.error('Error:', error));
            audioChunks = [];
        }
        }
    })
    .catch(function(err) {
        console.log('The following getUserMedia error occurred: ' + err);
    });
}