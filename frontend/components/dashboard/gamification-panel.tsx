import { LeaderboardEntry } from "@/types";

export function GamificationPanel({ entry }: { entry: LeaderboardEntry | null }) {
  if (!entry) return null;

  return (
    <div className="panel p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Gamification</p>
          <h2 className="mt-2 text-2xl font-bold text-white">Level {entry.level}</h2>
          <p className="mt-2 text-sm text-slate-300">Rank #{entry.rank} globally with {entry.xp_points} XP.</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-right">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Composite score</p>
          <p className="mt-1 text-3xl font-bold text-white">{entry.total_score}</p>
        </div>
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Daily streak</p>
          <p className="mt-2 text-2xl font-bold text-white">{entry.streak_count} days</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Improvement</p>
          <p className="mt-2 text-2xl font-bold text-white">+{entry.improvement_score}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Badges</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {entry.badges.map((badge) => (
              <span key={badge} className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-100">
                {badge}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
