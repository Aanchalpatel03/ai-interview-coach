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

const PROFILE_KEY = "demo-profile";
const TOKEN = "demo-token";
const INTERVIEW_STATE_KEY = "demo-interview-state";
const CHALLENGE_PROGRESS_KEY = "demo-challenge-progress";
const QUESTION_BANK: Record<string, string[]> = {
  technical: [
    "Explain a recent system you built and the tradeoffs you made.",
    "How would you reduce latency in a React and FastAPI application?",
    "Describe a production incident and how you resolved it.",
    "How would you design a scalable notification service for web and mobile users?",
    "Tell me about a time you improved application performance. What did you measure before and after?",
    "How do you decide between shipping quickly and refactoring for long-term maintainability?",
    "Describe how you would debug intermittent API failures in production.",
    "What architectural changes would you make if your application traffic grew tenfold?",
  ],
  hr: [
    "Tell me about yourself.",
    "Describe a time you handled conflict in a team.",
    "Why do you want this role?",
    "Tell me about a project you are proud of and why it mattered.",
  ],
};

type InterviewState = {
  currentId: string | null;
  askedQuestions: string[];
  interviewType: string;
  targetRole: string | null;
};

function getProfile(): Profile {
  if (typeof window === "undefined") {
    return {
      id: "demo-user",
      name: "Demo Candidate",
      email: "demo@example.com",
      role: "user",
      resume_url: null,
      extracted_skills: ["react", "fastapi", "system design"],
    };
  }

  const stored = window.localStorage.getItem(PROFILE_KEY);
  if (stored) return JSON.parse(stored) as Profile;

  const profile: Profile = {
    id: "demo-user",
    name: "Demo Candidate",
    email: "demo@example.com",
    role: "user",
    resume_url: null,
    extracted_skills: ["react", "fastapi", "system design"],
  };
  window.localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
  return profile;
}

function setProfile(profile: Profile) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
  }
}

function getInterviewState(): InterviewState {
  if (typeof window === "undefined") {
    return { currentId: null, askedQuestions: [], interviewType: "technical", targetRole: null };
  }

  const stored = window.localStorage.getItem(INTERVIEW_STATE_KEY);
  if (!stored) {
    return { currentId: null, askedQuestions: [], interviewType: "technical", targetRole: null };
  }

  return JSON.parse(stored) as InterviewState;
}

function setInterviewState(state: InterviewState) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(INTERVIEW_STATE_KEY, JSON.stringify(state));
  }
}

function getChallengeProgress(): Record<string, boolean> {
  if (typeof window === "undefined") return {};
  const stored = window.localStorage.getItem(CHALLENGE_PROGRESS_KEY);
  return stored ? (JSON.parse(stored) as Record<string, boolean>) : {};
}

function setChallengeProgress(progress: Record<string, boolean>) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(CHALLENGE_PROGRESS_KEY, JSON.stringify(progress));
  }
}

function normalizeQuestion(question: string) {
  const separator = " Frame your answer for a ";
  return question.includes(separator) ? question.split(separator, 1)[0].trim() : question.trim();
}

function getNextQuestion(state: InterviewState): Question {
  const profile = getProfile();
  const bucket = [
    ...(QUESTION_BANK[state.interviewType] ?? QUESTION_BANK.technical),
    ...(profile.extracted_skills.includes("react")
      ? [
          "How do you prevent unnecessary re-renders in a complex React screen without overusing memoization?",
          "Describe a frontend architecture decision you made in React that improved maintainability.",
        ]
      : []),
    ...(profile.extracted_skills.includes("fastapi")
      ? [
          "How would you structure a FastAPI service for long-term maintainability and testability?",
          "Describe how you would handle async workloads and external service failures in FastAPI.",
        ]
      : []),
    ...(profile.extracted_skills.includes("system design")
      ? [
          "Design an interview coaching platform that supports realtime video feedback for thousands of concurrent users.",
        ]
      : []),
  ];

  const deduped = Array.from(new Set(bucket));
  const asked = new Set(state.askedQuestions.map(normalizeQuestion));
  const nextBaseQuestion = deduped.find((question) => !asked.has(question)) ?? deduped[state.askedQuestions.length % deduped.length];
  const question = state.targetRole ? `${nextBaseQuestion} Frame your answer for a ${state.targetRole} context.` : nextBaseQuestion;
  const category = profile.extracted_skills.some((skill) => nextBaseQuestion.toLowerCase().includes(skill)) ? "skill-based" : state.interviewType;
  state.askedQuestions = [...state.askedQuestions, question];
  setInterviewState(state);
  return { question, category };
}

export const mockApi = {
  async signup(payload: { name: string; email: string; password: string }) {
    const profile = { ...getProfile(), name: payload.name, email: payload.email };
    setProfile(profile);
    return { access_token: TOKEN };
  },
  async login(_: { email: string; password: string }) {
    return { access_token: TOKEN };
  },
  async profile() {
    return getProfile();
  },
  async dashboard(): Promise<DashboardData> {
    return {
      metrics: [
        { label: "Confidence", value: 81 },
        { label: "Communication", value: 78 },
        { label: "Posture", value: 74 },
      ],
      progress: [
        { name: "Apr 03", confidence: 66, communication: 62, posture: 58 },
        { name: "Apr 05", confidence: 72, communication: 69, posture: 64 },
        { name: "Apr 07", confidence: 78, communication: 75, posture: 71 },
        { name: "Apr 08", confidence: 81, communication: 78, posture: 74 },
      ],
      interviews: [
        {
          id: "int-demo-1",
          type: "technical",
          status: "completed",
          date: new Date().toISOString(),
          confidence_score: 81,
          posture_score: 74,
          communication_score: 78,
        },
      ],
      gamification: {
        user_id: "demo-user",
        name: getProfile().name,
        total_score: 84,
        rank: 8,
        level: "Advanced",
        xp_points: 420,
        badges: ["Confident Speaker", "Active Learner"],
        streak_count: 4,
        improvement_score: 18,
      },
      challenge_summary: {
        streak_count: 4,
        xp_boost: 15,
        completion_rate: 33.3,
      },
    };
  },
  async leaderboard(): Promise<LeaderboardResponse> {
    return {
      leaders: [
        { user_id: "u1", name: "Priya", total_score: 92, rank: 1, level: "Expert", xp_points: 980, badges: ["Perfect Posture", "Confident Speaker"], streak_count: 9, improvement_score: 26 },
        { user_id: "u2", name: "Arjun", total_score: 89, rank: 2, level: "Expert", xp_points: 910, badges: ["Consistent Challenger"], streak_count: 8, improvement_score: 21 },
        { user_id: "demo-user", name: getProfile().name, total_score: 84, rank: 8, level: "Advanced", xp_points: 420, badges: ["Confident Speaker", "Active Learner"], streak_count: 4, improvement_score: 18 },
      ],
      current_user: { user_id: "demo-user", name: getProfile().name, total_score: 84, rank: 8, level: "Advanced", xp_points: 420, badges: ["Confident Speaker", "Active Learner"], streak_count: 4, improvement_score: 18 },
    };
  },
  async updateLeaderboard() {
    const data = await this.leaderboard();
    return { status: "updated", entry: data.current_user! };
  },
  async todaysChallenges(): Promise<TodayChallengesResponse> {
    const progress = getChallengeProgress();
    const today = new Date().toISOString().slice(0, 10);
    const challenges = [
      { id: "challenge-hr", date: today, question: "Describe a time you handled difficult feedback well.", type: "hr", xp_reward: 25, completed: Boolean(progress["challenge-hr"]) },
      { id: "challenge-tech", date: today, question: "Explain how you would improve a slow API without adding long-term maintenance debt.", type: "technical", xp_reward: 25, completed: Boolean(progress["challenge-tech"]) },
      { id: "challenge-behavioral", date: today, question: "Record a 90-second STAR answer about resolving conflict and finish with a measurable outcome.", type: "behavioral", xp_reward: 35, completed: Boolean(progress["challenge-behavioral"]) },
    ];
    const completedCount = challenges.filter((item) => item.completed).length;
    return {
      date: today,
      challenges,
      summary: {
        streak_count: 4,
        xp_boost: completedCount === challenges.length ? 15 : 0,
        completion_rate: (completedCount / challenges.length) * 100,
      },
    };
  },
  async completeChallenge(challengeId: string) {
    const progress = getChallengeProgress();
    progress[challengeId] = true;
    setChallengeProgress(progress);
    return { status: "completed", xp_awarded: challengeId === "challenge-behavioral" ? 35 : 25, streak_count: 4 };
  },
  async performanceHistory(): Promise<PerformanceHistoryResponse> {
    return {
      history: [
        { interview_id: "int-1", date: "2026-04-03T10:00:00.000Z", confidence: 66, posture: 58, communication: 62, eye_contact: 60, overall_score: 63 },
        { interview_id: "int-2", date: "2026-04-05T10:00:00.000Z", confidence: 72, posture: 64, communication: 69, eye_contact: 67, overall_score: 69 },
        { interview_id: "int-3", date: "2026-04-07T10:00:00.000Z", confidence: 78, posture: 71, communication: 75, eye_contact: 72, overall_score: 75 },
        { interview_id: "int-4", date: "2026-04-09T10:00:00.000Z", confidence: 81, posture: 74, communication: 78, eye_contact: 73, overall_score: 78 },
      ],
    };
  },
  async performanceAnalytics(): Promise<PerformanceAnalyticsResponse> {
    return {
      averages: { confidence: 74.3, posture: 66.8, communication: 71, eye_contact: 68, overall_score: 71.3 },
      strengths: ["Confidence is becoming a reliable strength in live sessions.", "You are sustaining visible progress over time."],
      weaknesses: ["Eye contact is the biggest opportunity in your live delivery.", "Turn repeated feedback into one concrete practice goal each week."],
      improvement_score: 18,
      consistency_score: 84,
    };
  },
  async uploadResume(_: string, file: File) {
    const profile = { ...getProfile(), resume_url: `demo://resumes/${file.name}`, extracted_skills: ["react", "nextjs", "fastapi", "docker"] };
    setProfile(profile);
    return { resume_url: profile.resume_url!, skills: profile.extracted_skills };
  },
  async analyzeResume() {
    const profile = getProfile();
    return {
      resume_url: profile.resume_url ?? null,
      extracted_skills: profile.extracted_skills,
      suggested_roles: ["Frontend Engineer", "Backend Engineer", "Platform Engineer"],
    };
  },
  async startInterview(_: string, payload: { type: string; target_role: string; difficulty: string }) {
    setInterviewState({
      currentId: "demo-interview",
      askedQuestions: [],
      interviewType: payload.type,
      targetRole: payload.target_role,
    });
    return {
      id: "demo-interview",
      type: payload.type,
      status: "active",
      start_time: new Date().toISOString(),
      target_role: payload.target_role,
      difficulty: payload.difficulty,
    };
  },
  async getQuestion(): Promise<Question> {
    return getNextQuestion(getInterviewState());
  },
  async submitAnswer(_: string, payload: { interview_id: string; question: string; answer: string }) {
    const lengthScore = Math.min(100, 45 + payload.answer.split(" ").length);
    return {
      response_id: "demo-response",
      score: lengthScore,
      communication_score: Math.max(60, lengthScore - 4),
      structure_score: 76,
      relevance_score: 79,
      specificity_score: 68,
      verdict: "Decent answer",
      strengths: ["You answered the prompt directly.", "The response has a usable overall flow."],
      improvements: ["Add one measurable result.", "Explain one concrete tradeoff or decision."],
      feedback: "Demo mode feedback: strong structure. Add one quantified result and one clearer tradeoff to make the answer feel more senior.",
    };
  },
  async sendFrame(): Promise<LiveFeedback> {
    return {
      posture_score: 76,
      confidence_score: 82,
      eye_contact_score: 73,
      hand_movement_score: 69,
      status: "green",
      posture: "good",
      eye_contact: "medium",
      confidence: 82,
      suggestions: ["Delivery looks stable. Keep the same pace and presence."],
      overall_score: 79,
    };
  },
  async endInterview() {
    const state = getInterviewState();
    setInterviewState({ ...state, currentId: null, askedQuestions: [] });
    return { status: "completed", feedback_id: "demo-feedback" };
  },
  async feedback() {
    return {
      interview_id: "demo-interview",
      posture_score: 76,
      confidence_score: 82,
      communication_score: 79,
      eye_contact_score: 73,
      hand_movement_score: 69,
      overall_score: 80,
      session_xp: 92,
      improvement_delta: 14,
      summary: "Demo report: your answer structure was solid and your delivery looked composed. The biggest gains would come from sharper metrics and steadier eye contact.",
      suggestions: [
        "Use the STAR format explicitly for behavioral prompts",
        "Keep your shoulders square to the camera",
        "Close each answer with a measurable outcome",
      ],
    };
  },
};
