import { FormEvent, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { createExercise, getHints, submitAttempt } from "../api/client";
import { MonacoEditorPanel } from "../components/MonacoEditorPanel";
import { SectionCard } from "../components/SectionCard";
import { useWorkflowState } from "../providers/WorkflowStateProvider";

const MAX_HINTS = 2;

export function ExerciseViewPage() {
  const navigate = useNavigate();
  const params = useParams<{ candidateId?: string }>();
  const workflow = useWorkflowState();
  const [candidateId, setCandidateId] = useState(
    workflow.selectedCandidate?.id ?? params.candidateId ?? "",
  );
  const [loading, setLoading] = useState(false);
  const [submittingAttempt, setSubmittingAttempt] = useState(false);
  const [revealingHint, setRevealingHint] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const revealedHintCount = workflow.hints?.hints.length ?? 0;
  const hintsExhausted = revealedHintCount >= MAX_HINTS;

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

  async function handleRevealHint() {
    if (!workflow.exercise) {
      setError("Create an exercise before revealing hints.");
      return;
    }
    if (hintsExhausted) {
      return;
    }

    setRevealingHint(true);
    setError(null);

    try {
      workflow.setHints(await getHints(workflow.exercise.exercise_id));
    } catch (error) {
      setError(error instanceof Error ? error.message : "Hint could not be revealed.");
    } finally {
      setRevealingHint(false);
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
      navigate(`/feedback/${encodeURIComponent(workflow.exercise.exercise_id)}`);
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
        <SectionCard
          title="Progressive Hints"
          eyebrow={`Revealed ${revealedHintCount} of ${MAX_HINTS}`}
        >
          <div className="stack">
            <button
              className="secondary-button"
              disabled={revealingHint || hintsExhausted}
              type="button"
              onClick={() => void handleRevealHint()}
            >
              {hintsExhausted
                ? "All hints revealed"
                : revealingHint
                  ? "Revealing..."
                  : revealedHintCount === 0
                    ? "Reveal first hint"
                    : "Reveal next hint"}
            </button>
            {workflow.hints && workflow.hints.hints.length > 0 ? (
              <ol className="hint-list">
                {workflow.hints.hints.map((hint, index) => (
                  <li key={index}>{hint}</li>
                ))}
              </ol>
            ) : (
              <p className="muted">Hints are progressive and reveal one at a time. Try solving first.</p>
            )}
            {workflow.hints?.guidance_summary ? (
              <p className="muted">Guidance: {workflow.hints.guidance_summary}</p>
            ) : null}
          </div>
        </SectionCard>
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
