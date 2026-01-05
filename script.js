async function send() {
  const msg = document.getElementById("msg").value;

  const res = await fetch("https://YOUR_BACKEND_URL/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg })
  });

  const data = await res.json();
  document.getElementById("chat").innerHTML +=
    `<p><b>You:</b> ${msg}</p><p><b>Bot:</b> ${JSON.stringify(data.reply)}</p>`;
}
