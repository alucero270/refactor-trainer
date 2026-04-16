import { MonacoEditorPanel } from "../components/MonacoEditorPanel";
import { SectionCard } from "../components/SectionCard";

const sampleCode = `def summarize(items):
    total = 0
    for item in items:
        if item > 0:
            total += item
    return total
`;

export function UploadPastePage() {
  return (
    <div className="two-column">
      <SectionCard title="Upload / Paste" eyebrow="Ingestion">
        <div className="stack">
          <div className="placeholder-box">
            <p>Single-file Python ingestion is scaffolded for upload, paste, or GitHub import sources.</p>
            <p className="muted">Real file handling and validation flow are intentionally left for the next implementation pass.</p>
          </div>
          <p className="muted">
            Target route: <code>POST /submit-code</code>
          </p>
        </div>
      </SectionCard>
      <MonacoEditorPanel value={sampleCode} />
    </div>
  );
}

