import { ProviderSetupCard } from "../components/ProviderSetupCard";
import { SectionCard } from "../components/SectionCard";

export function ProviderSetupPage() {
  return (
    <div className="content-grid">
      <ProviderSetupCard />
      <SectionCard title="Provider Config API" eyebrow="Backend seam">
        <div className="placeholder-box">
          <p>Use the backend scaffold endpoints to list providers, inspect placeholder health, and store lightweight local config.</p>
          <p className="muted">
            Target routes: <code>/providers</code>, <code>/provider/config</code>, <code>/provider/health</code>
          </p>
        </div>
      </SectionCard>
    </div>
  );
}

