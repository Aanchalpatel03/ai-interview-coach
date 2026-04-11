export function InterviewHistory({
  interviews,
}: {
  interviews: Array<{
    id: string;
    type: string;
    status: string;
    date: string;
    confidence_score: number;
    posture_score: number;
    communication_score: number;
  }>;
}) {
  return (
    <div className="panel p-6">
      <h2 className="text-xl font-bold">Recent interviews</h2>
      <div className="mt-5 space-y-3">
        {interviews.map((item) => (
          <div key={item.id} className="rounded-[1.5rem] border border-white/8 bg-gradient-to-r from-white/[0.05] to-white/[0.02] p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold capitalize">{item.type} interview</p>
                <p className="text-sm text-slate-400">{new Date(item.date).toLocaleString()}</p>
              </div>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.2em] text-slate-300">{item.status}</span>
            </div>
            <p className="mt-3 text-sm text-slate-300">
              Confidence {item.confidence_score} • Posture {item.posture_score} • Communication {item.communication_score}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
