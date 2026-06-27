import "./globals.css";

export const metadata = {
  title: "NexusAI — Enterprise Knowledge Platform",
  description: "Upload documents, search semantically, and get AI-powered answers grounded in your data.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-gray-950 text-gray-100 antialiased">{children}</body>
    </html>
  );
}
