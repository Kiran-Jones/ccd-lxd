import Link from "next/link";

export default function HomePage(): JSX.Element {
  return (
    <main className="main-container">
      <section className="page-card">
        <p className="roadmap-kicker">LXD: Learn. Experience. Design.</p>
        <h1>Welcome to the Dartmouth Center for Career Design</h1>
        <p>
          A Signature Visitor Experience at Dartmouth&apos;s Center for Career Design.
        </p>
        <p>
          This short diagnostic helps identify activities that can best support your next step. You will answer
          18 questions using a four-point agreement scale.
        </p>
        <p>
          Your recommendations are calculated from your responses and sequenced so foundation activities happen
          before advanced exploration.
        </p>
        <div className="hero-actions">
          <Link href="/survey" className="button-link primary-btn">
            Start Survey
          </Link>
        </div>
      </section>
    </main>
  );
}
