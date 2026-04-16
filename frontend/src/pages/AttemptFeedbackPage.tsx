import { SectionCard } from "../components/SectionCard";

export function AttemptFeedbackPage() {
  return (
    <SectionCard title="Attempt Feedback" eyebrow="Evaluation stub">
      <div className="stack">
        <div className="placeholder-box">
          <p>Attempt submission and feedback are intentionally stubbed for this pass.</p>
          <p className="muted">Future work can add diff-aware evaluation, rubric alignment, and hint escalation.</p>
        </div>
        <p className="muted">
          Target routes: <code>/exercise/{`{candidate_id}`}</code>, <code>/hints/{`{exercise_id}`}</code>, <code>/submit-attempt/{`{exercise_id}`}</code>
        </p>
      </div>
    </SectionCard>
  );
}

