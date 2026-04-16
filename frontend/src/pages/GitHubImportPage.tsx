import { SectionCard } from "../components/SectionCard";

export function GitHubImportPage() {
  return (
    <SectionCard title="GitHub Import" eyebrow="Placeholder flow">
      <div className="stack">
        <div className="placeholder-box">
          <p>GitHub connect, repo list, tree navigation, and file import routes are scaffolded only.</p>
          <p className="muted">OAuth, live repository browsing, and import execution are intentionally deferred.</p>
        </div>
        <p className="muted">
          Target routes: <code>/github/connect</code>, <code>/github/repos</code>, <code>/github/repo/{`{repo_id}`}/tree</code>, <code>/github/import-file</code>
        </p>
      </div>
    </SectionCard>
  );
}

