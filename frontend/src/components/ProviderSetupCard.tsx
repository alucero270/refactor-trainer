import { FormEvent, useEffect, useMemo, useState } from "react";

import { getProviderConfig, getProviderHealth, saveProviderConfig } from "../api/client";
import { SectionCard } from "./SectionCard";
import type { ProviderConfig, ProviderHealthItem, ProviderName, ProviderSummary } from "../types/api";
import { useProviders } from "../hooks/useProviders";

const providerLabels: Record<ProviderName, string> = {
  ollama: "Ollama",
  openai: "OpenAI",
  anthropic: "Anthropic",
  mcp: "MCP",
};

const providerNotes: Record<ProviderName, string> = {
  ollama: "Local-first reference provider.",
  openai: "Optional BYOK remote provider.",
  anthropic: "Optional BYOK remote provider.",
  mcp: "Provider-compatible MCP path.",
};

const emptyConfig: ProviderConfig = {
  default_provider: "ollama",
  configured_providers: ["ollama"],
  providers: {
    ollama: {
      base_url: "http://localhost:11434",
      model: "",
    },
    openai: {
      api_key: "",
      model: "",
      base_url: "",
    },
    anthropic: {
      api_key: "",
      model: "",
      base_url: "",
    },
    mcp: {
      server_url: "",
      model: "",
    },
  },
};

function normalizeConfig(config: ProviderConfig): ProviderConfig {
  return {
    ...config,
    providers: {
      ollama: {
        ...config.providers.ollama,
        model: config.providers.ollama.model ?? "",
      },
      openai: {
        ...config.providers.openai,
        api_key: "",
        model: config.providers.openai.model ?? "",
        base_url: config.providers.openai.base_url ?? "",
      },
      anthropic: {
        ...config.providers.anthropic,
        api_key: "",
        model: config.providers.anthropic.model ?? "",
        base_url: config.providers.anthropic.base_url ?? "",
      },
      mcp: {
        ...config.providers.mcp,
        server_url: config.providers.mcp.server_url ?? "",
        model: config.providers.mcp.model ?? "",
      },
    },
  };
}

export function ProviderSetupCard() {
  const { providers, loading, error } = useProviders();
  const [config, setConfig] = useState<ProviderConfig>(emptyConfig);
  const [health, setHealth] = useState<ProviderHealthItem[]>([]);
  const [configError, setConfigError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  const selectedProvider = config.default_provider;
  const selectedHealth = health.find((item) => item.provider === selectedProvider);
  const orderedProviders = useMemo(
    () => providers.length > 0 ? providers : fallbackProviders(),
    [providers],
  );

  useEffect(() => {
    let cancelled = false;

    async function loadConfig() {
      try {
        const [storedConfig, providerHealth] = await Promise.all([
          getProviderConfig(),
          getProviderHealth(),
        ]);
        if (!cancelled) {
          setConfig(normalizeConfig(storedConfig));
          setHealth(providerHealth);
          setConfigError(null);
        }
      } catch (error) {
        if (!cancelled) {
          setConfigError(error instanceof Error ? error.message : "Provider setup could not be loaded.");
        }
      }
    }

    void loadConfig();

    return () => {
      cancelled = true;
    };
  }, []);

  async function refreshHealth() {
    try {
      setHealth(await getProviderHealth());
      setConfigError(null);
    } catch (error) {
      setConfigError(error instanceof Error ? error.message : "Provider health could not be loaded.");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setSavedMessage(null);
    setConfigError(null);

    try {
      const savedConfig = await saveProviderConfig(toPayload(config));
      setConfig(normalizeConfig(savedConfig));
      setSavedMessage(`${providerLabels[savedConfig.default_provider]} configuration saved.`);
      setHealth(await getProviderHealth());
    } catch (error) {
      setConfigError(error instanceof Error ? error.message : "Provider configuration could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <SectionCard
      title="Provider Setup"
      eyebrow="Configuration"
      aside={<span className="muted">{loading ? "Loading..." : `${orderedProviders.length} providers`}</span>}
    >
      <form className="stack" onSubmit={handleSubmit}>
        {error ? (
          <div className="placeholder-box">
            <p>Provider metadata could not be loaded from the backend.</p>
            <p className="muted">{error}</p>
          </div>
        ) : null}
        <div className="provider-grid" role="list">
          {orderedProviders.map((provider) => (
            <button
              className={provider.name === selectedProvider ? "provider-option selected" : "provider-option"}
              key={provider.name}
              onClick={() => setConfig(selectProvider(config, provider.name))}
              role="listitem"
              type="button"
            >
              <span>
                <strong>{providerLabels[provider.name]}</strong>
                <small>{providerNotes[provider.name]}</small>
              </span>
              <span className="provider-kind">{provider.kind}</span>
            </button>
          ))}
        </div>
        <ProviderFields config={config} setConfig={setConfig} />
        <div className="status-strip">
          <div>
            <strong>{selectedHealth?.status === "ready" ? "Ready" : "Not ready"}</strong>
            <p className="muted">{selectedHealth?.message ?? "Health has not been checked yet."}</p>
          </div>
          <button className="secondary-button" type="button" onClick={() => void refreshHealth()}>
            Refresh health
          </button>
        </div>
        {health.length > 0 ? (
          <div className="pill-row">
            {health.map((item) => (
              <span key={item.provider} className={item.available ? "pill ready" : "pill unavailable"}>
                {providerLabels[item.provider]}: {item.status}
              </span>
            ))}
          </div>
        ) : null}
        {configError ? <p className="error-text">{configError}</p> : null}
        {savedMessage ? <p className="success-text">{savedMessage}</p> : null}
        <div className="form-actions">
          <button className="primary-button" disabled={saving} type="submit">
            {saving ? "Saving..." : "Save provider setup"}
          </button>
        </div>
      </form>
    </SectionCard>
  );
}

type ProviderFieldsProps = {
  config: ProviderConfig;
  setConfig: (config: ProviderConfig) => void;
};

function ProviderFields({ config, setConfig }: ProviderFieldsProps) {
  const provider = config.default_provider;

  if (provider === "ollama") {
    return (
      <div className="form-grid">
        <label>
          Base URL
          <input
            required
            value={config.providers.ollama.base_url}
            onChange={(event) =>
              setConfig({
                ...config,
                providers: {
                  ...config.providers,
                  ollama: { ...config.providers.ollama, base_url: event.target.value },
                },
              })
            }
          />
        </label>
        <label>
          Model
          <input
            placeholder="Optional"
            value={config.providers.ollama.model ?? ""}
            onChange={(event) =>
              setConfig({
                ...config,
                providers: {
                  ...config.providers,
                  ollama: { ...config.providers.ollama, model: event.target.value },
                },
              })
            }
          />
        </label>
      </div>
    );
  }

  if (provider === "mcp") {
    return (
      <div className="form-grid">
        <label>
          Server URL
          <input
            required
            placeholder="https://example.com/mcp"
            value={config.providers.mcp.server_url ?? ""}
            onChange={(event) =>
              setConfig({
                ...config,
                providers: {
                  ...config.providers,
                  mcp: { ...config.providers.mcp, server_url: event.target.value },
                },
              })
            }
          />
        </label>
        <label>
          Model
          <input
            placeholder="Optional"
            value={config.providers.mcp.model ?? ""}
            onChange={(event) =>
              setConfig({
                ...config,
                providers: {
                  ...config.providers,
                  mcp: { ...config.providers.mcp, model: event.target.value },
                },
              })
            }
          />
        </label>
      </div>
    );
  }

  return (
    <div className="form-grid">
      <label>
        API key
        <input
          required
          autoComplete="off"
          type="password"
          value={config.providers[provider].api_key ?? ""}
          onChange={(event) =>
            setConfig({
              ...config,
              providers: {
                ...config.providers,
                [provider]: { ...config.providers[provider], api_key: event.target.value },
              },
            })
          }
        />
      </label>
      <label>
        Model
        <input
          placeholder="Optional"
          value={config.providers[provider].model ?? ""}
          onChange={(event) =>
            setConfig({
              ...config,
              providers: {
                ...config.providers,
                [provider]: { ...config.providers[provider], model: event.target.value },
              },
            })
          }
        />
      </label>
      <label>
        Base URL
        <input
          placeholder="Optional"
          value={config.providers[provider].base_url ?? ""}
          onChange={(event) =>
            setConfig({
              ...config,
              providers: {
                ...config.providers,
                [provider]: { ...config.providers[provider], base_url: event.target.value },
              },
            })
          }
        />
      </label>
    </div>
  );
}

function selectProvider(config: ProviderConfig, provider: ProviderName): ProviderConfig {
  return {
    ...config,
    default_provider: provider,
    configured_providers: [provider],
  };
}

function toPayload(config: ProviderConfig): ProviderConfig {
  return {
    ...config,
    configured_providers: [config.default_provider],
    providers: {
      ollama: {
        ...config.providers.ollama,
        model: cleanOptional(config.providers.ollama.model),
      },
      openai: {
        ...config.providers.openai,
        api_key: cleanOptional(config.providers.openai.api_key),
        model: cleanOptional(config.providers.openai.model),
        base_url: cleanOptional(config.providers.openai.base_url),
      },
      anthropic: {
        ...config.providers.anthropic,
        api_key: cleanOptional(config.providers.anthropic.api_key),
        model: cleanOptional(config.providers.anthropic.model),
        base_url: cleanOptional(config.providers.anthropic.base_url),
      },
      mcp: {
        ...config.providers.mcp,
        server_url: cleanOptional(config.providers.mcp.server_url),
        model: cleanOptional(config.providers.mcp.model),
      },
    },
  };
}

function cleanOptional(value: string | null): string | null {
  const trimmed = value?.trim() ?? "";
  return trimmed ? trimmed : null;
}

function fallbackProviders(): ProviderSummary[] {
  return [
    { name: "ollama", kind: "local", supports_local: true },
    { name: "openai", kind: "remote", supports_local: false },
    { name: "anthropic", kind: "remote", supports_local: false },
    { name: "mcp", kind: "mcp", supports_local: false },
  ];
}
