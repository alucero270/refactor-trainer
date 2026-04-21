import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  getGitHubConnection,
  getGitHubRepoTree,
  importGitHubFile,
  listGitHubRepos,
  submitCode,
} from "../api/client";
import { SectionCard } from "../components/SectionCard";
import type { GitHubConnectResponse, GitHubRepo, GitHubTreeItem, SubmitCodeResponse } from "../types/api";

export function GitHubImportPage() {
  const [token, setToken] = useState("");
  const [connection, setConnection] = useState<GitHubConnectResponse | null>(null);
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [tree, setTree] = useState<GitHubTreeItem[]>([]);
  const [repoId, setRepoId] = useState("");
  const [selectedPath, setSelectedPath] = useState("");
  const [ref, setRef] = useState("HEAD");
  const [submission, setSubmission] = useState<SubmitCodeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pythonFiles = useMemo(
    () => tree.filter((item) => item.type === "blob" && item.path.toLowerCase().endsWith(".py")),
    [tree],
  );

  useEffect(() => {
    let cancelled = false;

    async function loadRepos() {
      try {
        const repoList = await listGitHubRepos();
        if (!cancelled) {
          setRepos(repoList);
          if (repoList.length > 0) {
            setRepoId(repoList[0].id);
          }
        }
      } catch (error) {
        if (!cancelled) {
          setError(error instanceof Error ? error.message : "GitHub repositories could not be loaded.");
        }
      }
    }

    void loadRepos();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadTree() {
      if (!repoId) {
        setTree([]);
        return;
      }

      try {
        const repoTree = await getGitHubRepoTree(repoId);
        if (!cancelled) {
          setTree(repoTree);
          setSelectedPath("");
        }
      } catch (error) {
        if (!cancelled) {
          setError(error instanceof Error ? error.message : "Repository tree could not be loaded.");
        }
      }
    }

    void loadTree();

    return () => {
      cancelled = true;
    };
  }, [repoId]);

  async function handleConnect(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      setConnection(await getGitHubConnection(token));
    } catch (error) {
      setError(error instanceof Error ? error.message : "GitHub connection could not be checked.");
    } finally {
      setLoading(false);
    }
  }

  async function handleImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!repoId || !selectedPath) {
      setError("Choose one Python file before importing.");
      return;
    }

    setLoading(true);
    setSubmission(null);
    setError(null);

    try {
      const imported = await importGitHubFile(repoId, selectedPath, ref);
      const filename = imported.path.split("/").pop() ?? "github-import.py";
      setSubmission(await submitCode({ source: "github", filename, code: imported.content }));
    } catch (error) {
      setError(error instanceof Error ? error.message : "GitHub file could not be imported.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="content-grid">
      <SectionCard title="GitHub Import" eyebrow="Connection">
        <form className="stack" onSubmit={handleConnect}>
          <label>
            Bearer token
            <input
              autoComplete="off"
              type="password"
              value={token}
              onChange={(event) => setToken(event.target.value)}
            />
          </label>
          <button className="secondary-button" disabled={loading} type="submit">
            {loading ? "Checking..." : "Check connection"}
          </button>
          {connection ? (
            <div className="status-strip">
              <div>
                <strong>{connection.status === "connected" ? "Connected" : "Not connected"}</strong>
                <p className="muted">{connection.message}</p>
              </div>
              {connection.account ? <span className="pill ready">{connection.account.login}</span> : null}
            </div>
          ) : null}
        </form>
      </SectionCard>
      <SectionCard title="Select One File" eyebrow="Targeted import">
        <form className="stack" onSubmit={handleImport}>
          <div className="form-grid">
            <label>
              Repository
              <select value={repoId} onChange={(event) => setRepoId(event.target.value)}>
                {repos.map((repo) => (
                  <option key={repo.id} value={repo.id}>
                    {repo.owner}/{repo.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Ref
              <input value={ref} onChange={(event) => setRef(event.target.value)} />
            </label>
          </div>
          <div className="file-list" role="list">
            {pythonFiles.map((item) => (
              <button
                className={item.path === selectedPath ? "file-row selected" : "file-row"}
                key={item.path}
                onClick={() => setSelectedPath(item.path)}
                role="listitem"
                type="button"
              >
                {item.path}
              </button>
            ))}
          </div>
          <button className="primary-button" disabled={loading || !selectedPath} type="submit">
            {loading ? "Importing..." : "Import selected file"}
          </button>
        </form>
      </SectionCard>
      {submission ? (
        <SectionCard title="Imported Submission" eyebrow="Backend response">
          <p>
            Submission <code>{submission.submission_id}</code> accepted with {submission.candidate_count} detected candidates.
          </p>
        </SectionCard>
      ) : null}
      {error ? (
        <SectionCard title="GitHub Import Error" eyebrow="Validation">
          <p className="error-text">{error}</p>
        </SectionCard>
      ) : null}
    </div>
  );
}
