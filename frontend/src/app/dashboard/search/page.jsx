"use client";

import { useState } from "react";
import Link from "next/link";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);

  const runSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/search/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query, limit: 8 }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Search failed");
      const data = await res.json();
      setResults(data.results);
      setSearched(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => {
    if (score >= 0.8) return "text-green-400 bg-green-500/15";
    if (score >= 0.6) return "text-yellow-400 bg-yellow-500/15";
    return "text-gray-400 bg-gray-500/15";
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Semantic Search</h1>
          <p className="text-gray-400 text-sm mt-1">Search across all your embedded documents by meaning, not just keywords</p>
        </div>

        <form onSubmit={runSearch} className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. What was the Q3 revenue growth?"
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 rounded-lg text-sm font-medium transition-colors"
          >
            {loading ? "Searching…" : "Search"}
          </button>
        </form>

        {error && (
          <div className="bg-red-900/20 border border-red-700/40 rounded-lg p-4 text-red-400 text-sm">
            {error}
          </div>
        )}

        {searched && !error && (
          <div className="space-y-3">
            <p className="text-sm text-gray-500">{results.length} result{results.length !== 1 ? "s" : ""}</p>

            {results.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <div className="text-4xl mb-2">🔍</div>
                <p>No matches found. Try a different phrasing.</p>
              </div>
            ) : (
              results.map((r, i) => (
                <Link
                  key={r.chunk_id}
                  href={`/dashboard/documents/${r.document_id}`}
                  className="block bg-gray-800 rounded-lg p-4 hover:bg-gray-750 border border-gray-700 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">Doc #{r.document_id}</span>
                      <span className="text-xs text-gray-600">·</span>
                      <span className="text-xs text-gray-500">Chunk #{r.chunk_index}</span>
                      {r.page_number && (
                        <>
                          <span className="text-xs text-gray-600">·</span>
                          <span className="text-xs text-gray-500">Page {r.page_number}</span>
                        </>
                      )}
                    </div>
                    <span className={`text-xs font-mono px-2 py-0.5 rounded ${scoreColor(r.score)}`}>
                      {(r.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-sm text-gray-300 leading-relaxed">{r.text}</p>
                </Link>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
