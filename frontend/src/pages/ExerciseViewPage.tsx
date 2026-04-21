import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { createExercise, submitAttempt } from "../api/client";
import { MonacoEditorPanel } from "../components/MonacoEditorPanel";
import { SectionCard } from "../components/SectionCard";
import { useWorkflowState } from "../providers/WorkflowStateProvider";

export function ExerciseViewPage() {
  const navigate = useNavigate();
  const workflow = useWorkflowState();
  const [candidateId, setCandidateId] = useState(workflow.selectedCandidate?.id ?? "");
  const [loading, setLoading] = useState(false);
  const [submittingAttempt, setSubmittingAttempt] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedCandidateId = (workflow.selectedCandidate?.id ?? candidateId).trim();

    if (!normalizedCandidateId) {
      setError("Enter a candidate id before creating an exercise.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const generated = await createExercise(normalizedCandidateId);
      workflow.setExercise(generated);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Exercise could not be generated.");
    } finally {
      setLoading(false);
    }
  }

  async function handleAttemptSubmit() {
    if (!workflow.exercise) {
      setError("Create an exercise before submitting an attempt.");
      return;
    }

    setSubmittingAttempt(true);
    setError(null);

    try {
      workflow.setFeedback(await submitAttempt(workflow.exercise.exercise_id, workflow.editorCode));
      navigate("/feedback");
    } catch (error) {
      setError(error instanceof Error ? error.message : "Attempt could not be submitted.");
    } finally {
      setSubmittingAttempt(false);
    }
  }

  return (
    <div className="content-grid">
      <SectionCard title="Exercise View" eyebrow="Generated exercise">
        <form className="stack" onSubmit={handleSubmit}>
          <label>
            Candidate id
            <input
              value={workflow.selectedCandidate?.id ?? candidateId}
              onChange={(event) => setCandidateId(event.target.value)}
              readOnly={Boolean(workflow.selectedCandidate)}
            />
          </label>
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? "Generating..." : "Generate exercise"}
          </button>
        </form>
      </SectionCard>
      {workflow.exercise ? (
        <div className="two-column">
          <SectionCard
            title={workflow.exercise.title}
            eyebrow="Active exercise"
            aside={<span className="pill">{workflow.exercise.difficulty}</span>}
          >
            <div className="stack">
              <p>{workflow.exercise.description}</p>
              <p className="muted">
                Exercise <code>{workflow.exercise.exercise_id}</code> for candidate <code>{workflow.exercise.candidate_id}</code>
              </p>
            </div>
          </SectionCard>
          <MonacoEditorPanel
            aside={workflow.exercise.status}
            title="Attempt Editor"
            value={workflow.editorCode}
            onChange={workflow.setEditorCode}
          />
        </div>
      ) : null}
      {workflow.exercise ? (
        <SectionCard title="Attempt Submission" eyebrow="Deterministic feedback">
          <div className="stack">
            <button className="primary-button" disabled={submittingAttempt} type="button" onClick={() => void handleAttemptSubmit()}>
              {submittingAttempt ? "Submitting..." : "Submit attempt"}
            </button>
            {workflow.feedback ? (
              <div className={workflow.feedback.accepted ? "feedback-box accepted" : "feedback-box rejected"}>
                <strong>{workflow.feedback.accepted ? "Pass" : "Fail"}</strong>
                <p>{workflow.feedback.feedback}</p>
                <p className="muted">
                  Feedback for exercise <code>{workflow.feedback.exercise_id}</code>
                </p>
              </div>
            ) : null}
          </div>
        </SectionCard>
      ) : null}
      {error ? (
        <SectionCard title="Exercise Error" eyebrow="Validation">
          <p className="error-text">{error}</p>
        </SectionCard>
      ) : null}
    </div>
  );
}
