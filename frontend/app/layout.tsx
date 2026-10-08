import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import Providers from "./providers";
import Nav from "@/components/Nav";

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
          <Nav />
          {children}
        </Providers>
      </body>
    </html>
  );
}
