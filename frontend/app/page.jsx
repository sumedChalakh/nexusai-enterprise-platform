"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const features = [
  {
    icon: "📤",
    title: "Smart Upload",
    desc: "Drag & drop PDF, DOCX, TXT, CSV files up to 50MB. Auto-parsed and indexed in seconds.",
  },
  {
    icon: "🧠",
    title: "AI Chat",
    desc: "Ask questions in plain English. Get answers grounded in your actual documents with source citations.",
  },
  {
    icon: "🔍",
    title: "Semantic Search",
    desc: "Find information by meaning — not just keywords. Powered by vector embeddings.",
  },
  {
    icon: "🧩",
    title: "Chunk Explorer",
    desc: "Inspect every parsed chunk. See exactly how your documents were split and embedded.",
  },
];

const stats = [
  { label: "Doc Formats", value: "4+" },
  { label: "Max File Size", value: "50MB" },
  { label: "Search Type", value: "Vector" },
  { label: "AI Engine", value: "RAG" },
];

export default function HomePage() {
  const [online, setOnline] = useState(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/health`)
      .then((r) => setOnline(r.ok))
      .catch(() => setOnline(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 overflow-hidden">
      {/* Gradient orbs background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl" />
        <div className="absolute top-1/3 -right-32 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/3 w-72 h-72 bg-indigo-600/10 rounded-full blur-3xl" />
      </div>

      {/* Nav */}
      <nav className="relative border-b border-gray-800/60 backdrop-blur-sm bg-gray-950/80 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-sm font-bold">
              N
            </div>
            <span className="font-bold text-lg tracking-tight">NexusAI</span>
          </div>
          <div className="flex items-center gap-3">
            <span className={`flex items-center gap-1.5 text-xs px-3 py-1 rounded-full border ${
              online === true
                ? "bg-green-500/10 border-green-500/30 text-green-400"
                : online === false
                ? "bg-red-500/10 border-red-500/30 text-red-400"
                : "bg-gray-500/10 border-gray-500/30 text-gray-400"
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${
                online === true ? "bg-green-400 animate-pulse" : online === false ? "bg-red-400" : "bg-gray-400"
              }`} />
              {online === true ? "Backend online" : online === false ? "Backend offline" : "Checking…"}
            </span>
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-all hover:shadow-lg hover:shadow-blue-500/25"
            >
              Open Dashboard →
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative max-w-6xl mx-auto px-6 pt-24 pb-16 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
          Enterprise Knowledge Platform
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold leading-tight tracking-tight mb-6">
          Turn your documents into{" "}
          <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            intelligent answers
          </span>
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Upload PDFs, Word docs, and spreadsheets. Ask questions in plain English.
          Get accurate, source-cited answers powered by RAG — Retrieval-Augmented Generation.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/dashboard/upload"
            className="px-8 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 rounded-xl text-sm font-semibold transition-all hover:shadow-xl hover:shadow-blue-500/30 hover:-translate-y-0.5"
          >
            📤 Upload a Document
          </Link>
          <Link
            href="/dashboard/chat"
            className="px-8 py-3.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-sm font-semibold transition-all hover:-translate-y-0.5"
          >
            💬 Start Chatting
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-6xl mx-auto px-6 pb-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((s) => (
            <div
              key={s.label}
              className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 text-center backdrop-blur-sm"
            >
              <p className="text-2xl font-bold text-white mb-1">{s.value}</p>
              <p className="text-xs text-gray-500">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 pb-24">
        <h2 className="text-2xl font-bold text-center mb-10">Everything you need</h2>
        <div className="grid md:grid-cols-2 gap-5">
          {features.map((f) => (
            <div
              key={f.title}
              className="group bg-gray-900/60 border border-gray-800 hover:border-gray-600 rounded-2xl p-6 transition-all hover:-translate-y-1 hover:shadow-xl hover:shadow-black/40 backdrop-blur-sm"
            >
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="text-base font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-sm text-gray-600">
        NexusAI · Enterprise Knowledge Platform · Built with FastAPI + Next.js + Qdrant
      </footer>
    </div>
  );
}
