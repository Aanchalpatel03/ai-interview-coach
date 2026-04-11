"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { ChallengesCard } from "@/components/dashboard/challenges-card";
import { GamificationPanel } from "@/components/dashboard/gamification-panel";
import { InterviewHistory } from "@/components/dashboard/interview-history";
import { MetricCard } from "@/components/dashboard/metric-card";
import { PerformanceChart } from "@/components/dashboard/performance-chart";
import { ResumePanel } from "@/components/dashboard/resume-panel";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";
import { useAppContext } from "@/components/providers/app-provider";
import { api } from "@/lib/api";
import { ChallengeItem, ChallengeSummary, DashboardData } from "@/types";

export default function DashboardPage() {
  const { token, profile } = useAppContext();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [challengeState, setChallengeState] = useState<{ challenges: ChallengeItem[]; summary: ChallengeSummary | null }>({
    challenges: [],
    summary: null,
  });
  const [resumeInfo, setResumeInfo] = useState<{ resume_url: string | null; extracted_skills: string[]; suggested_roles: string[] }>({
    resume_url: null,
    extracted_skills: [],
    suggested_roles: [],
  });

  useEffect(() => {
    if (!token) return;
    api.dashboard(token).then(setDashboard).catch(console.error);
    api.todaysChallenges(token)
      .then((payload) => setChallengeState({ challenges: payload.challenges, summary: payload.summary }))
      .catch(() => undefined);
    api.analyzeResume(token).then(setResumeInfo).catch(() => undefined);
  }, [token]);

  async function handleUpload(file: File) {
    if (!token) return;
    await api.uploadResume(token, file);
    const next = await api.analyzeResume(token);
    setResumeInfo(next);
  }

  async function handleCompleteChallenge(challengeId: string) {
    if (!token) return;
    await api.completeChallenge(token, challengeId);
    const [nextChallenges, nextDashboard] = await Promise.all([api.todaysChallenges(token), api.dashboard(token)]);
    setChallengeState({ challenges: nextChallenges.challenges, summary: nextChallenges.summary });
    setDashboard(nextDashboard);
  }

  return (
    <main className="mx-auto max-w-7xl px-6 pb-10">
      <Navbar />
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
        <Sidebar />
        <section className="space-y-6">
          <div className="hero-surface flex flex-col justify-between gap-6 rounded-[2.25rem] border border-white/8 p-8 text-white shadow-panel lg:flex-row">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-white/65">Performance cockpit</p>
              <h1 className="mt-2 text-4xl font-bold">Welcome back, {profile?.name ?? "Candidate"}.</h1>
              <p className="mt-3 max-w-2xl text-white/78">
                Review recent sessions, track communication trends, and start a new interview with tailored prompts.
              </p>
            </div>
            <Link href="/interview" className="self-start rounded-full bg-white px-6 py-4 text-sm font-semibold text-slate-900">
              Start interview
            </Link>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {dashboard?.metrics.map((metric) => <MetricCard key={metric.label} {...metric} />)}
          </div>

          <GamificationPanel entry={dashboard?.gamification ?? null} />

          <ChallengesCard
            challenges={challengeState.challenges}
            summary={challengeState.summary ?? dashboard?.challenge_summary ?? null}
            onComplete={handleCompleteChallenge}
          />

          <PerformanceChart data={dashboard?.progress ?? []} />

          <InterviewHistory interviews={dashboard?.interviews ?? []} />

          <ResumePanel
            resumeUrl={resumeInfo.resume_url ?? profile?.resume_url}
            skills={resumeInfo.extracted_skills.length ? resumeInfo.extracted_skills : profile?.extracted_skills ?? []}
            roles={resumeInfo.suggested_roles}
            onUpload={handleUpload}
          />
        </section>
      </div>
    </main>
  );
}
