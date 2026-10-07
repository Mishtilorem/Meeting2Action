import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "Meeting to Action Agent",
  description: "Transform meeting recordings and transcripts into verified action items with human approval.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <Providers>
          <header className="border-b bg-white shadow-sm">
            <div className="mx-auto flex max-w-4xl items-center justify-between p-4">
              <Link href="/" className="text-xl font-bold tracking-tight text-gray-900">
                Meeting<span className="text-blue-600">2Action</span>
              </Link>
              <nav className="flex gap-4 font-medium text-sm">
                <Link href="/" className="hover:text-blue-600">
                  New Meeting
                </Link>
                <Link href="/history" className="hover:text-blue-600">
                  History
                </Link>
              </nav>
            </div>
          </header>
          {children}
        </Providers>
      </body>
    </html>
  );
}
