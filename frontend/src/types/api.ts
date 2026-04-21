export type ProviderName = "ollama" | "openai" | "anthropic" | "mcp";

export type ProviderSummary = {
  name: ProviderName;
  kind: string;
  supports_local: boolean;
};

export type ProviderConfig = {
  default_provider: ProviderName;
  configured_providers: ProviderName[];
  providers: {
    ollama: {
      base_url: string;
      model: string | null;
    };
    openai: {
      api_key: string | null;
      model: string | null;
      base_url: string | null;
    };
    anthropic: {
      api_key: string | null;
      model: string | null;
      base_url: string | null;
    };
    mcp: {
      server_url: string | null;
      model: string | null;
    };
  };
};

export type ProviderHealthItem = {
  provider: ProviderName;
  status: "ready" | "unavailable";
  available: boolean;
  message: string;
  failure: {
    code: string;
    detail: string;
  } | null;
};

export type SubmitCodeSource = "upload" | "paste" | "github";

export type SubmitCodeRequest = {
  source: SubmitCodeSource;
  filename?: string | null;
  code: string;
};

export type SubmitCodeResponse = {
  submission_id: string;
  candidate_count: number;
  status: string;
};

export type GitHubConnectResponse = {
  status: "connected" | "not_connected";
  auth_mode: "bearer_token";
  required_permissions: string[];
  capabilities: string[];
  account: {
    login: string;
  } | null;
  message: string;
};

export type GitHubRepo = {
  id: string;
  name: string;
  owner: string;
};

export type GitHubTreeItem = {
  path: string;
  type: string;
};

export type GitHubImportResponse = {
  repo_id: string;
  path: string;
  content: string;
  status: string;
};

export type Candidate = {
  id: string;
  title: string;
  smell: string;
  summary: string;
  severity: string;
};

export type Exercise = {
  exercise_id: string;
  candidate_id: string;
  title: string;
  description: string;
  difficulty: "Easy" | "Medium" | "Hard";
  status: string;
};

export type HintBundle = {
  exercise_id: string;
  hints: string[];
  guidance_summary: string;
  status: string;
};

export type AttemptFeedbackResponse = {
  exercise_id: string;
  accepted: boolean;
  feedback: string;
  status: string;
};
