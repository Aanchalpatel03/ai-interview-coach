import {
  DashboardData,
  LeaderboardResponse,
  LiveFeedback,
  PerformanceAnalyticsResponse,
  PerformanceHistoryResponse,
  Profile,
  Question,
  TodayChallengesResponse,
} from "@/types";
import { mockApi } from "@/lib/mock-api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<T>;
}

export const api = {
  getOAuthStartUrl: (provider: "google" | "github") => {
    if (DEMO_MODE) return "/auth/oauth-callback?token=demo-token";
    return `${API_URL}/auth/oauth/${provider}/start`;
  },
  signup: async (payload: { name: string; email: string; password: string }) => {
    if (DEMO_MODE) return mockApi.signup(payload);
    try {
      return await request<{ access_token: string }>("/auth/signup", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } catch {
      return mockApi.signup(payload);
    }
  },
  login: async (payload: { email: string; password: string }) => {
    if (DEMO_MODE) return mockApi.login(payload);
    try {
      return await request<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } catch {
      return mockApi.login(payload);
    }
  },
  profile: async (token: string) => {
    if (DEMO_MODE) return mockApi.profile();
    try {
      return await request<Profile>("/auth/profile", {}, token);
    } catch {
      return mockApi.profile();
    }
  },
  dashboard: async (token: string) => {
    if (DEMO_MODE) return mockApi.dashboard();
    try {
      return await request<DashboardData>("/user/dashboard", {}, token);
    } catch {
      return mockApi.dashboard();
    }
  },
  leaderboard: async (token: string) => {
    if (DEMO_MODE) return mockApi.leaderboard();
    try {
      return await request<LeaderboardResponse>("/leaderboard", {}, token);
    } catch {
      return mockApi.leaderboard();
    }
  },
  updateLeaderboard: async (token: string) => {
    if (DEMO_MODE) return mockApi.updateLeaderboard();
    try {
      return await request<{ status: string; entry: LeaderboardResponse["leaders"][number] }>("/leaderboard/update", { method: "POST" }, token);
    } catch {
      return mockApi.updateLeaderboard();
    }
  },
  todaysChallenges: async (token: string) => {
    if (DEMO_MODE) return mockApi.todaysChallenges();
    try {
      return await request<TodayChallengesResponse>("/challenges/today", {}, token);
    } catch {
      return mockApi.todaysChallenges();
    }
  },
  completeChallenge: async (token: string, challengeId: string) => {
    if (DEMO_MODE) return mockApi.completeChallenge(challengeId);
    try {
      return await request<{ status: string; xp_awarded: number; streak_count: number }>(
        "/challenges/complete",
        { method: "POST", body: JSON.stringify({ challenge_id: challengeId }) },
        token,
      );
    } catch {
      return mockApi.completeChallenge(challengeId);
    }
  },
  performanceHistory: async (token: string) => {
    if (DEMO_MODE) return mockApi.performanceHistory();
    try {
      return await request<PerformanceHistoryResponse>("/performance/history", {}, token);
    } catch {
      return mockApi.performanceHistory();
    }
  },
  performanceAnalytics: async (token: string) => {
    if (DEMO_MODE) return mockApi.performanceAnalytics();
    try {
      return await request<PerformanceAnalyticsResponse>("/performance/analytics", {}, token);
    } catch {
      return mockApi.performanceAnalytics();
    }
  },
  uploadResume: (token: string, file: File) => {
    if (DEMO_MODE) return mockApi.uploadResume(token, file);
    const formData = new FormData();
    formData.append("file", file);
    return request<{ resume_url: string; skills: string[] }>("/resume/upload", { method: "POST", body: formData }, token).catch(() =>
      mockApi.uploadResume(token, file),
    );
  },
  analyzeResume: async (token: string) => {
    if (DEMO_MODE) return mockApi.analyzeResume();
    try {
      return await request<{ resume_url: string | null; extracted_skills: string[]; suggested_roles: string[] }>("/resume/analyze", {}, token);
    } catch {
      return mockApi.analyzeResume();
    }
  },
  startInterview: async (token: string, payload: { type: string; target_role: string; difficulty: string }) => {
    if (DEMO_MODE) return mockApi.startInterview(token, payload);
    try {
      return await request<{ id: string; type: string; status: string; start_time: string; target_role: string; difficulty: string }>(
        "/interview/start",
        { method: "POST", body: JSON.stringify(payload) },
        token,
      );
    } catch {
      return mockApi.startInterview(token, payload);
    }
  },
  getQuestion: async (token: string, interviewId: string) => {
    if (DEMO_MODE) return mockApi.getQuestion();
    try {
      return await request<Question>(`/interview/question?interview_id=${interviewId}`, {}, token);
    } catch {
      return mockApi.getQuestion();
    }
  },
  submitAnswer: async (token: string, payload: { interview_id: string; question: string; answer: string }) => {
    if (DEMO_MODE) return mockApi.submitAnswer(token, payload);
    try {
      return await request<{
        response_id: string;
        score: number;
        communication_score: number;
        structure_score: number;
        relevance_score: number;
        specificity_score: number;
        verdict: string;
        strengths: string[];
        improvements: string[];
        feedback: string;
      }>(
        "/interview/answer",
        { method: "POST", body: JSON.stringify(payload) },
        token,
      );
    } catch {
      return mockApi.submitAnswer(token, payload);
    }
  },
  sendFrame: async (token: string, payload: { interview_id: string; frame: string }) => {
    if (DEMO_MODE) return mockApi.sendFrame();
    try {
      return await request<LiveFeedback>("/video/frame", { method: "POST", body: JSON.stringify(payload) }, token);
    } catch {
      return mockApi.sendFrame();
    }
  },
  endInterview: async (token: string, interviewId: string) => {
    if (DEMO_MODE) return mockApi.endInterview();
    try {
      return await request<{ status: string; feedback_id: string }>(
        "/interview/end",
        { method: "POST", body: JSON.stringify({ interview_id: interviewId }) },
        token,
      );
    } catch {
      return mockApi.endInterview();
    }
  },
  feedback: async (token: string, interviewId: string) => {
    if (DEMO_MODE) return mockApi.feedback();
    try {
      return await request<{
        interview_id: string;
        posture_score: number;
        confidence_score: number;
        communication_score: number;
        eye_contact_score: number;
        hand_movement_score: number;
        overall_score: number;
        session_xp: number;
        improvement_delta: number;
        summary: string | null;
        suggestions: string[];
      }>(`/feedback/${interviewId}`, {}, token);
    } catch {
      return mockApi.feedback();
    }
  },
};
