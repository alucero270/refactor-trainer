import { SectionCard } from "../components/SectionCard";

const candidates = [
  {
    id: "cand-demo",
    title: "Extract focused helper",
    smell: "long_function",
    summary: "Deterministic placeholder candidate for the scaffold.",
  },
];

export function CandidateListPage() {
  return (
    <SectionCard title="Candidate List" eyebrow="Deterministic detection">
      <div className="stack">
        {candidates.map((candidate) => (
          <div key={candidate.id} className="placeholder-box">
            <strong>{candidate.title}</strong>
            <p>{candidate.summary}</p>
            <p className="muted">
              {candidate.id} · {candidate.smell}
            </p>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

