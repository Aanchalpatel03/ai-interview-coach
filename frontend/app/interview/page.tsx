"use client";

import { useEffect, useState } from "react";

import { ChatPanel } from "@/components/interview/chat-panel";
import { FinalFeedback } from "@/components/interview/final-feedback";
import { FeedbackIndicators } from "@/components/interview/feedback-indicators";
import { VideoFeed } from "@/components/interview/video-feed";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";
import { useAppContext } from "@/components/providers/app-provider";
import { api } from "@/lib/api";
import { LiveFeedback } from "@/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/api/ml/ws/ml-feedback";

export default function InterviewPage() {
  const { token, profile } = useAppContext();
  const [interviewId, setInterviewId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState<{
    score: number;
    communication_score: number;
    structure_score: number;
    relevance_score: number;
    specificity_score: number;
    verdict: string;
    strengths: string[];
    improvements: string[];
    feedback: string;
  } | null>(null);
  const [feedback, setFeedback] = useState<LiveFeedback | null>(null);
  const [finalReport, setFinalReport] = useState<{
    posture_score: number;
    confidence_score: number;
    communication_score: number;
    eye_contact_score: number;
    summary: string | null;
    suggestions: string[];
  } | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [questionCount, setQuestionCount] = useState(0);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);

  useEffect(() => {
    if (!interviewId) return;
    const separator = WS_URL.includes("?") ? "&" : "?";
    const ws = new WebSocket(`${WS_URL}${separator}interview_id=${encodeURIComponent(interviewId)}`);
    ws.onmessage = (event) => setFeedback(JSON.parse(event.data) as LiveFeedback);
    const pulse = window.setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 2500);
    return () => {
      window.clearInterval(pulse);
      ws.close();
    };
  }, [interviewId]);

  useEffect(() => {
    if (!interviewId) {
      setElapsed(0);
      return;
    }
    const timer = window.setInterval(() => setElapsed((current) => current + 1), 1000);
    return () => window.clearInterval(timer);
  }, [interviewId]);

  async function startInterview() {
    if (!token || interviewId || isLoadingQuestion) return;
    setIsLoadingQuestion(true);
    const started = await api.startInterview(token, {
      type: "technical",
      target_role: profile?.extracted_skills?.includes("react") ? "Frontend Engineer" : "Software Engineer",
      difficulty: "mid",
    });
    try {
      setFinalReport(null);
      setEvaluation(null);
      setFeedback(null);
      setAnswer("");
      setInterviewId(started.id);
      setQuestionCount(0);
      await loadNextQuestion(started.id, "", 0);
    } finally {
      setIsLoadingQuestion(false);
    }
  }

  async function handleSubmitAnswer() {
    if (!token || !interviewId || !question || !answer.trim() || isSubmittingAnswer) return;
    setIsSubmittingAnswer(true);
    try {
      const currentQuestion = question;
      const result = await api.submitAnswer(token, { interview_id: interviewId, question: currentQuestion, answer });
      setEvaluation(result);
      setAnswer("");
      await loadNextQuestion(interviewId, currentQuestion, questionCount + 1);
    } finally {
      setIsSubmittingAnswer(false);
    }
  }

  async function handleFrame(frame: string) {
    if (!token || !interviewId) return;
    const result = await api.sendFrame(token, { interview_id: interviewId, frame });
    setFeedback(result);
  }

  async function finishInterview() {
    if (!token || !interviewId) return;
    await api.endInterview(token, interviewId);
    const report = await api.feedback(token, interviewId);
    setFinalReport(report);
    setInterviewId(null);
    setQuestion("");
    setQuestionCount(0);
  }

  async function loadNextQuestion(activeInterviewId: string, previousQuestion: string, nextCount: number) {
    if (!token) return;

    let nextQuestion = await api.getQuestion(token, activeInterviewId);
    if (previousQuestion) {
      let attempts = 0;
      while (attempts < 3 && nextQuestion.question === previousQuestion) {
        nextQuestion = await api.getQuestion(token, activeInterviewId);
        attempts += 1;
      }
    }

    setQuestion(nextQuestion.question);
    setQuestionCount(nextCount);
  }

  return (
    <main className="mx-auto max-w-7xl px-6 pb-10">
      <Navbar />
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
        <Sidebar />
        <section className="space-y-6">
          <div className="hero-surface flex flex-wrap items-center justify-between gap-4 rounded-[2.25rem] border border-white/8 p-6 text-white shadow-panel">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-white/65">Realtime interview room</p>
              <h1 className="mt-2 text-3xl font-bold">Live AI interviewer</h1>
              <p className="mt-2 text-sm text-white/75">Session timer: {Math.floor(elapsed / 60)}m {elapsed % 60}s</p>
              <p className="mt-1 text-sm text-white/60">Questions completed: {questionCount}</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={startInterview}
                disabled={Boolean(interviewId) || isLoadingQuestion}
                className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-900 disabled:cursor-not-allowed disabled:bg-white/60"
              >
                {isLoadingQuestion ? "Starting..." : interviewId ? "Session active" : "Start session"}
              </button>
              <button
                onClick={finishInterview}
                disabled={!interviewId}
                className="rounded-full border border-white/30 bg-white/10 px-6 py-3 text-sm font-semibold text-white backdrop-blur disabled:cursor-not-allowed disabled:border-white/10 disabled:text-white/40"
              >
                End session
              </button>
            </div>
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
            <div className="space-y-6">
              <VideoFeed onFrame={handleFrame} feedback={feedback} />
              <ChatPanel
                question={question}
                answer={answer}
                onChange={setAnswer}
                onSubmit={handleSubmitAnswer}
                evaluation={evaluation}
                isSubmitting={isSubmittingAnswer}
                canSubmit={Boolean(interviewId && question && answer.trim())}
              />
            </div>
            <FeedbackIndicators feedback={feedback} />
          </div>

          <FinalFeedback report={finalReport} />
        </section>
      </div>
    </main>
  );
}
