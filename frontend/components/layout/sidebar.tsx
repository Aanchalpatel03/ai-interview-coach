"use client";

import Link from "next/link";
import type { Route } from "next";
import { BarChart3, FileText, MessageSquareText, Trophy, UserCircle2 } from "lucide-react";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/interview", label: "Interview Room", icon: MessageSquareText },
  { href: "/leaderboard", label: "Leaderboard", icon: Trophy },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard#resume", label: "Resume", icon: FileText },
  { href: "/dashboard#profile", label: "Profile", icon: UserCircle2 },
] satisfies Array<{ href: Route; label: string; icon: typeof BarChart3 }>;

export function Sidebar() {
  return (
    <aside className="panel hidden min-h-[calc(100vh-8rem)] w-72 overflow-hidden p-6 lg:block">
      <div className="accent-card -mx-6 -mt-6 mb-6 px-6 py-6 text-white">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-white/70">Navigation</p>
        <p className="mt-3 text-2xl font-bold leading-tight">Sharpen answers. Train presence.</p>
      </div>
      <nav className="space-y-2">
        {links.map(({ href, label, icon: Icon }) => (
          <Link key={href} href={href} className="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/5 hover:text-white">
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
