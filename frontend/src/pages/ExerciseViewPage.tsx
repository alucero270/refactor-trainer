import { FormEvent, useState } from "react";

import { createExercise } from "../api/client";
import { MonacoEditorPanel } from "../components/MonacoEditorPanel";
import { SectionCard } from "../components/SectionCard";
import type { Exercise } from "../types/api";

export function ExerciseViewPage() {
  const [candidateId, setCandidateId] = useState("");
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [editorCode, setEditorCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedCandidateId = candidateId.trim();

    if (!normalizedCandidateId) {
      setError("Enter a candidate id before creating an exercise.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const generated = await createExercise(normalizedCandidateId);
      setExercise(generated);
      setEditorCode("");
    } catch (error) {
      setExercise(null);
      setError(error instanceof Error ? error.message : "Exercise could not be generated.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="content-grid">
      <SectionCard title="Exercise View" eyebrow="Generated exercise">
        <form className="stack" onSubmit={handleSubmit}>
          <label>
            Candidate id
            <input value={candidateId} onChange={(event) => setCandidateId(event.target.value)} />
          </label>
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? "Generating..." : "Generate exercise"}
          </button>
        </form>
      </SectionCard>
      {exercise ? (
        <div className="two-column">
          <SectionCard
            title={exercise.title}
            eyebrow="Active exercise"
            aside={<span className="pill">{exercise.difficulty}</span>}
          >
            <div className="stack">
              <p>{exercise.description}</p>
              <p className="muted">
                Exercise <code>{exercise.exercise_id}</code> for candidate <code>{exercise.candidate_id}</code>
              </p>
            </div>
          </SectionCard>
          <MonacoEditorPanel
            aside={exercise.status}
            title="Attempt Editor"
            value={editorCode}
            onChange={setEditorCode}
          />
        </div>
      ) : null}
      {error ? (
        <SectionCard title="Exercise Error" eyebrow="Validation">
          <p className="error-text">{error}</p>
        </SectionCard>
      ) : null}
    </div>
  );
}
