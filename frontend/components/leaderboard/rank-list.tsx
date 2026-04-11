import { LeaderboardEntry } from "@/types";

export function RankList({ leaders, currentUser }: { leaders: LeaderboardEntry[]; currentUser: LeaderboardEntry | null }) {
  return (
    <div className="space-y-6">
      <div className="panel p-6">
        <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Global leaderboard</p>
        <div className="mt-5 space-y-3">
          {leaders.map((entry) => (
            <div key={entry.user_id} className="flex items-center justify-between rounded-[1.5rem] border border-white/10 bg-white/[0.03] px-4 py-4">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-signal to-coral text-lg font-bold text-white">
                  #{entry.rank}
                </div>
                <div>
                  <p className="font-semibold text-white">{entry.name}</p>
                  <p className="text-sm text-slate-400">{entry.level} · {entry.xp_points} XP</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-white">{entry.total_score}</p>
                <div className="mt-2 flex flex-wrap justify-end gap-2">
                  {entry.badges.map((badge) => (
                    <span key={badge} className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-slate-200">
                      {badge}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      {currentUser ? (
        <div className="accent-card rounded-[2rem] p-6 text-white shadow-panel">
          <p className="text-xs uppercase tracking-[0.25em] text-white/70">Your standing</p>
          <div className="mt-3 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-3xl font-bold">#{currentUser.rank}</h2>
              <p className="mt-2 text-white/80">{currentUser.level} · {currentUser.improvement_score} improvement score</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {currentUser.badges.map((badge) => (
                <span key={badge} className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs text-white">
                  {badge}
                </span>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
