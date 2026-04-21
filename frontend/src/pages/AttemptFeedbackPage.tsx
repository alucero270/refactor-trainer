import { Link } from "react-router-dom";

import { SectionCard } from "../components/SectionCard";
import { useWorkflowState } from "../providers/WorkflowStateProvider";

export function AttemptFeedbackPage() {
  const workflow = useWorkflowState();

  if (!workflow.exercise || !workflow.feedback) {
    return (
      <SectionCard title="Attempt Feedback" eyebrow="Evaluation">
        <div className="stack">
          <p className="muted">No active evaluated attempt is available.</p>
          <Link className="secondary-button" to="/exercise">
            Open exercise
          </Link>
        </div>
      </SectionCard>
    );
  }

  return (
    <SectionCard
      title={workflow.feedback.accepted ? "Attempt Passed" : "Attempt Needs More Work"}
      eyebrow="Deterministic evaluation"
      aside={<span className={workflow.feedback.accepted ? "pill ready" : "pill unavailable"}>{workflow.feedback.accepted ? "Pass" : "Fail"}</span>}
    >
      <div className="stack">
        <div className={workflow.feedback.accepted ? "feedback-box accepted" : "feedback-box rejected"}>
          <strong>{workflow.exercise.title}</strong>
          <p>{workflow.feedback.feedback}</p>
          <p className="muted">
            Exercise <code>{workflow.exercise.exercise_id}</code> for candidate <code>{workflow.exercise.candidate_id}</code>
          </p>
        </div>
        <Link className="secondary-button" to="/exercise">
          Return to exercise
        </Link>
      </div>
    </SectionCard>
  );
}
