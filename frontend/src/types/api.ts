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
  instructions: string;
  guidance_summary: string;
  status: string;
};

export type HintBundle = {
  exercise_id: string;
  hints: string[];
  guidance_summary: string;
  status: string;
};
