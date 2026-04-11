"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";
import { useAppContext } from "@/components/providers/app-provider";
import { api } from "@/lib/api";
import { PerformanceAnalyticsResponse, PerformancePoint } from "@/types";

const AnalyticsPanel = dynamic(() => import("@/components/analytics/analytics-panel").then((mod) => mod.AnalyticsPanel), {
  ssr: false,
});

export default function AnalyticsPage() {
  const { token } = useAppContext();
  const [history, setHistory] = useState<PerformancePoint[]>([]);
  const [analytics, setAnalytics] = useState<PerformanceAnalyticsResponse | null>(null);

  useEffect(() => {
    if (!token) return;
    api.performanceHistory(token).then((payload) => setHistory(payload.history)).catch(() => undefined);
    api.performanceAnalytics(token).then(setAnalytics).catch(() => undefined);
  }, [token]);

  return (
    <main className="mx-auto max-w-7xl px-6 pb-10">
      <Navbar />
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
        <Sidebar />
        <section className="space-y-6">
          <div className="hero-surface rounded-[2.25rem] border border-white/8 p-8 text-white shadow-panel">
            <p className="text-sm uppercase tracking-[0.3em] text-white/65">Deep analytics</p>
            <h1 className="mt-2 text-4xl font-bold">Performance history</h1>
            <p className="mt-3 max-w-2xl text-white/78">
              Review how confidence, posture, communication, and eye contact change over time.
            </p>
          </div>
          <AnalyticsPanel history={history} analytics={analytics} />
        </section>
      </div>
    </main>
  );
}
