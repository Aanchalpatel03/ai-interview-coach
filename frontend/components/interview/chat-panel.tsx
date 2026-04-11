export function ChatPanel({
  question,
  answer,
  onChange,
  onSubmit,
  evaluation,
  isSubmitting,
  canSubmit,
}: {
  question: string;
  answer: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  evaluation: {
    score: number;
    communication_score: number;
    structure_score: number;
    relevance_score: number;
    specificity_score: number;
    verdict: string;
    strengths: string[];
    improvements: string[];
    feedback: string;
  } | null;
  isSubmitting: boolean;
  canSubmit: boolean;
}) {
  return (
    <div className="panel p-6">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Current question</p>
      <h2 className="mt-2 text-2xl font-bold leading-snug text-white">{question || "Start a session to receive a question."}</h2>
      <textarea
        value={answer}
        onChange={(event) => onChange(event.target.value)}
        className="mt-5 h-44 w-full rounded-2xl border border-white/10 bg-white/[0.03] p-4 outline-none ring-0"
        placeholder="Type or paste your answer here while speaking it aloud."
        disabled={!question || isSubmitting}
      />
      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={onSubmit}
          disabled={!canSubmit || isSubmitting}
          className="rounded-full bg-gradient-to-r from-signal to-coral px-6 py-3 text-sm font-semibold text-white shadow-glow disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Submitting..." : "Submit answer"}
        </button>
        {!question ? <p className="text-sm text-slate-400">Start a live session to unlock the answer box.</p> : null}
      </div>
      {evaluation && (
        <div className="mt-5 space-y-4 rounded-[1.5rem] bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 p-4 text-sm text-slate-200">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Answer review</p>
              <p className="mt-1 text-lg font-semibold text-white">{evaluation.verdict}</p>
            </div>
            <div className="flex gap-2">
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">Overall {evaluation.score}</span>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">Communication {evaluation.communication_score}</span>
            </div>
          </div>
          <p><strong className="text-white">AI feedback:</strong> {evaluation.feedback}</p>
          <div className="grid gap-3 md:grid-cols-3">
            {[
              ["Structure", evaluation.structure_score],
              ["Relevance", evaluation.relevance_score],
              ["Specificity", evaluation.specificity_score],
            ].map(([label, value]) => (
              <div key={label as string} className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
                <p className="mt-2 text-2xl font-bold text-white">{value}</p>
              </div>
            ))}
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-emerald-200">What went well</p>
              <div className="mt-2 space-y-2">
                {evaluation.strengths.map((item) => (
                  <p key={item} className="text-sm text-slate-100">{item}</p>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-amber-500/20 bg-amber-500/10 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-amber-200">How to improve</p>
              <div className="mt-2 space-y-2">
                {evaluation.improvements.map((item) => (
                  <p key={item} className="text-sm text-slate-100">{item}</p>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
