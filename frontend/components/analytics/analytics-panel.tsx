"use client";

import { CartesianGrid, Legend, Line, LineChart, Radar, RadarChart, PolarAngleAxis, PolarGrid, ResponsiveContainer, Tooltip } from "recharts";

import { PerformanceAnalyticsResponse, PerformancePoint } from "@/types";

export function AnalyticsPanel({
  history,
  analytics,
}: {
  history: PerformancePoint[];
  analytics: PerformanceAnalyticsResponse | null;
}) {
  const radarData = analytics
    ? Object.entries(analytics.averages).map(([metric, value]) => ({ metric: metric.replace("_", " "), value }))
    : [];

  return (
    <div className="space-y-6">
      <div className="panel h-[380px] p-6">
        <div className="mb-5">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Performance analytics</p>
          <h2 className="mt-2 text-2xl font-bold text-white">Interview trendline</h2>
        </div>
        <ResponsiveContainer width="100%" height="85%">
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(148,163,184,0.15)" />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="confidence" stroke="#22d3ee" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="communication" stroke="#3b82f6" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="posture" stroke="#10b981" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="eye_contact" stroke="#f59e0b" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="panel h-[360px] p-6">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Strength vs weakness</p>
          <ResponsiveContainer width="100%" height="90%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(148,163,184,0.2)" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: "#cbd5e1", fontSize: 11 }} />
              <Radar dataKey="value" stroke="#22d3ee" fill="#22d3ee" fillOpacity={0.25} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="panel p-6">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Coaching summary</p>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-[1.5rem] border border-emerald-500/20 bg-emerald-500/10 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-emerald-200">Strengths</p>
              <div className="mt-3 space-y-2 text-sm text-slate-100">
                {(analytics?.strengths ?? []).map((item) => <p key={item}>{item}</p>)}
              </div>
            </div>
            <div className="rounded-[1.5rem] border border-amber-500/20 bg-amber-500/10 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-amber-100">Weaknesses</p>
              <div className="mt-3 space-y-2 text-sm text-slate-100">
                {(analytics?.weaknesses ?? []).map((item) => <p key={item}>{item}</p>)}
              </div>
            </div>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Improvement</p>
              <p className="mt-2 text-3xl font-bold text-white">+{analytics?.improvement_score ?? 0}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Consistency</p>
              <p className="mt-2 text-3xl font-bold text-white">{analytics?.consistency_score ?? 0}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
