"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { 
  UploadCloud, 
  FileText, 
  X, 
  CheckCircle2, 
  AlertCircle, 
  ArrowLeft,
  Loader2,
  Check
} from "lucide-react";

const ALLOWED = [
  "application/pdf", 
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
  "text/plain", 
  "text/csv"
];
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
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/documents/upload`, {
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

  const statusStyle = {
    pending: "text-gray-400 border-gray-800 bg-gray-900/40",
    uploading: "text-blue-400 border-blue-500/20 bg-blue-500/5",
    done: "text-emerald-400 border-emerald-500/20 bg-emerald-500/5",
    error: "text-rose-400 border-rose-500/20 bg-rose-500/5",
  };

  const statusLabel = {
    pending: "Pending Ingestion",
    uploading: "Uploading…",
    done: "Completed",
    error: "Failed",
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8 relative overflow-hidden">
      <div className="max-w-3xl mx-auto space-y-8 relative z-10">
        
        {/* Header */}
        <div className="border-b border-gray-900 pb-6 flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/10">
            <UploadCloud className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">Upload Documents</h1>
            <p className="text-gray-400 text-sm mt-0.5">
              Ingest files to index them inside the vector knowledge base
            </p>
          </div>
        </div>

        {/* Drop zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => document.getElementById("file-input").click()}
          className={`border-2 border-dashed rounded-2xl p-14 text-center cursor-pointer transition-all duration-300 backdrop-blur-md
            ${dragging 
              ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/5 scale-[1.01]" 
              : "border-gray-800 bg-gray-900/20 hover:border-gray-700/80 hover:bg-gray-900/40"}`}
        >
          <div className="w-14 h-14 rounded-2xl bg-gray-950/60 border border-gray-850 flex items-center justify-center mx-auto mb-4">
            <UploadCloud className={`w-7 h-7 text-gray-500 group-hover:text-blue-400 ${dragging ? "text-blue-400 animate-bounce" : ""}`} />
          </div>
          <p className="text-gray-300 font-bold text-sm">Drag & drop files here</p>
          <p className="text-gray-500 text-xs mt-1">Accepts PDF, DOCX, TXT, CSV up to 50 MB</p>
          
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
          <div className="space-y-2.5">
            <p className="text-[10px] uppercase font-bold text-gray-500 tracking-wider px-1">
              Ingestion Queue ({files.length} file{files.length !== 1 ? "s" : ""})
            </p>
            
            {files.map((f, i) => (
              <div 
                key={i} 
                className={`flex items-center justify-between border rounded-xl px-5 py-3.5 transition-colors ${statusStyle[f.status]}`}
              >
                <div className="flex items-center gap-3.5 min-w-0">
                  <div className="w-9 h-9 rounded-lg bg-gray-950 flex items-center justify-center text-lg shadow-inner">
                    📄
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold truncate text-gray-200">{f.file.name}</p>
                    <p className="text-xs text-gray-500">{(f.file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 flex-shrink-0">
                  <span className="text-[10px] uppercase tracking-wider font-bold">
                    {statusLabel[f.status]}
                  </span>
                  
                  {f.status === "uploading" && (
                    <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                  )}
                  {f.status === "done" && (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  )}
                  {f.status === "error" && (
                    <AlertCircle className="w-4 h-4 text-rose-400" title={f.error} />
                  )}
                  
                  {f.status === "pending" && (
                    <button 
                      onClick={(e) => { e.stopPropagation(); removeFile(i); }} 
                      className="p-1 text-gray-500 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-all"
                      title="Remove"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-3 border-t border-gray-900 pt-6">
          <button
            onClick={uploadAll}
            disabled={uploading || !files.some((f) => f.status === "pending")}
            className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 disabled:from-gray-800 disabled:to-gray-800 text-white rounded-xl text-xs font-bold transition-all hover:shadow-lg hover:shadow-blue-500/25"
          >
            {uploading ? (
              <span className="flex items-center gap-1.5">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Ingesting…
              </span>
            ) : (
              "Ingest All"
            )}
          </button>
          
          {results.length > 0 && (
            <button
              onClick={() => router.push("/dashboard")}
              className="px-6 py-2.5 bg-gray-900 border border-gray-800 hover:border-gray-700 text-gray-300 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Return to Dashboard
            </button>
          )}
        </div>

        {/* Success list */}
        {results.length > 0 && (
          <div className="bg-emerald-500/5 border border-emerald-500/10 rounded-2xl p-5 space-y-3">
            <p className="text-emerald-400 text-xs font-bold uppercase tracking-wider flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-400" />
              Ingested Successfully ({results.length})
            </p>
            <ul className="space-y-2">
              {results.map((r, i) => (
                <li key={i} className="text-xs text-gray-400 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  <span className="font-semibold text-gray-300 truncate max-w-sm">{r.original_name}</span>
                  <span className="text-[10px] text-gray-600 font-mono">ID #{r.id}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
