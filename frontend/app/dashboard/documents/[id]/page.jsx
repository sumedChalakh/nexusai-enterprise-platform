"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import ChunkViewer from "../../../components/ChunkViewer";
import ParseStatus from "../../../components/ParseStatus";

const TABS = ["Chunks", "Extracted Text"];
const TERMINAL = ["chunked", "embedded", "failed"];

export default function DocumentDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [doc, setDoc] = useState(null);
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchDoc = async () => {
    const token = localStorage.getItem("access_token");
    const r = await fetch(
      `/api/v1/documents/${id}/status`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (r.ok) setDoc(await r.json());
    setLoading(false);
  };

  useEffect(() => { fetchDoc(); }, [id]);

  if (loading) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center text-gray-400">Loading…</div>
  );

  const isReady = ["chunked", "embedded"].includes(doc?.status);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <button onClick={() => router.back()} className="text-gray-500 hover:text-gray-300 text-sm mb-2 block">← Back</button>
            <h1 className="text-xl font-bold text-white">Document #{id}</h1>
          </div>
          <ParseStatus docId={id} initialStatus={doc?.status} onReady={fetchDoc} />
        </div>

        {/* Stats row */}
        {doc && (
          <div className="flex gap-6 text-sm text-gray-400">
            {doc.word_count > 0 && <span>📝 {doc.word_count?.toLocaleString()} words</span>}
            {doc.chunk_count > 0 && <span>🧩 {doc.chunk_count} chunks</span>}
          </div>
        )}

        {/* Tabs */}
        {isReady && (
          <>
            <div className="flex gap-1 border-b border-gray-700">
              {TABS.map((t, i) => (
                <button key={t} onClick={() => setTab(i)}
                  className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors
                    ${tab === i ? "border-blue-500 text-blue-400" : "border-transparent text-gray-500 hover:text-gray-300"}`}>
                  {t}
                </button>
              ))}
            </div>

            {tab === 0 && <ChunkViewer docId={id} />}
            {tab === 1 && (
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
                <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono leading-relaxed max-h-[70vh] overflow-y-auto">
                  {doc?.extracted_text || "No text available"}
                </pre>
              </div>
            )}
          </>
        )}

        {!isReady && doc?.status !== "failed" && (
          <div className="text-center py-16 text-gray-500">
            <div className="text-4xl mb-3">⚙️</div>
            <p>Processing document — chunks will appear here when ready.</p>
          </div>
        )}

        {doc?.status === "failed" && (
          <div className="bg-red-900/20 border border-red-700/40 rounded-xl p-6 text-red-400">
            <p className="font-medium mb-1">Processing failed</p>
            <p className="text-sm">{doc?.parse_error || "Unknown error"}</p>
          </div>
        )}
      </div>
    </div>
  );
}
