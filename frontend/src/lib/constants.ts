import type { ResponseOption } from "@/lib/types";

export const RESPONSE_LABELS: Record<number, string> = {
  0: "Strongly disagree",
  1: "Disagree",
  2: "Agree",
  3: "Strongly agree",
};

export const RESPONSE_VALUES: Record<number, ResponseOption> = {
  0: "strongly_disagree",
  1: "disagree",
  2: "agree",
  3: "strongly_agree",
};

export const SURVEY_SESSION_KEY = "dccd-survey-responses";
export const RESULTS_SESSION_KEY = "dccd-survey-results";
