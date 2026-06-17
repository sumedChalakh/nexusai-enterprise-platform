"use client";

import { useEffect, useState } from "react";

type HealthStatus = { status: string; service: string; env: string } | null;

export default function Home() {
  const [health, setHealth] = useState<HealthStatus>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => setHealth(d))
      .catch(() => setHealth(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-8 p-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-brand-900 mb-2">NexusAI</h1>
        <p className="text-gray-500 text-lg">Enterprise Knowledge Platform</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 w-full max-w-sm">
        <p className="text-sm font-semibold text-gray-500 mb-3">API STATUS</p>
        {loading ? (
          <p className="text-gray-400 text-sm">Checking backend...</p>
        ) : health ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
              <span className="text-green-700 font-medium text-sm">Backend online</span>
            </div>
            <p className="text-xs text-gray-400">Service: {health.service}</p>
            <p className="text-xs text-gray-400">Env: {health.env}</p>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />
            <span className="text-red-600 font-medium text-sm">Backend offline</span>
          </div>
        )}
      </div>

      <p className="text-xs text-gray-400">Day 1 setup complete — ready to build 🚀</p>
    </main>
  );
}
