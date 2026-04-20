import { useProviders } from "../hooks/useProviders";
import { SectionCard } from "./SectionCard";

export function ProviderSetupCard() {
  const { providers, loading, error } = useProviders();

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
        {error ? (
          <div className="placeholder-box">
            <p>Provider metadata could not be loaded from the backend.</p>
            <p className="muted">{error}</p>
          </div>
        ) : null}
        <div className="pill-row">
          {providers.map((provider) => (
            <span key={provider.name} className="pill">
              {provider.name} - {provider.kind}
            </span>
          ))}
        </div>
      </div>
    </SectionCard>
  );
}
