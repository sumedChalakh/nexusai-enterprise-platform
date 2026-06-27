"use client";

import DocumentList from "../../components/DocumentList";
import Link from "next/link";

export default function DocumentsPage() {
  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Documents</h1>
          <p className="text-gray-400 text-sm mt-1">
            All your uploaded and processed documents
          </p>
        </div>
        <Link
          href="/dashboard/upload"
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition-all hover:shadow-lg hover:shadow-blue-500/25"
        >
          + Upload New
        </Link>
      </div>

      <DocumentList />
    </div>
  );
}
