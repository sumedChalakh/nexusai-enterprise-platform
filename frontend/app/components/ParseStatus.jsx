"use client";

import { useEffect, useState, useCallback } from "react";

const STATUS_CONFIG = {
  uploaded:   { label: "Queued",       color: "text-gray-400",   bg: "bg-gray-800/60 border border-gray-700", pulse: false },
  processing: { label: "Parsing…",     color: "text-blue-400",   bg: "bg-blue-950/40 border border-blue-800/40",   pulse: true  },
  ready:      { label: "Parsed",       color: "text-cyan-400",   bg: "bg-cyan-950/40 border border-cyan-800/40",   pulse: false },
  chunking:   { label: "Chunking…",    color: "text-indigo-400", bg: "bg-indigo-950/40 border border-indigo-800/40", pulse: true  },
  chunked:    { label: "Chunked",      color: "text-teal-400",   bg: "bg-teal-950/40 border border-teal-800/40",   pulse: false },
  embedding:  { label: "Embedding…",   color: "text-purple-400", bg: "bg-purple-950/40 border border-purple-800/40", pulse: true  },
  embedded:   { label: "Embedded",     color: "text-emerald-400",bg: "bg-emerald-950/40 border border-emerald-800/40",pulse: false },
  failed:     { label: "Failed",       color: "text-red-400",    bg: "bg-red-950/40 border border-red-800/40",    pulse: false },
};

export default function ParseStatus({ docId, initialStatus, onReady }) {
  const [status, setStatus] = useState(initialStatus || "uploaded");
  const [wordCount, setWordCount] = useState(0);
  const [error, setError] = useState(null);

  const poll = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    try {
      const res = await fetch(
        `/api/v1/documents/${docId}/status`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) return;
      const data = await res.json();
      setStatus(data.status);
      setWordCount(data.word_count);
      setError(data.parse_error);
      if ((data.status === "embedded" || data.status === "chunked" || data.status === "ready") && onReady) {
        onReady(data);
      }
    } catch (e) {
      console.error("Poll error:", e);
    }
  }, [docId, onReady]);

  useEffect(() => {
    if (status === "embedded" || status === "failed") return;
    poll();
    const id = setInterval(poll, 3000);
    return () => clearInterval(id);
  }, [status, poll]);

  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.uploaded;

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${cfg.bg} ${cfg.color}`}>
      {cfg.pulse && (
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500" />
        </span>
      )}
      {cfg.label}
      {status === "ready" && wordCount > 0 && (
        <span className="text-green-300 ml-1">· {wordCount.toLocaleString()} words</span>
      )}
      {status === "failed" && error && (
        <span className="text-red-300 ml-1 truncate max-w-[160px]" title={error}>· {error}</span>
      )}
    </div>
  );
}
