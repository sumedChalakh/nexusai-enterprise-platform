"use client";

import { useEffect, useState, useCallback } from "react";

const STATUS_CONFIG = {
  uploaded:   { label: "Queued",     color: "text-gray-400",   bg: "bg-gray-700/40",   pulse: false },
  processing: { label: "Parsing…",   color: "text-blue-400",   bg: "bg-blue-500/20",   pulse: true  },
  ready:      { label: "Ready",      color: "text-green-400",  bg: "bg-green-500/20",  pulse: false },
  failed:     { label: "Failed",     color: "text-red-400",    bg: "bg-red-500/20",    pulse: false },
};

export default function ParseStatus({ docId, initialStatus, onReady }) {
  const [status, setStatus] = useState(initialStatus || "uploaded");
  const [wordCount, setWordCount] = useState(0);
  const [error, setError] = useState(null);

  const poll = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/documents/${docId}/status`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) return;
      const data = await res.json();
      setStatus(data.status);
      setWordCount(data.word_count);
      setError(data.parse_error);
      if (data.status === "ready" && onReady) onReady(data);
    } catch (e) {
      console.error("Poll error:", e);
    }
  }, [docId, onReady]);

  useEffect(() => {
    if (status === "ready" || status === "failed") return;
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
