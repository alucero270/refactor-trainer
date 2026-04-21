import type {
  Candidate,
  AttemptFeedbackResponse,
  Exercise,
  GitHubConnectResponse,
  GitHubImportResponse,
  GitHubRepo,
  GitHubTreeItem,
  ProviderConfig,
  ProviderHealthItem,
  ProviderSummary,
  SubmitCodeRequest,
  SubmitCodeResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail ?? detail;
    } catch {
      // Keep the HTTP status text when the backend does not return JSON.
    }
    throw new Error(`Request failed for ${path}: ${response.status} ${detail}`);
  }

  return (await response.json()) as T;
}

export async function listProviders(): Promise<ProviderSummary[]> {
  const payload = await requestJson<{ providers: ProviderSummary[] }>("/providers");
  return payload.providers;
}

export async function getProviderConfig(): Promise<ProviderConfig> {
  const payload = await requestJson<{ config: ProviderConfig }>("/provider/config");
  return payload.config;
}

export async function saveProviderConfig(config: ProviderConfig): Promise<ProviderConfig> {
  const payload = await requestJson<{ config: ProviderConfig }>("/provider/config", {
    method: "PUT",
    body: JSON.stringify({ config }),
  });
  return payload.config;
}

export async function getProviderHealth(): Promise<ProviderHealthItem[]> {
  const payload = await requestJson<{ providers: ProviderHealthItem[] }>("/provider/health");
  return payload.providers;
}

export async function submitCode(payload: SubmitCodeRequest): Promise<SubmitCodeResponse> {
  return requestJson<SubmitCodeResponse>("/submit-code", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getGitHubConnection(token: string): Promise<GitHubConnectResponse> {
  const headers = token.trim() ? { Authorization: `Bearer ${token.trim()}` } : undefined;
  return requestJson<GitHubConnectResponse>("/github/connect", { headers });
}

export async function listGitHubRepos(): Promise<GitHubRepo[]> {
  const payload = await requestJson<{ repos: GitHubRepo[] }>("/github/repos");
  return payload.repos;
}

export async function getGitHubRepoTree(repoId: string): Promise<GitHubTreeItem[]> {
  const payload = await requestJson<{ tree: GitHubTreeItem[] }>(`/github/repo/${encodeURIComponent(repoId)}/tree`);
  return payload.tree;
}

export async function importGitHubFile(repoId: string, path: string, ref = "HEAD"): Promise<GitHubImportResponse> {
  return requestJson<GitHubImportResponse>("/github/import-file", {
    method: "POST",
    body: JSON.stringify({ repo_id: repoId, path, ref }),
  });
}

export async function listCandidates(submissionId: string): Promise<Candidate[]> {
  const query = new URLSearchParams({ submission_id: submissionId });
  const payload = await requestJson<{ candidates: Candidate[] }>(`/candidates?${query.toString()}`);
  return payload.candidates;
}

export async function createExercise(candidateId: string): Promise<Exercise> {
  return requestJson<Exercise>(`/exercise/${encodeURIComponent(candidateId)}`, {
    method: "POST",
  });
}

export async function submitAttempt(exerciseId: string, attemptCode: string): Promise<AttemptFeedbackResponse> {
  return requestJson<AttemptFeedbackResponse>(`/submit-attempt/${encodeURIComponent(exerciseId)}`, {
    method: "POST",
    body: JSON.stringify({ attempt_code: attemptCode }),
  });
}
