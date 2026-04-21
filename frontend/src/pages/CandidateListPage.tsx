import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { listCandidates } from "../api/client";
import { SectionCard } from "../components/SectionCard";
import { useWorkflowState } from "../providers/WorkflowStateProvider";
import type { Candidate } from "../types/api";

export function CandidateListPage() {
  const navigate = useNavigate();
  const workflow = useWorkflowState();
  const [submissionId, setSubmissionId] = useState(workflow.submission?.submission_id ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (workflow.submission?.submission_id) {
      setSubmissionId(workflow.submission.submission_id);
      if (workflow.candidates.length === 0) {
        void loadCandidates(workflow.submission.submission_id);
      }
    }
  }, [workflow.submission?.submission_id]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedId = submissionId.trim();

    if (!normalizedId) {
      setError("Enter a submission id before loading candidates.");
      return;
    }

    await loadCandidates(normalizedId);
  }

  async function loadCandidates(activeSubmissionId: string) {
    setLoading(true);
    setError(null);

    try {
      workflow.setCandidates(await listCandidates(activeSubmissionId));
    } catch (error) {
      workflow.setCandidates([]);
      setError(error instanceof Error ? error.message : "Candidates could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  function handleCandidateSelect(candidate: Candidate) {
    workflow.selectCandidate(candidate);
  }

  return (
    <div className="content-grid">
      <SectionCard title="Candidate List" eyebrow="Deterministic detection">
        <form className="stack" onSubmit={handleSubmit}>
          <label>
            Submission id
            <input value={submissionId} onChange={(event) => setSubmissionId(event.target.value)} />
          </label>
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? "Loading..." : "Load candidates"}
          </button>
        </form>
      </SectionCard>
      {workflow.candidates.length > 0 ? (
        <SectionCard title="Ranked Candidates" eyebrow={`${workflow.candidates.length} returned`}>
          <div className="candidate-list" role="list">
            {workflow.candidates.map((candidate, index) => (
              <button
                className={candidate.id === workflow.selectedCandidate?.id ? "candidate-row selected" : "candidate-row"}
                key={candidate.id}
                onClick={() => handleCandidateSelect(candidate)}
                role="listitem"
                type="button"
              >
                <span className="rank">{index + 1}</span>
                <span className="candidate-copy">
                  <strong>{candidate.title}</strong>
                  <span>{candidate.summary}</span>
                  <small>
                    {candidate.smell} - {candidate.severity}
                  </small>
                </span>
              </button>
            ))}
          </div>
        </SectionCard>
      ) : null}
      {workflow.selectedCandidate ? (
        <SectionCard title="Selected Candidate" eyebrow="Ready for exercise generation">
          <div className="stack">
            <strong>{workflow.selectedCandidate.title}</strong>
            <p>{workflow.selectedCandidate.summary}</p>
            <p className="muted">
              Candidate id <code>{workflow.selectedCandidate.id}</code>
            </p>
            <button className="primary-button" type="button" onClick={() => navigate("/exercise")}>
              Continue to exercise
            </button>
          </div>
        </SectionCard>
      ) : null}
      {error ? (
        <SectionCard title="Candidate Error" eyebrow="Validation">
          <p className="error-text">{error}</p>
        </SectionCard>
      ) : null}
    </div>
  );
}
