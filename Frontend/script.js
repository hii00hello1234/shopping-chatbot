async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value;

    if (!message) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<p class="user">You: ${message}</p>`;

    const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    const data = await response.json();
    chatBox.innerHTML += `<p class="bot">Bot: ${data.reply}</p>`;

    input.value = "";
}
