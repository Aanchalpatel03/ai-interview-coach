"use client";

import { useEffect, useState } from "react";

import { RankList } from "@/components/leaderboard/rank-list";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";
import { useAppContext } from "@/components/providers/app-provider";
import { api } from "@/lib/api";
import { LeaderboardResponse } from "@/types";

export default function LeaderboardPage() {
  const { token } = useAppContext();
  const [leaderboard, setLeaderboard] = useState<LeaderboardResponse | null>(null);

  useEffect(() => {
    if (!token) return;
    api.leaderboard(token).then(setLeaderboard).catch(() => undefined);
  }, [token]);

  return (
    <main className="mx-auto max-w-7xl px-6 pb-10">
      <Navbar />
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
        <Sidebar />
        <section className="space-y-6">
          <div className="hero-surface rounded-[2.25rem] border border-white/8 p-8 text-white shadow-panel">
            <p className="text-sm uppercase tracking-[0.3em] text-white/65">Competitive practice</p>
            <h1 className="mt-2 text-4xl font-bold">Global leaderboard</h1>
            <p className="mt-3 max-w-2xl text-white/78">
              Track your rank, compare progress, and unlock badges as your communication and presence improve.
            </p>
          </div>
          <RankList leaders={leaderboard?.leaders ?? []} currentUser={leaderboard?.current_user ?? null} />
        </section>
      </div>
    </main>
  );
}
