import { LiveFeedback } from "@/types";

const tone = {
  green: "bg-moss",
  yellow: "bg-amber-400",
  red: "bg-coral",
};

export function FeedbackIndicators({ feedback }: { feedback: LiveFeedback | null }) {
  const current = feedback ?? {
    posture_score: 0,
    confidence_score: 0,
    eye_contact_score: 0,
    hand_movement_score: 0,
    status: "yellow",
    posture: "warning",
    eye_contact: "medium",
    confidence: 0,
    suggestions: [],
    overall_score: 0,
  };

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold">Live feedback</h3>
        <span className={`h-3 w-3 rounded-full ${tone[current.status as keyof typeof tone] ?? tone.yellow}`} />
      </div>
      <div className="mt-4 space-y-4">
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-white">Realtime coach pulse</p>
            <span className="text-sm text-slate-300">{current.overall_score}/100</span>
          </div>
          <p className="mt-2 text-sm text-slate-300">Posture {current.posture} · Eye contact {current.eye_contact}</p>
          <div className="mt-3 space-y-2">
            {current.suggestions.map((suggestion) => (
              <p key={suggestion} className="text-xs text-slate-400">{suggestion}</p>
            ))}
          </div>
        </div>
        {[
          ["Confidence", current.confidence_score],
          ["Posture", current.posture_score],
          ["Eye contact", current.eye_contact_score],
          ["Hand control", current.hand_movement_score],
        ].map(([label, value]) => (
          <div key={label}>
            <div className="mb-1 flex justify-between text-sm text-slate-500">
              <span>{label}</span>
              <span>{value}</span>
            </div>
            <div className="h-2 rounded-full bg-slate-100">
              <div className="h-2 rounded-full bg-gradient-to-r from-signal to-coral" style={{ width: `${value}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
