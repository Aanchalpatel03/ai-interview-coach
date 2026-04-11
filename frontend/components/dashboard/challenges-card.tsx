import { ChallengeItem, ChallengeSummary } from "@/types";

export function ChallengesCard({
  challenges,
  summary,
  onComplete,
}: {
  challenges: ChallengeItem[];
  summary: ChallengeSummary | null;
  onComplete: (challengeId: string) => void;
}) {
  return (
    <div className="panel p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Today's challenge</p>
          <h2 className="mt-2 text-2xl font-bold text-white">Daily practice streak</h2>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-right">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Streak</p>
          <p className="mt-1 text-2xl font-bold text-white">{summary?.streak_count ?? 0} days</p>
        </div>
      </div>
      <div className="mt-5 space-y-3">
        {challenges.map((challenge) => (
          <div key={challenge.id} className="rounded-[1.5rem] border border-white/10 bg-white/[0.03] p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{challenge.type}</p>
                <p className="mt-2 text-sm text-slate-100">{challenge.question}</p>
              </div>
              <button
                onClick={() => onComplete(challenge.id)}
                disabled={challenge.completed}
                className="rounded-full border border-white/20 px-4 py-2 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:border-emerald-500/30 disabled:bg-emerald-500/10 disabled:text-emerald-100"
              >
                {challenge.completed ? "Completed" : `Earn ${challenge.xp_reward} XP`}
              </button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 flex items-center justify-between text-sm text-slate-300">
        <span>Completion {summary?.completion_rate ?? 0}%</span>
        <span>Daily bonus +{summary?.xp_boost ?? 0} XP</span>
      </div>
    </div>
  );
}
