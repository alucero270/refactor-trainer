import { useEffect, useState } from "react";

import { listProviders } from "../api/client";
import type { ProviderSummary } from "../types/api";

export function useProviders() {
  const [providers, setProviders] = useState<ProviderSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const data = await listProviders();
      if (!cancelled) {
        setProviders(data);
        setLoading(false);
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return { providers, loading };
}

