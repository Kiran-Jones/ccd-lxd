export type ResponseOption =
  | "strongly_disagree"
  | "disagree"
  | "agree"
  | "strongly_agree";

export type Question = {
  id: number;
  statement: string;
};

export type QuestionsResponse = {
  questions: Question[];
};

export type RecommendationItem = {
  name: string;
  description: string;
  phase: string;
};

export type RecommendationResponse = {
  recommendations: RecommendationItem[];
  total_questions: number;
  completion_percent: number;
  scoring_note: string;
  prerequisite_note: string | null;
};
