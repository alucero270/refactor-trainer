import { SectionCard } from "../components/SectionCard";

export function AttemptFeedbackPage() {
  return (
    <SectionCard title="Attempt Feedback" eyebrow="Evaluation stub">
      <div className="stack">
        <div className="placeholder-box">
          <p>Attempt feedback is displayed with the active exercise after deterministic evaluation.</p>
          <p className="muted">The backend returns pass or fail feedback from the submit-attempt endpoint.</p>
        </div>
        <p className="muted">
          Target routes: <code>/exercise/{`{candidate_id}`}</code>, <code>/hints/{`{exercise_id}`}</code>, <code>/submit-attempt/{`{exercise_id}`}</code>
        </p>
      </div>
    </SectionCard>
  );
}
