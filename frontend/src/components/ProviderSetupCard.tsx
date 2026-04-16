import { useProviders } from "../hooks/useProviders";
import { SectionCard } from "./SectionCard";

export function ProviderSetupCard() {
  const { providers, loading } = useProviders();

  return (
    <SectionCard
      title="Provider Setup"
      eyebrow="Configuration"
      aside={<span className="muted">{loading ? "Loading..." : `${providers.length} providers`}</span>}
    >
      <div className="stack">
        <p className="muted">
          This scaffold keeps provider configuration intentionally shallow while exposing the expected seams for local, remote, and MCP-backed providers.
        </p>
        <div className="pill-row">
          {providers.map((provider) => (
            <span key={provider.name} className="pill">
              {provider.name} · {provider.kind}
            </span>
          ))}
        </div>
      </div>
    </SectionCard>
  );
}

