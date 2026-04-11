"use client";

import { motion } from "framer-motion";

export function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="panel relative overflow-hidden p-6">
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-signal via-coral to-amber-300" />
      <p className="text-sm uppercase tracking-[0.2em] text-slate-400">{label}</p>
      <div className="mt-4 flex items-end justify-between">
        <h3 className="text-5xl font-bold tracking-tight">{value}</h3>
        <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">
          improving
        </span>
      </div>
      <p className="mt-4 text-sm text-slate-400">Composite score across recent interviews</p>
    </motion.div>
  );
}
