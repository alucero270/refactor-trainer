import { useEffect, useState } from "react";

import { listProviders } from "../api/client";
import type { ProviderSummary } from "../types/api";

export function useProviders() {
  const [providers, setProviders] = useState<ProviderSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await listProviders();
        if (!cancelled) {
          setProviders(data);
          setError(null);
        }
      } catch (error) {
        if (!cancelled) {
          setProviders([]);
          setError(error instanceof Error ? error.message : "Failed to load providers.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return { providers, loading, error };
}
