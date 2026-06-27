"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  UploadCloud,
  FolderClosed,
  MessageSquareCode,
  Search,
  Database,
  Layers,
  LogOut,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard, exact: true },
  { href: "/dashboard/upload", label: "Upload", icon: UploadCloud },
  { href: "/dashboard/documents", label: "Documents", icon: FolderClosed },
  { href: "/dashboard/chat", label: "AI Chat", icon: MessageSquareCode },
  { href: "/dashboard/search", label: "Search", icon: Search },
];

export default function DashboardLayout({ children }) {
  const pathname = usePathname();
  const router = useRouter();
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    // Decode JWT payload to show user info (no server verification needed)
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setUserEmail(payload.email || payload.sub || "User");
    } catch {
      setUserEmail("User");
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.replace("/login");
  };

  const isActive = (item) =>
    item.exact ? pathname === item.href : pathname.startsWith(item.href);

  return (
    <div className="flex min-h-screen bg-gray-950 font-sans antialiased text-gray-100">
      {/* Sidebar */}
      <aside className="w-60 flex-shrink-0 border-r border-gray-900 bg-gray-950/60 backdrop-blur-md flex flex-col sticky top-0 h-screen z-20">
        {/* Logo */}
        <div className="px-6 py-6 border-b border-gray-900/60">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform duration-300">
              <Layers className="w-4 h-4 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-sm text-white tracking-tight group-hover:text-blue-400 transition-colors duration-300">NexusAI</span>
              <span className="text-[9px] text-gray-500 font-semibold tracking-wider uppercase">Enterprise</span>
            </div>
          </Link>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          <p className="px-3 pb-2 text-[10px] uppercase tracking-widest text-gray-600 font-bold">
            Workspace
          </p>
          {navItems.map((item) => {
            const active = isActive(item);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 group relative ${
                  active
                    ? "bg-gradient-to-r from-blue-600/15 to-indigo-600/5 text-blue-400 border border-blue-500/15 shadow-sm shadow-blue-500/5"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-900/50 border border-transparent"
                }`}
              >
                <Icon className={`w-4 h-4 transition-transform duration-300 ${
                  active ? "text-blue-400 scale-105" : "text-gray-500 group-hover:text-gray-300 group-hover:scale-105"
                }`} />
                {item.label}
                {active && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-gradient-to-r from-blue-400 to-indigo-500 shadow-md shadow-blue-400/80" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-gray-900/60 bg-gray-950/20 space-y-3">
          {userEmail && (
            <div className="px-3 py-2 bg-gray-900/60 rounded-xl border border-gray-800/60">
              <p className="text-[9px] text-gray-600 uppercase tracking-wider font-bold mb-0.5">Signed in as</p>
              <p className="text-xs text-gray-300 font-medium truncate">{userEmail}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 w-full px-3 py-2 text-gray-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-all text-xs font-semibold"
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>
          <div className="flex items-center gap-2 text-gray-700 px-3">
            <Database className="w-3 h-3" />
            <span className="text-[10px] font-semibold tracking-wider uppercase">
              Hybrid-RAG Core
            </span>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 overflow-auto bg-gradient-to-b from-gray-950 to-gray-950/90 relative">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-20 left-1/4 w-96 h-96 bg-purple-600/5 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          {children}
        </div>
      </main>
    </div>
  );
}
