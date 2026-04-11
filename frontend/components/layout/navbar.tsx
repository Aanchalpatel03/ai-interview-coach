"use client";

import Link from "next/link";
import { BrainCircuit, LogOut } from "lucide-react";

import { useAppContext } from "@/components/providers/app-provider";

export function Navbar() {
  const { profile, setToken } = useAppContext();

  return (
    <header className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6">
      <Link href="/" className="flex items-center gap-3 text-lg font-bold tracking-tight">
        <span className="rounded-2xl bg-gradient-to-br from-signal to-coral px-3 py-2 text-white shadow-glow">
          <BrainCircuit className="h-5 w-5" />
        </span>
        <span>
          AI Interview Coach
          <span className="ml-2 rounded-full border border-white/10 bg-white/5 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-300">
            Live
          </span>
        </span>
      </Link>
      <div className="flex items-center gap-3">
        {profile && <span className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">{profile.name}</span>}
        <button className="rounded-full border border-white/10 bg-white px-4 py-2 text-sm font-medium text-slate-900" onClick={() => setToken(null)}>
          <span className="inline-flex items-center gap-2">
            <LogOut className="h-4 w-4" />
            Logout
          </span>
        </button>
      </div>
    </header>
  );
}
