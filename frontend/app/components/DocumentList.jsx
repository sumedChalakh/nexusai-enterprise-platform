"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Trash2, FileText, Calendar, HardDrive, ExternalLink } from "lucide-react";

const typeIcon = {
  "application/pdf": "📕",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "📘",
  "text/plain": "📄",
  "text/csv": "📊",
};

const statusBadge = {
  uploaded: "bg-amber-500/10 border border-amber-500/20 text-amber-400",
  processing: "bg-blue-500/10 border border-blue-500/20 text-blue-400 animate-pulse",
  ready: "bg-cyan-500/10 border border-cyan-500/20 text-cyan-400",
  chunking: "bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 animate-pulse",
  chunked: "bg-teal-500/10 border border-teal-500/20 text-teal-400",
  embedding: "bg-purple-500/10 border border-purple-500/20 text-purple-400 animate-pulse",
  embedded: "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400",
  failed: "bg-rose-500/10 border border-rose-500/20 text-rose-400",
};

export default function DocumentList() {
  const [docs, setDocs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchDocs = async () => {
    const token = localStorage.getItem("access_token");
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/documents/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setDocs(data.documents || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, id) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Delete this document?")) return;
    const token = localStorage.getItem("access_token");
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/documents/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchDocs();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  useEffect(() => { fetchDocs(); }, []);

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="h-6 w-36 bg-gray-800 rounded animate-pulse" />
          <div className="h-10 w-24 bg-gray-800 rounded animate-pulse" />
        </div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-20 bg-gray-900/40 border border-gray-800 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between border-b border-gray-800/80 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">My Documents</h2>
          <p className="text-xs text-gray-500 mt-0.5">{total} files indexed in vector store</p>
        </div>
        <Link href="/dashboard/upload" className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-lg text-sm font-semibold transition-all hover:shadow-lg hover:shadow-blue-500/25">
          + Upload
        </Link>
      </div>

      {docs.length === 0 ? (
        <div className="bg-gray-900/40 backdrop-blur-md border border-gray-800 border-dashed rounded-2xl p-14 text-center">
          <div className="text-4xl mb-4 text-gray-600">📂</div>
          <h3 className="text-sm font-semibold text-gray-300">No documents found</h3>
          <p className="text-xs text-gray-500 mt-1 max-w-xs mx-auto">Upload PDF, DOCX, TXT or CSV documents to start semantic searching and AI chatting.</p>
          <Link href="/dashboard/upload" className="inline-flex items-center gap-1.5 mt-5 text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors">
            Upload your first document <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {docs.map((doc) => (
            <div
              key={doc.id}
              className="group relative flex items-center justify-between bg-gray-900/40 backdrop-blur-md border border-gray-800 hover:border-gray-700/80 rounded-xl px-5 py-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-black/20"
            >
              {/* Entire left portion is the Link to detail page */}
              <Link
                href={`/dashboard/documents/${doc.id}`}
                className="flex-1 flex items-center gap-4 min-w-0 pr-4"
              >
                <div className="w-10 h-10 rounded-lg bg-gray-850 flex items-center justify-center text-xl shadow-inner group-hover:bg-gray-800 transition-colors">
                  {typeIcon[doc.content_type] || "📄"}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-gray-200 font-semibold truncate group-hover:text-blue-400 transition-colors">
                    {doc.original_name}
                  </p>
                  <div className="flex items-center gap-3 text-xs text-gray-500 mt-1">
                    <span className="flex items-center gap-1">
                      <HardDrive className="w-3 h-3" />
                      {(doc.size_bytes / 1024).toFixed(1)} KB
                    </span>
                    <span>·</span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {new Date(doc.created_at).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </span>
                  </div>
                </div>
              </Link>

              {/* Right portion is actions / status */}
              <div className="flex items-center gap-3.5 flex-shrink-0 z-10">
                <span className={`text-[10px] uppercase tracking-wider px-2.5 py-1 rounded-full border font-semibold ${statusBadge[doc.status] || "bg-gray-500/10 border-gray-500/20 text-gray-400"}`}>
                  {doc.status}
                </span>
                
                <button
                  onClick={(e) => handleDelete(e, doc.id)}
                  className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
                  title="Delete Document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
