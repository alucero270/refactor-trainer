import { FormEvent, useState } from "react";

import { listCandidates } from "../api/client";
import { SectionCard } from "../components/SectionCard";
import type { Candidate } from "../types/api";

export function CandidateListPage() {
  const [submissionId, setSubmissionId] = useState("");
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedId = submissionId.trim();

    if (!normalizedId) {
      setError("Enter a submission id before loading candidates.");
      return;
    }

    setLoading(true);
    setError(null);
    setSelectedCandidateId("");

    try {
      setCandidates(await listCandidates(normalizedId));
    } catch (error) {
      setCandidates([]);
      setError(error instanceof Error ? error.message : "Candidates could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  const selectedCandidate = candidates.find((candidate) => candidate.id === selectedCandidateId);

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
      {candidates.length > 0 ? (
        <SectionCard title="Ranked Candidates" eyebrow={`${candidates.length} returned`}>
          <div className="candidate-list" role="list">
            {candidates.map((candidate, index) => (
              <button
                className={candidate.id === selectedCandidateId ? "candidate-row selected" : "candidate-row"}
                key={candidate.id}
                onClick={() => setSelectedCandidateId(candidate.id)}
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
      {selectedCandidate ? (
        <SectionCard title="Selected Candidate" eyebrow="Ready for exercise generation">
          <div className="stack">
            <strong>{selectedCandidate.title}</strong>
            <p>{selectedCandidate.summary}</p>
            <p className="muted">
              Candidate id <code>{selectedCandidate.id}</code>
            </p>
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
