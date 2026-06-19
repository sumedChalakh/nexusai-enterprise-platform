"use client";

import { useState, useRef, useEffect } from "react";

export default function ChatPage() {
  const [messages, setMessages] = useState([]); // {role, text, sources}
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendQuestion = async (e) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || streaming) return;

    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setMessages((m) => [...m, { role: "assistant", text: "", sources: [], streaming: true }]);
    setStreaming(true);

    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/ask/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question, limit: 5 }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n\n");
        buffer = lines.pop(); // keep incomplete chunk for next read

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = JSON.parse(line.slice(6));

          if (payload.token) {
            setMessages((m) => {
              const copy = [...m];
              const last = copy[copy.length - 1];
              copy[copy.length - 1] = { ...last, text: last.text + payload.token };
              return copy;
            });
          }
          if (payload.sources) {
            setMessages((m) => {
              const copy = [...m];
              const last = copy[copy.length - 1];
              copy[copy.length - 1] = { ...last, sources: payload.sources };
              return copy;
            });
          }
          if (payload.error) {
            setMessages((m) => {
              const copy = [...m];
              copy[copy.length - 1] = { role: "assistant", text: `⚠️ ${payload.error}`, streaming: false };
              return copy;
            });
          }
        }
      }
    } catch (err) {
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = { role: "assistant", text: `⚠️ ${err.message}`, streaming: false };
        return copy;
      });
    } finally {
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = { ...copy[copy.length - 1], streaming: false };
        return copy;
      });
      setStreaming(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
      <div className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-lg font-bold text-white">Ask NexusAI</h1>
        <p className="text-xs text-gray-500">Answers are grounded in your uploaded documents</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 max-w-3xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="text-center py-20 text-gray-500">
            <div className="text-4xl mb-3">💬</div>
            <p>Ask a question about anything you've uploaded.</p>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
              m.role === "user" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-200"
            }`}>
              <p className="text-sm whitespace-pre-wrap leading-relaxed">
                {m.text}
                {m.streaming && <span className="inline-block w-2 h-4 bg-gray-400 ml-1 animate-pulse" />}
              </p>
              {m.sources && m.sources.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2 pt-2 border-t border-gray-700/50">
                  {m.sources.map((s, idx) => (
                    <a
                      key={s.chunk_id}
                      href={`/dashboard/documents/${s.document_id}`}
                      className="text-xs px-2 py-0.5 rounded-full bg-gray-700/60 text-gray-300 hover:bg-gray-600 transition-colors"
                      title={`Score: ${(s.score * 100).toFixed(0)}%`}
                    >
                      [{idx + 1}] Doc #{s.document_id}{s.page_number ? ` · p.${s.page_number}` : ""}
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendQuestion} className="border-t border-gray-800 px-6 py-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents…"
            disabled={streaming}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-full px-5 py-3 text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={streaming || !input.trim()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 rounded-full text-sm font-medium transition-colors"
          >
            {streaming ? "…" : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
}
