"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const typeIcon = {
  "application/pdf": "📕",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "📘",
  "text/plain": "📄",
  "text/csv": "📊",
};

const statusBadge = {
  uploaded: "bg-yellow-500/20 text-yellow-400",
  processing: "bg-blue-500/20 text-blue-400",
  ready: "bg-green-500/20 text-green-400",
  failed: "bg-red-500/20 text-red-400",
};

export default function DocumentList() {
  const [docs, setDocs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchDocs = async () => {
    const token = localStorage.getItem("access_token");
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/documents/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setDocs(data.documents);
      setTotal(data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this document?")) return;
    const token = localStorage.getItem("access_token");
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/documents/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchDocs();
  };

  useEffect(() => { fetchDocs(); }, []);

  if (loading) return <div className="text-gray-400 text-sm">Loading documents…</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">My Documents ({total})</h2>
        <Link href="/dashboard/upload" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors">
          + Upload
        </Link>
      </div>

      {docs.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-2">📂</div>
          <p>No documents yet.</p>
          <Link href="/dashboard/upload" className="text-blue-400 text-sm hover:underline mt-1 block">Upload your first document →</Link>
        </div>
      ) : (
        <div className="space-y-2">
          {docs.map((doc) => (
            <div key={doc.id} className="flex items-center justify-between bg-gray-800 rounded-lg px-4 py-3">
              <div className="flex items-center gap-3 min-w-0">
                <span className="text-2xl">{typeIcon[doc.content_type] || "📄"}</span>
                <div className="min-w-0">
                  <p className="text-sm text-gray-200 truncate font-medium">{doc.original_name}</p>
                  <p className="text-xs text-gray-500">
                    {(doc.size_bytes / 1024).toFixed(1)} KB · {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusBadge[doc.status]}`}>
                  {doc.status}
                </span>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="text-gray-500 hover:text-red-400 text-sm transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
