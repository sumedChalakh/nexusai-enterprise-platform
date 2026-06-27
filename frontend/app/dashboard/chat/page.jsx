"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { 
  Send, 
  Sparkles, 
  Trash2, 
  FileText, 
  Info,
  ArrowRight,
  MessageSquare,
  HelpCircle,
  Link2
} from "lucide-react";

const SUGGESTED_PROMPTS = [
  "Summarize the recent uploaded files",
  "What are the key findings or revenue stats?",
  "Are there any actions or dates mentioned?",
  "Explain the core architecture from my docs"
];

export default function ChatPage() {
  const [messages, setMessages] = useState([]); // {role, text, sources}
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (questionText) => {
    const question = questionText.trim();
    if (!question || streaming) return;

    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setMessages((m) => [...m, { role: "assistant", text: "", sources: [], streaming: true }]);
    setStreaming(true);

    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/chat/ask/stream`, {
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

  const onSubmit = (e) => {
    e.preventDefault();
    handleSend(input);
  };

  const clearChat = () => {
    if (confirm("Clear chat history?")) {
      setMessages([]);
    }
  };

  return (
    <div className="h-screen bg-gray-950 text-gray-100 flex flex-col relative overflow-hidden">
      {/* Header */}
      <div className="border-b border-gray-900 bg-gray-950/40 backdrop-blur-md px-8 py-4 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight">AI Chat Assistant</h1>
            <p className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider">Retrieval-Augmented Grounding</p>
          </div>
        </div>
        
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-800 bg-gray-900/40 text-xs text-gray-400 hover:text-red-400 hover:border-red-500/20 transition-all"
            title="Clear Chat"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Clear
          </button>
        )}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-8 py-8 space-y-6 max-w-4xl mx-auto w-full z-10">
        {messages.length === 0 ? (
          <div className="py-16 text-center max-w-md mx-auto space-y-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white mx-auto shadow-xl shadow-blue-500/10">
              <MessageSquare className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">Ask your Knowledge Base</h2>
              <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                Ask questions about your uploaded PDFs, DOCX files, spreadsheets or plain text. The AI will cite source chunks matching your queries.
              </p>
            </div>
            
            {/* Suggested prompts grid */}
            <div className="grid grid-cols-1 gap-2 pt-2 text-left">
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1 px-1 flex items-center gap-1.5">
                <HelpCircle className="w-3 h-3 text-blue-500" />
                Suggested Questions
              </p>
              {SUGGESTED_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(prompt)}
                  className="flex items-center justify-between text-left text-xs bg-gray-900/40 border border-gray-800 hover:border-gray-700/80 rounded-xl px-4 py-3 text-gray-300 hover:text-blue-400 transition-all hover:bg-gray-900/80 group"
                >
                  <span>{prompt}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-gray-600 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all" />
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] rounded-2xl px-5 py-4 shadow-xl ${
                  m.role === "user" 
                    ? "bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-tr-sm" 
                    : "bg-gray-900/50 backdrop-blur-md border border-gray-850 text-gray-200 rounded-tl-sm"
                }`}>
                  <div className="text-sm whitespace-pre-wrap leading-relaxed">
                    {m.text}
                    {m.streaming && (
                      <span className="inline-flex items-center gap-0.5 ml-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                      </span>
                    )}
                  </div>
                  
                  {/* Sources Grounding links */}
                  {m.sources && m.sources.length > 0 && (
                    <div className="mt-4 pt-3.5 border-t border-gray-800/85">
                      <div className="flex items-center gap-1.5 text-[10px] uppercase font-bold tracking-wider text-gray-500 mb-2">
                        <Info className="w-3.5 h-3.5 text-blue-500" />
                        Grounding Sources
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {m.sources.map((s, idx) => (
                          <Link
                            key={s.chunk_id}
                            href={`/dashboard/documents/${s.document_id}`}
                            className="inline-flex items-center gap-1.5 text-xs px-3 py-1 rounded-full bg-gray-950/80 border border-gray-800 hover:border-blue-500/35 hover:text-blue-400 text-gray-400 transition-all font-medium"
                            title={`Similarity Score: ${(s.score * 100).toFixed(1)}%`}
                          >
                            <Link2 className="w-3 h-3 text-blue-500/80" />
                            <span>[{idx + 1}] Doc #{s.document_id}</span>
                            {s.page_number && <span className="text-[10px] text-gray-600">p.{s.page_number}</span>}
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input bar */}
      <div className="border-t border-gray-900 bg-gray-950/40 backdrop-blur-md px-8 py-5 z-10">
        <form onSubmit={onSubmit} className="max-w-4xl mx-auto">
          <div className="relative flex items-center bg-gray-900/60 border border-gray-800 hover:border-gray-700/80 focus-within:border-blue-500/60 rounded-2xl px-5 py-3 transition-all">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={streaming ? "AI is typing…" : "Ask a question about your indexed knowledge…"}
              disabled={streaming}
              className="flex-1 bg-transparent text-sm text-gray-100 placeholder-gray-500 focus:outline-none disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={streaming || !input.trim()}
              className="ml-3 p-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 disabled:from-gray-800 disabled:to-gray-800 text-white rounded-xl transition-all shadow-md hover:shadow-blue-500/10 flex items-center justify-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
