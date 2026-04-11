export function FinalFeedback({
  report,
}: {
  report: {
    posture_score: number;
    confidence_score: number;
    communication_score: number;
    eye_contact_score: number;
    summary: string | null;
    suggestions: string[];
  } | null;
}) {
  if (!report) return null;

  return (
    <div className="panel p-6">
      <h2 className="text-xl font-bold">Post-interview report</h2>
      <p className="mt-2 text-sm text-slate-300">{report.summary}</p>
      <div className="mt-5 grid gap-4 md:grid-cols-4">
        {[
          ["Confidence", report.confidence_score],
          ["Communication", report.communication_score],
          ["Posture", report.posture_score],
          ["Eye contact", report.eye_contact_score],
        ].map(([label, value]) => (
          <div key={label as string} className="rounded-[1.5rem] bg-gradient-to-b from-white/[0.07] to-white/[0.03] p-4">
            <p className="text-sm text-slate-400">{label}</p>
            <p className="mt-2 text-3xl font-bold">{value}</p>
          </div>
        ))}
      </div>
      <div className="mt-5 space-y-2">
        {report.suggestions.map((suggestion) => (
          <p key={suggestion} className="rounded-[1.5rem] bg-gradient-to-r from-cyan-500/10 to-blue-500/10 p-4 text-sm text-slate-200">
            {suggestion}
          </p>
        ))}
      </div>
    </div>
  );
}
