import type { QuestionsResponse, RecommendationResponse, ResponseOption } from "@/lib/types";

const API_BASE_URL = "http://localhost:8000";

export async function fetchQuestions(): Promise<QuestionsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/questions`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load survey questions.");
  }
  return response.json() as Promise<QuestionsResponse>;
}

export async function fetchRecommendations(
  responses: ResponseOption[],
): Promise<RecommendationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ responses }),
  });

  if (!response.ok) {
    throw new Error("Failed to calculate recommendations.");
  }

  return response.json() as Promise<RecommendationResponse>;
}
