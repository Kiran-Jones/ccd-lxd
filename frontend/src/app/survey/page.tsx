"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { RESPONSE_LABELS, RESPONSE_VALUES, RESULTS_SESSION_KEY, SURVEY_SESSION_KEY } from "@/lib/constants";
import { fetchQuestions, fetchRecommendations } from "@/lib/api";
import type { Question, ResponseOption } from "@/lib/types";

type AnswerMap = Record<number, number | undefined>;

function snapToValidStop(rawValue: number): number | undefined {
  if (rawValue === 1.5) {
    return undefined;
  }
  if (rawValue < 0.5) {
    return 0;
  }
  if (rawValue < 1.5) {
    return 1;
  }
  if (rawValue < 2.5) {
    return 2;
  }
  return 3;
}

export default function SurveyPage(): JSX.Element {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<AnswerMap>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();

  useEffect(() => {
    async function load(): Promise<void> {
      try {
        const questionResponse = await fetchQuestions();
        setQuestions(questionResponse.questions);

        const storedAnswers = sessionStorage.getItem(SURVEY_SESSION_KEY);
        if (storedAnswers) {
          setAnswers(JSON.parse(storedAnswers) as AnswerMap);
        }
      } catch (requestError) {
        const message = requestError instanceof Error ? requestError.message : "Failed to load survey.";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    }

    load().catch(() => setError("Failed to load survey."));
  }, []);

  const answeredCount = useMemo(() => Object.values(answers).filter((value) => value !== undefined).length, [answers]);
  const completionPercent = questions.length === 0 ? 0 : Math.round((answeredCount / questions.length) * 100);
  const allAnswered = questions.length > 0 && answeredCount === questions.length;

  function updateAnswer(questionId: number, value: number): void {
    const snapped = snapToValidStop(value);
    const next = { ...answers, [questionId]: snapped };
    setAnswers(next);
    sessionStorage.setItem(SURVEY_SESSION_KEY, JSON.stringify(next));
  }

  async function submitSurvey(): Promise<void> {
    if (!allAnswered || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const orderedAnswers = questions.map((question) => answers[question.id]);
      const responses = orderedAnswers.map((value) => RESPONSE_VALUES[value as number]) as ResponseOption[];

      const recommendationResponse = await fetchRecommendations(responses);
      sessionStorage.setItem(RESULTS_SESSION_KEY, JSON.stringify(recommendationResponse));
      router.push("/results");
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Failed to calculate recommendations.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return (
      <main className="main-container">
        <section className="page-card">
          <p>Loading survey...</p>
        </section>
      </main>
    );
  }

  return (
    <main className="main-container">
      <section className="page-card" aria-live="polite">
        <h1>Career Diagnostic Survey</h1>
        <div className="survey-sticky">
          <div className="progress-row">
            <strong>
              {answeredCount}/{questions.length} complete ({completionPercent}%)
            </strong>
          </div>
          <div className="progress-bar" aria-hidden="true">
            <span style={{ width: `${completionPercent}%` }} />
          </div>
        </div>

        {error ? <p className="alert">{error}</p> : null}

        <div className="question-list survey-list">
          {questions.map((question) => {
            const selected = answers[question.id];
            const sliderValue = selected ?? 1.5;
            return (
              <article className="question-item" key={question.id}>
                <p>
                  <strong>
                    {question.id}. {question.statement}
                  </strong>
                </p>
                <div className={`slider-wrap ${selected === undefined ? "slider-wrap-unanswered" : ""}`}>
                  <input
                    className={`slider ${selected === undefined ? "slider-unanswered" : ""}`}
                    type="range"
                    min={0}
                    max={3}
                    step={0.01}
                    value={sliderValue}
                    onChange={(event) => updateAnswer(question.id, Number(event.target.value))}
                    aria-label={`Question ${question.id}`}
                  />
                  <div className="slider-labels" aria-hidden="true">
                    <span>Strongly disagree</span>
                    <span>Disagree</span>
                    <span>Agree</span>
                    <span>Strongly agree</span>
                  </div>
                  <span className="current-value">
                    {selected === undefined ? "Select an answer" : `Selected: ${RESPONSE_LABELS[selected]}`}
                  </span>
                </div>
              </article>
            );
          })}
        </div>

        <div className="footer-actions survey-actions">
          <button type="button" className="primary-btn" disabled={!allAnswered || isSubmitting} onClick={submitSurvey}>
            {isSubmitting ? "Calculating..." : "Continue"}
          </button>
        </div>
      </section>
    </main>
  );
}
