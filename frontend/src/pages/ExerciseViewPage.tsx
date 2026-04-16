import { MonacoEditorPanel } from "../components/MonacoEditorPanel";
import { SectionCard } from "../components/SectionCard";

const exerciseDraft = `# Exercise placeholder

- Preserve behavior
- Extract a focused helper
- Keep the change single-file and minimal
`;

export function ExerciseViewPage() {
  return (
    <div className="two-column">
      <SectionCard title="Exercise View" eyebrow="Generated exercise">
        <div className="stack">
          <div className="placeholder-box">
            <p>Exercise generation is wired as a backend seam and returns scaffold content only.</p>
            <p className="muted">The final generation policy should align with repo-local guidance and prompt templates.</p>
          </div>
        </div>
      </SectionCard>
      <MonacoEditorPanel value={exerciseDraft} />
    </div>
  );
}

