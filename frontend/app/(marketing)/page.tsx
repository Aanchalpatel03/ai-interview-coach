import Link from "next/link";
import { ArrowRight, Mic, Radar, Sparkles } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="mx-auto min-h-screen max-w-7xl px-6 py-10">
      <section className="hero-surface relative grid gap-10 overflow-hidden rounded-[2.5rem] border border-white/8 p-8 text-white shadow-panel lg:grid-cols-[1.3fr_0.7fr] lg:p-12">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-white/70">Interview intelligence platform</p>
          <h1 className="mt-4 max-w-4xl text-5xl font-bold leading-[0.95] lg:text-8xl">
            Interview with <span className="bg-gradient-to-r from-signal to-coral bg-clip-text text-transparent">AI Coach</span>
          </h1>
          <p className="mt-6 max-w-2xl text-xl text-white/72">
            Run timed mock interviews, stream webcam analysis, score communication, and review progress in a single SaaS workflow.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link href="/auth/signup" className="rounded-full bg-white px-7 py-4 text-sm font-semibold text-slate-900 shadow-[0_18px_45px_rgba(255,255,255,0.14)]">
              Start free session
            </Link>
            <Link href="/auth/login" className="rounded-full border border-white/20 bg-white/10 px-7 py-4 text-sm font-semibold text-white backdrop-blur">
              Login <ArrowRight className="ml-2 inline h-4 w-4" />
            </Link>
          </div>
        </div>
        <div className="grid gap-4">
          {[
            { icon: Sparkles, title: "AI question engine", copy: "HR, technical, stress, and resume-tailored prompts." },
            { icon: Radar, title: "Realtime video scoring", copy: "Confidence, eye contact, posture, and hand movement." },
            { icon: Mic, title: "Actionable feedback", copy: "Post-interview summaries and progress charts." },
          ].map(({ icon: Icon, title, copy }) => (
            <div key={title} className="rounded-3xl border border-white/10 bg-white/[0.05] p-6 backdrop-blur">
              <Icon className="h-6 w-6" />
              <h3 className="mt-4 text-xl font-bold">{title}</h3>
              <p className="mt-2 text-sm text-white/72">{copy}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
