// Alert message when the page loads
window.onload = function() {
    alert("If this page isn't working as expected, please go back and try again.");
};

var socketio = io();

const messages = document.getElementById("messages");

const createMessage = (name, ogMsg, trMsg) => {
  const content = `
  <div class="text">
      <span><strong>${name}</strong> says:</span>
      <span>Original: ${ogMsg}</span>
      <span>Translated: ${trMsg}</span>
      <span class="muted">${new Date().toLocaleString()}</span>
  </div>
  `;
  messages.innerHTML += content;
  messages.scrollTop = messages.scrollHeight; // Scroll to bottom for new message
};

socketio.on("message", (data) => {
  createMessage(data.name, data.ogMessage, data.trMessage);
});

const sendMessage = () => {
  const message = document.getElementById("message");
  if (message.value == "") return;
  socketio.emit("message", { data: message.value });
  message.value = "";
};

// Start Recording button event listener
document.getElementById("record-btn").addEventListener("click", () => {
  fetch("/begin_recording", { method: "POST" })
      .then(response => response.json())
      .then(data => {
          console.log(data.message);
          document.getElementById("record-btn").style.display = "none"; // Hide start button
          document.getElementById("stop-btn").style.display = "block";  // Show stop button
      })
      .catch(error => console.error("Error:", error));

  alert("Recording started");
});

// Stop Recording button event listener
document.getElementById("stop-btn").addEventListener("click", () => {
    fetch("/stop_recording", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            document.getElementById("record-btn").style.display = "block"; // Show start button
            document.getElementById("stop-btn").style.display = "none";   // Hide stop button

            // Fetch transcription after stopping the recording
            fetchTranscriptionAndSpeak();
        })
        .catch(error => console.error("Error:", error));

    alert("Recording stopped");
});

function fetchTranscriptionAndSpeak() {
  fetch("/get_transcription")
      .then(response => response.json())
      .then(data => {
          const messageInput = document.getElementById("message");
          messageInput.value = data.text;
      })
      .catch(error => console.error("Error fetching transcription:", error));
}
