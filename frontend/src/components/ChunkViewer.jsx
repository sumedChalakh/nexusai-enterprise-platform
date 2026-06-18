"use client";

import { useEffect, useState } from "react";

export default function ChunkViewer({ docId }) {
  const [stats, setStats] = useState(null);
  const [chunks, setChunks] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);
  const LIMIT = 10;

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : "";
  const base = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/documents/${docId}/chunks`;

  const fetchStats = async () => {
    const r = await fetch(`${base}/stats`, { headers: { Authorization: `Bearer ${token}` } });
    if (r.ok) setStats(await r.json());
  };

  const fetchChunks = async (p = 0) => {
    setLoading(true);
    const r = await fetch(`${base}/?skip=${p * LIMIT}&limit=${LIMIT}`,
      { headers: { Authorization: `Bearer ${token}` } });
    if (r.ok) {
      const d = await r.json();
      setChunks(d.chunks);
      setTotal(d.total_chunks);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStats();
    fetchChunks(0);
  }, [docId]);

  const goPage = (p) => { setPage(p); fetchChunks(p); setExpanded(null); };
  const totalPages = Math.ceil(total / LIMIT);

  return (
    <div className="space-y-4">
      {/* Stats bar */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: "Total Chunks", val: stats.chunk_count },
            { label: "Total Tokens", val: stats.total_tokens.toLocaleString() },
            { label: "Avg Tokens", val: stats.avg_tokens },
            { label: "Pages", val: stats.pages_covered || "N/A" },
          ].map(({ label, val }) => (
            <div key={label} className="bg-gray-800 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-blue-400">{val}</p>
              <p className="text-xs text-gray-500 mt-1">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Chunk list */}
      {loading ? (
        <div className="text-gray-400 text-sm text-center py-8">Loading chunks…</div>
      ) : (
        <div className="space-y-2">
          {chunks.map((c) => (
            <div key={c.id} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
              <button
                onClick={() => setExpanded(expanded === c.id ? null : c.id)}
                className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-750 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono bg-blue-900/50 text-blue-300 px-2 py-0.5 rounded">
                    #{c.chunk_index}
                  </span>
                  {c.page_number && (
                    <span className="text-xs text-gray-500">Page {c.page_number}</span>
                  )}
                  <span className="text-sm text-gray-300 truncate max-w-[420px]">
                    {c.text.slice(0, 80)}…
                  </span>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs text-gray-500">{c.token_estimate} tokens</span>
                  <span className="text-gray-500 text-xs">{expanded === c.id ? "▲" : "▼"}</span>
                </div>
              </button>

              {expanded === c.id && (
                <div className="px-4 pb-4 border-t border-gray-700">
                  <div className="flex gap-4 text-xs text-gray-500 py-2 mb-2">
                    <span>chars {c.start_char}–{c.end_char}</span>
                    <span>{c.end_char - c.start_char} chars</span>
                    <span>{c.token_estimate} tokens</span>
                  </div>
                  <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono leading-relaxed bg-gray-900 rounded p-3 max-h-60 overflow-y-auto">
                    {c.text}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <button onClick={() => goPage(page - 1)} disabled={page === 0}
            className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 disabled:opacity-30 rounded text-sm">
            ←
          </button>
          <span className="text-sm text-gray-400">Page {page + 1} / {totalPages}</span>
          <button onClick={() => goPage(page + 1)} disabled={page >= totalPages - 1}
            className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 disabled:opacity-30 rounded text-sm">
            →
          </button>
        </div>
      )}
    </div>
  );
}
