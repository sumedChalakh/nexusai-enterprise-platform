"use client";

import { useState } from "react";
import Link from "next/link";
import { 
  Search, 
  FileText, 
  Cpu, 
  HelpCircle, 
  ArrowUpRight, 
  Sparkles,
  AlertCircle,
  Hash,
  BookOpen
} from "lucide-react";

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
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/search/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query, limit: 8 }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Search failed");
      const data = await res.json();
      setResults(data.results || []);
      setSearched(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => {
    if (score >= 0.8) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
    if (score >= 0.6) return "text-amber-400 bg-amber-500/10 border-amber-500/20";
    return "text-gray-400 bg-gray-500/10 border-gray-500/20";
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8 relative overflow-hidden">
      <div className="max-w-3xl mx-auto space-y-8 relative z-10">
        
        {/* Header */}
        <div className="border-b border-gray-900 pb-6 flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white shadow-lg shadow-emerald-500/10">
            <Search className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">Semantic Search</h1>
            <p className="text-gray-400 text-sm mt-0.5">
              Query your indexed knowledge base by meaning, powered by vector embeddings
            </p>
          </div>
        </div>

        {/* Form Input */}
        <form onSubmit={runSearch} className="flex gap-3">
          <div className="relative flex-1 flex items-center bg-gray-900/60 border border-gray-800 focus-within:border-emerald-500/60 rounded-xl px-4 py-3 transition-all">
            <Search className="w-4 h-4 text-gray-500 mr-3" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question or enter concepts (e.g., 'growth statistics' or 'revenue models')"
              className="flex-1 bg-transparent text-sm text-gray-100 placeholder-gray-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-40 disabled:from-gray-800 disabled:to-gray-800 text-white rounded-xl text-sm font-semibold transition-all hover:shadow-lg hover:shadow-emerald-500/25 flex items-center gap-1.5"
          >
            {loading ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Searching…
              </>
            ) : (
              "Search"
            )}
          </button>
        </form>

        {/* Error State */}
        {error && (
          <div className="bg-rose-900/20 border border-rose-700/30 rounded-xl p-4 flex gap-3 text-rose-400 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="font-semibold">Search operation failed</p>
              <p className="text-xs text-rose-500/90 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Results Container */}
        {searched && !error && (
          <div className="space-y-4">
            <div className="flex items-center justify-between px-1">
              <p className="text-xs text-gray-500 uppercase tracking-widest font-bold">
                Matches Ingested ({results.length} found)
              </p>
              <span className="text-[10px] uppercase font-bold text-gray-600 flex items-center gap-1">
                <Cpu className="w-3 h-3 text-emerald-500" />
                Vector Distance Cosine
              </span>
            </div>

            {results.length === 0 ? (
              <div className="bg-gray-900/40 border border-gray-800 rounded-2xl p-16 text-center">
                <div className="text-4xl mb-4 text-gray-600">🔍</div>
                <h3 className="text-sm font-semibold text-gray-300">No matching chunks found</h3>
                <p className="text-xs text-gray-500 mt-1 max-w-xs mx-auto">Try rephrasing your search query or uploading more contextual documents.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {results.map((r, i) => (
                  <Link
                    key={r.chunk_id}
                    href={`/dashboard/documents/${r.document_id}`}
                    className="block bg-gray-900/40 backdrop-blur-md rounded-xl p-5 hover:bg-gray-900/80 border border-gray-800 hover:border-gray-700 transition-all duration-300 group hover:-translate-y-0.5 hover:shadow-xl hover:shadow-black/25"
                  >
                    <div className="flex items-center justify-between mb-3 border-b border-gray-800/60 pb-2.5">
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1 font-semibold text-gray-400 group-hover:text-emerald-400 transition-colors">
                          <FileText className="w-3.5 h-3.5" />
                          Doc #{r.document_id}
                        </span>
                        <span>·</span>
                        <span className="flex items-center gap-1">
                          <Hash className="w-3 h-3" />
                          Chunk {r.chunk_index}
                        </span>
                        {r.page_number && (
                          <>
                            <span>·</span>
                            <span className="flex items-center gap-1">
                              <BookOpen className="w-3 h-3" />
                              Page {r.page_number}
                            </span>
                          </>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-mono font-bold tracking-wider px-2 py-0.5 rounded border uppercase ${scoreColor(r.score)}`}>
                          {(r.score * 100).toFixed(1)}% Match
                        </span>
                        <ArrowUpRight className="w-3.5 h-3.5 text-gray-600 group-hover:text-emerald-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-300 leading-relaxed font-mono">
                      {r.text}
                    </p>
                  </Link>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
