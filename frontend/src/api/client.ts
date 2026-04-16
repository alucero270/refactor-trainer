import type { ProviderSummary } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function listProviders(): Promise<ProviderSummary[]> {
  try {
    const payload = await getJson<{ providers: ProviderSummary[] }>("/providers");
    return payload.providers;
  } catch {
    return [
      { name: "ollama", kind: "local", supports_local: true },
      { name: "openai", kind: "remote", supports_local: false },
      { name: "anthropic", kind: "remote", supports_local: false },
      { name: "mcp", kind: "mcp", supports_local: false },
    ];
  }
}

