"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";

const ALLOWED = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain", "text/csv"];
const MAX_MB = 50;

export default function UploadPage() {
  const router = useRouter();
  const [dragging, setDragging] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);

  const validate = (f) => {
    if (!ALLOWED.includes(f.type)) return `${f.name}: unsupported type`;
    if (f.size > MAX_MB * 1024 * 1024) return `${f.name}: exceeds ${MAX_MB}MB`;
    return null;
  };

  const addFiles = useCallback((incoming) => {
    const arr = Array.from(incoming);
    const valid = [];
    const errs = [];
    arr.forEach((f) => {
      const e = validate(f);
      e ? errs.push(e) : valid.push({ file: f, error: null, status: "pending" });
    });
    if (errs.length) alert(errs.join("\n"));
    setFiles((prev) => [...prev, ...valid]);
  }, []);

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  };

  const uploadAll = async () => {
    if (!files.length) return;
    setUploading(true);
    const token = localStorage.getItem("access_token");

    const updated = [...files];
    for (let i = 0; i < updated.length; i++) {
      if (updated[i].status !== "pending") continue;
      updated[i] = { ...updated[i], status: "uploading" };
      setFiles([...updated]);

      const fd = new FormData();
      fd.append("file", updated[i].file);

      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/documents/upload`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: fd,
        });
        if (!res.ok) throw new Error((await res.json()).detail || "Upload failed");
        const data = await res.json();
        updated[i] = { ...updated[i], status: "done", result: data };
        setResults((r) => [...r, data]);
      } catch (err) {
        updated[i] = { ...updated[i], status: "error", error: err.message };
      }
      setFiles([...updated]);
    }
    setUploading(false);
  };

  const removeFile = (idx) => setFiles((f) => f.filter((_, i) => i !== idx));

  const statusColor = { pending: "text-gray-400", uploading: "text-blue-400", done: "text-green-400", error: "text-red-400" };
  const statusLabel = { pending: "Pending", uploading: "Uploading…", done: "✓ Done", error: "✗ Failed" };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Upload Documents</h1>
          <p className="text-gray-400 text-sm mt-1">PDF, DOCX, TXT, CSV · Max 50 MB each</p>
        </div>

        {/* Drop zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => document.getElementById("file-input").click()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors
            ${dragging ? "border-blue-500 bg-blue-500/10" : "border-gray-700 hover:border-gray-500"}`}
        >
          <div className="text-4xl mb-3">📂</div>
          <p className="text-gray-300 font-medium">Drag & drop files here</p>
          <p className="text-gray-500 text-sm mt-1">or click to browse</p>
          <input
            id="file-input"
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.csv"
            className="hidden"
            onChange={(e) => addFiles(e.target.files)}
          />
        </div>

        {/* File list */}
        {files.length > 0 && (
          <div className="space-y-2">
            {files.map((f, i) => (
              <div key={i} className="flex items-center justify-between bg-gray-800 rounded-lg px-4 py-3">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xl">📄</span>
                  <div className="min-w-0">
                    <p className="text-sm text-gray-200 truncate">{f.file.name}</p>
                    <p className="text-xs text-gray-500">{(f.file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-medium ${statusColor[f.status]}`}>{statusLabel[f.status]}</span>
                  {f.status === "pending" && (
                    <button onClick={() => removeFile(i)} className="text-gray-500 hover:text-red-400 text-lg leading-none">×</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={uploadAll}
            disabled={uploading || !files.some((f) => f.status === "pending")}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 rounded-lg text-sm font-medium transition-colors"
          >
            {uploading ? "Uploading…" : "Upload All"}
          </button>
          {results.length > 0 && (
            <button
              onClick={() => router.push("/dashboard")}
              className="px-6 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-colors"
            >
              Go to Dashboard →
            </button>
          )}
        </div>

        {/* Success list */}
        {results.length > 0 && (
          <div className="bg-green-900/30 border border-green-700/40 rounded-xl p-4">
            <p className="text-green-400 text-sm font-medium mb-2">Uploaded successfully ({results.length})</p>
            <ul className="space-y-1">
              {results.map((r, i) => (
                <li key={i} className="text-xs text-green-300">✓ {r.original_name} — ID #{r.id}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
