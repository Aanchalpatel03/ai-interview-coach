export type Metric = {
  label: string;
  value: number;
};

export type DashboardData = {
  metrics: Metric[];
  progress: Array<Record<string, string | number>>;
  interviews: Array<{
    id: string;
    type: string;
    status: string;
    date: string;
    confidence_score: number;
    posture_score: number;
    communication_score: number;
  }>;
  gamification: LeaderboardEntry;
  challenge_summary: ChallengeSummary;
};

export type Profile = {
  id: string;
  name: string;
  email: string;
  role: string;
  resume_url?: string | null;
  extracted_skills: string[];
};

export type Question = {
  question: string;
  category: string;
};

export type LiveFeedback = {
  posture_score: number;
  confidence_score: number;
  eye_contact_score: number;
  hand_movement_score: number;
  status: string;
  posture: string;
  eye_contact: string;
  confidence: number;
  suggestions: string[];
  overall_score: number;
};

export type LeaderboardEntry = {
  user_id: string;
  name: string;
  total_score: number;
  rank: number;
  level: string;
  xp_points: number;
  badges: string[];
  streak_count: number;
  improvement_score: number;
};

export type LeaderboardResponse = {
  leaders: LeaderboardEntry[];
  current_user: LeaderboardEntry | null;
};

export type ChallengeItem = {
  id: string;
  date: string;
  question: string;
  type: string;
  xp_reward: number;
  completed: boolean;
  completed_at?: string | null;
};

export type ChallengeSummary = {
  streak_count: number;
  xp_boost: number;
  completion_rate: number;
};

export type TodayChallengesResponse = {
  date: string;
  challenges: ChallengeItem[];
  summary: ChallengeSummary;
};

export type PerformancePoint = {
  interview_id: string;
  date: string;
  confidence: number;
  posture: number;
  communication: number;
  eye_contact: number;
  overall_score: number;
};

export type PerformanceHistoryResponse = {
  history: PerformancePoint[];
};

export type PerformanceAnalyticsResponse = {
  averages: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  improvement_score: number;
  consistency_score: number;
};
