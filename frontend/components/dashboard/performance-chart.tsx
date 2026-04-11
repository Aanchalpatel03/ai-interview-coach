"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function PerformanceChart({ data }: { data: Array<Record<string, string | number>> }) {
  return (
    <div className="panel h-[360px] p-6">
      <div className="mb-5">
        <h2 className="text-xl font-bold">Progress trend</h2>
        <p className="text-sm text-slate-500">Confidence, posture, and communication over time</p>
      </div>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <Tooltip />
          <Line type="monotone" dataKey="confidence" stroke="#0f766e" strokeWidth={3} />
          <Line type="monotone" dataKey="communication" stroke="#14213d" strokeWidth={3} />
          <Line type="monotone" dataKey="posture" stroke="#f97316" strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
