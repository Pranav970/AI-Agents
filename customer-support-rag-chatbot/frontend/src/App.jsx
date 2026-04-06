import React, { useState } from "react";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Upload support documents, then ask a question." }
  ]);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [topK, setTopK] = useState(5);

  const uploadFiles = async () => {
    if (!files.length) return;

    const formData = new FormData();
    for (const file of files) formData.append("files", file);

    setLoading(true);
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    setMessages((prev) => [
      ...prev,
      { role: "assistant", text: `Upload complete: ${JSON.stringify(data.results)}` }
    ]);
    setLoading(false);
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    const userMsg = { role: "user", text: question };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k: topK })
    });

    const data = await res.json();
    setMessages((prev) => [
      ...prev,
      { role: "assistant", text: data.answer }
    ]);
    setQuestion("");
    setLoading(false);
  };

  return (
    <div className="app">
      <div className="sidebar">
        <h1>Customer Support RAG Chatbot</h1>
        <p>Claude Sonnet 4.6 + RAG + Prompt Engineering</p>

        <label className="label">Upload files</label>
        <input
          type="file"
          multiple
          onChange={(e) => setFiles([...e.target.files])}
        />
        <button onClick={uploadFiles} disabled={loading}>
          Upload and Index
        </button>

        <label className="label">Top K</label>
        <input
          type="number"
          min="1"
          max="10"
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
        />
      </div>

      <div className="chat">
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`msg ${msg.role}`}>
              {msg.text}
            </div>
          ))}
        </div>

        <div className="composer">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a customer support question..."
            onKeyDown={(e) => e.key === "Enter" && askQuestion()}
          />
          <button onClick={askQuestion} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
