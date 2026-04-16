export type ProviderSummary = {
  name: string;
  kind: string;
  supports_local: boolean;
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

