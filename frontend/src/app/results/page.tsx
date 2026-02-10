"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ResultsFlowDiagram } from "@/components/results/ResultsFlowDiagram";
import { RESULTS_SESSION_KEY, SURVEY_SESSION_KEY } from "@/lib/constants";
import type { RecommendationResponse } from "@/lib/types";

export default function ResultsPage(): JSX.Element {
  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const router = useRouter();

  useEffect(() => {
    const raw = sessionStorage.getItem(RESULTS_SESSION_KEY);
    if (!raw) {
      router.replace("/");
      return;
    }

    setResults(JSON.parse(raw) as RecommendationResponse);
  }, [router]);

  function retakeSurvey(): void {
    sessionStorage.removeItem(RESULTS_SESSION_KEY);
    sessionStorage.removeItem(SURVEY_SESSION_KEY);
    router.push("/survey");
  }

  if (!results) {
    return (
      <main className="main-container">
        <section className="page-card">
          <p>Loading results...</p>
        </section>
      </main>
    );
  }

  return (
    <main className="main-container">
      <section className="page-card results-shell">
        <div className="results-hero">
          <p className="roadmap-kicker">Your Career Design Roadmap</p>
          <h1>Your Recommended Activities</h1>
          <p>{results.scoring_note}</p>
          {results.prerequisite_note ? <p className="alert">{results.prerequisite_note}</p> : null}
        </div>

        <ResultsFlowDiagram recommendations={results.recommendations} />

        <div className="alert results-next-step">
          Next step: Meet with a Career Design intern to review these recommendations and pick your first activity.
        </div>

        <div className="footer-actions results-actions">
          <button type="button" className="primary-btn" onClick={retakeSurvey}>
            Retake Survey
          </button>
          <Link href="/" className="button-link secondary-btn">
            Back to Welcome
          </Link>
        </div>
      </section>
    </main>
  );
}
