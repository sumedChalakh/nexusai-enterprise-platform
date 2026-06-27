"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  UploadCloud, 
  MessageSquareCode, 
  Search, 
  FolderClosed, 
  ArrowRight,
  FileText,
  Clock,
  HardDrive,
  Cpu,
  Database,
  SearchIcon,
  HelpCircle
} from "lucide-react";

const quickLinks = [
  {
    href: "/dashboard/upload",
    icon: UploadCloud,
    title: "Upload Document",
    desc: "Drag & drop PDF, DOCX, TXT or CSV files",
    color: "from-blue-600/15 to-indigo-600/5 border-blue-500/15 hover:border-blue-400/40 text-blue-400 hover:shadow-blue-500/5",
  },
  {
    href: "/dashboard/chat",
    icon: MessageSquareCode,
    title: "AI Chat Assistant",
    desc: "Ask questions grounded in your index",
    color: "from-purple-600/15 to-indigo-600/5 border-purple-500/15 hover:border-purple-400/40 text-purple-400 hover:shadow-purple-500/5",
  },
  {
    href: "/dashboard/search",
    icon: Search,
    title: "Semantic Search",
    desc: "Find matches by concept, not keywords",
    color: "from-emerald-600/15 to-teal-600/5 border-emerald-500/15 hover:border-emerald-400/40 text-emerald-400 hover:shadow-emerald-500/5",
  },
  {
    href: "/dashboard/documents",
    icon: FolderClosed,
    title: "My Documents",
    desc: "Browse and manage your knowledge base",
    color: "from-amber-600/15 to-orange-600/5 border-amber-500/15 hover:border-amber-400/40 text-amber-400 hover:shadow-amber-500/5",
  },
];

export default function DashboardPage() {
  const [docs, setDocs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [online, setOnline] = useState(null);

  useEffect(() => {
    // Check health
    fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/health`)
      .then((r) => setOnline(r.ok))
      .catch(() => setOnline(false));

    // Fetch recent docs
    const token = localStorage.getItem("access_token");
    fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/documents/?limit=5`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((r) => r.ok ? r.json() : null)
      .then((d) => {
        if (d) {
          setDocs(d.documents || []);
          setTotal(d.total || 0);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

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

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-900 pb-6">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Workspace Overview</h1>
          <p className="text-gray-400 text-sm mt-1">
            Analyze documents and ask questions grounded in your secure knowledge base
          </p>
        </div>
        
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${
          online === true
            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
            : online === false
            ? "bg-rose-500/10 border-rose-500/20 text-rose-400"
            : "bg-gray-800 border-gray-700 text-gray-400"
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${
            online === true ? "bg-emerald-400 animate-pulse" : online === false ? "bg-rose-400" : "bg-gray-500"
          }`} />
          {online === true ? "RAG Server Online" : online === false ? "RAG Server Offline" : "Connecting…"}
        </div>
      </div>

      {/* Quick links grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {quickLinks.map((q) => {
          const Icon = q.icon;
          return (
            <Link
              key={q.href}
              href={q.href}
              className={`group bg-gradient-to-br ${q.color} border rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-black/50 flex flex-col justify-between h-44`}
            >
              <div>
                <div className="w-10 h-10 rounded-xl bg-gray-950/60 flex items-center justify-center mb-4 border border-gray-850 group-hover:scale-105 transition-transform">
                  <Icon className="w-5 h-5" />
                </div>
                <h2 className="text-base font-bold text-white mb-1.5 group-hover:text-blue-400 transition-colors">
                  {q.title}
                </h2>
                <p className="text-xs text-gray-400 leading-relaxed">{q.desc}</p>
              </div>
              <div className="flex items-center gap-1 mt-4 text-[10px] uppercase font-bold tracking-wider text-gray-500 group-hover:text-gray-300 transition-colors">
                Launch Workspace <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
              </div>
            </Link>
          );
        })}
      </div>

      {/* Recent documents */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <span>Recent Documents</span>
            {total > 0 && (
              <span className="text-[10px] uppercase px-2 py-0.5 rounded-full bg-gray-900 border border-gray-800 text-gray-500 font-semibold">
                {total} total
              </span>
            )}
          </h2>
          <Link
            href="/dashboard/documents"
            className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
          >
            Manage Documents <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="h-16 bg-gray-900/40 border border-gray-800/80 rounded-xl animate-pulse"
              />
            ))}
          </div>
        ) : docs.length === 0 ? (
          <div className="bg-gray-900/40 border border-gray-800 border-dashed rounded-2xl p-12 text-center backdrop-blur-md">
            <div className="text-4xl mb-3">📂</div>
            <p className="text-gray-300 text-sm font-semibold">Ready for upload</p>
            <p className="text-gray-500 text-xs mt-1">Get started by feeding your RAG index with documentation files.</p>
            <Link
              href="/dashboard/upload"
              className="inline-block mt-5 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 rounded-xl text-xs font-bold text-white transition-all shadow-lg shadow-blue-500/25"
            >
              Upload your first document
            </Link>
          </div>
        ) : (
          <div className="space-y-2.5">
            {docs.map((doc) => (
              <Link
                key={doc.id}
                href={`/dashboard/documents/${doc.id}`}
                className="flex items-center justify-between bg-gray-900/40 backdrop-blur-md border border-gray-850 hover:border-gray-750/80 rounded-xl px-5 py-3.5 transition-all duration-300 group hover:-translate-y-0.5"
              >
                <div className="flex items-center gap-3.5 min-w-0">
                  <div className="w-9 h-9 rounded-lg bg-gray-950 flex items-center justify-center shadow-inner text-lg">
                    📄
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm text-gray-200 font-semibold truncate group-hover:text-blue-400 transition-colors">
                      {doc.original_name}
                    </p>
                    <div className="flex items-center gap-3 text-[10px] text-gray-500 mt-0.5">
                      <span className="flex items-center gap-1">
                        <HardDrive className="w-2.5 h-2.5" />
                        {(doc.size_bytes / 1024).toFixed(1)} KB
                      </span>
                      <span>·</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-2.5 h-2.5" />
                        {new Date(doc.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                <span
                  className={`flex-shrink-0 text-[10px] uppercase tracking-wider px-2.5 py-0.5 rounded-full border font-semibold ${
                    statusBadge[doc.status] || "bg-gray-500/10 border-gray-500/20 text-gray-400"
                  }`}
                >
                  {doc.status}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* How it works */}
      <div className="bg-gray-900/30 border border-gray-900 rounded-2xl p-6 relative overflow-hidden">
        <h2 className="text-sm font-bold text-white mb-6 uppercase tracking-wider text-center">Pipeline Architecture</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 relative z-10">
          {[
            { step: "1", icon: UploadCloud, label: "Upload Documents", desc: "Drag files into ingestion portal" },
            { step: "2", icon: Cpu, label: "Chunk & Embed", desc: "Parsed and vectorized using Gemini" },
            { step: "3", icon: Database, label: "Vector Index", desc: "Indexed securely inside Qdrant" },
            { step: "4", icon: HelpCircle, label: "AI Answers", desc: "Grounded responses generated" },
          ].map((s) => {
            const SvgIcon = s.icon;
            return (
              <div key={s.step} className="space-y-3 flex flex-col items-center text-center">
                <div className="w-7 h-7 rounded-full bg-blue-600/10 border border-blue-500/25 text-blue-400 text-xs font-extrabold flex items-center justify-center">
                  {s.step}
                </div>
                <div className="w-10 h-10 rounded-xl bg-gray-950/60 border border-gray-850/80 flex items-center justify-center text-blue-400">
                  <SvgIcon className="w-5 h-5 text-blue-400/80" />
                </div>
                <div className="space-y-1">
                  <p className="text-xs font-bold text-white">{s.label}</p>
                  <p className="text-[10px] text-gray-500 leading-normal px-2">{s.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
