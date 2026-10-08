"use client";

import { Suspense } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
    { href: "/", label: "New meeting" },
    { href: "/history", label: "History" },
];

const base = "rounded-lg px-3 py-1.5 text-sm font-medium transition-colors";
const idle = "text-slate-600 hover:bg-slate-100 hover:text-slate-900";

function NavLinks() {
    const pathname = usePathname();
    return (
        <nav className="flex items-center gap-1">
            {links.map((l) => {
                const active = l.href === "/" ? pathname === "/" : pathname.startsWith(l.href);
                return (
                    <Link
                        key={l.href}
                        href={l.href}
                        className={`${base} ${active ? "bg-blue-600 text-white" : idle}`}
                    >
                        {l.label}
                    </Link>
                );
            })}
        </nav>
    );
}

function NavLinksFallback() {
    return (
        <nav className="flex items-center gap-1">
            {links.map((l) => (
                <Link key={l.href} href={l.href} className={`${base} ${idle}`}>
                    {l.label}
                </Link>
            ))}
        </nav>
    );
}

export default function Nav() {
    return (
        <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
            <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
                <Link href="/" className="text-xl font-bold tracking-tight text-slate-900">
                    Meeting2<span className="text-blue-600">Action</span>
                </Link>
                <Suspense fallback={<NavLinksFallback />}>
                    <NavLinks />
                </Suspense>
            </div>
        </header>
    );
}