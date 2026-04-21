import { ChangeEvent, FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { submitCode } from "../api/client";
import { SectionCard } from "../components/SectionCard";
import { useWorkflowState } from "../providers/WorkflowStateProvider";
import type { SubmitCodeResponse } from "../types/api";

const sampleCode = `def summarize(items):
    total = 0
    for item in items:
        if item > 0:
            total += item
    return total
`;

export function UploadPastePage() {
  const navigate = useNavigate();
  const workflow = useWorkflowState();
  const [pasteCode, setPasteCode] = useState(sampleCode);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [result, setResult] = useState<SubmitCodeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<"upload" | "paste" | null>(null);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setResult(null);
    setError(null);
    setUploadFile(event.target.files?.item(0) ?? null);
  }

  async function handleUploadSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!uploadFile) {
      setError("Choose one Python file before submitting.");
      return;
    }

    if (!uploadFile.name.toLowerCase().endsWith(".py")) {
      setError("Only one Python file can be uploaded.");
      return;
    }

    await submitSource("upload", uploadFile.name, await uploadFile.text());
  }

  async function handlePasteSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await submitSource("paste", "snippet.py", pasteCode);
  }

  async function submitSource(source: "upload" | "paste", filename: string, code: string) {
    setSubmitting(source);
    setResult(null);
    setError(null);

    try {
      const submission = await submitCode({ source, filename, code });
      workflow.setSubmission(submission);
      setResult(submission);
      navigate("/candidates");
    } catch (error) {
      setError(error instanceof Error ? error.message : "Code could not be submitted.");
    } finally {
      setSubmitting(null);
    }
  }

  return (
    <div className="two-column">
      <SectionCard title="Upload / Paste" eyebrow="Ingestion">
        <form className="stack" onSubmit={handleUploadSubmit}>
          <label>
            Python file
            <input accept=".py,text/x-python,text/plain" type="file" onChange={handleFileChange} />
          </label>
          <button className="secondary-button" disabled={submitting !== null} type="submit">
            {submitting === "upload" ? "Submitting..." : "Submit uploaded file"}
          </button>
        </form>
      </SectionCard>
      <SectionCard title="Paste Python" eyebrow="Single file">
        <form className="stack" onSubmit={handlePasteSubmit}>
          <label>
            Code
            <textarea
              className="code-input"
              value={pasteCode}
              onChange={(event) => setPasteCode(event.target.value)}
              spellCheck={false}
            />
          </label>
          <button className="primary-button" disabled={submitting !== null} type="submit">
            {submitting === "paste" ? "Submitting..." : "Submit pasted code"}
          </button>
        </form>
      </SectionCard>
      {result ? (
        <SectionCard title="Submission Accepted" eyebrow="Backend response">
          <div className="stack">
            <p>
              Submission <code>{result.submission_id}</code> accepted with {result.candidate_count} detected candidates.
            </p>
            <p className="muted">Both upload and paste use the same submit-code flow.</p>
          </div>
        </SectionCard>
      ) : null}
      {error ? (
        <SectionCard title="Submission Error" eyebrow="Validation">
          <p className="error-text">{error}</p>
        </SectionCard>
      ) : null}
    </div>
  );
}
