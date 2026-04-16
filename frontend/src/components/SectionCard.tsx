import type { PropsWithChildren, ReactNode } from "react";

type SectionCardProps = PropsWithChildren<{
  title: string;
  eyebrow?: string;
  aside?: ReactNode;
}>;

export function SectionCard({ title, eyebrow, aside, children }: SectionCardProps) {
  return (
    <section className="card">
      <div className="card-header">
        <div>
          {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
          <h2>{title}</h2>
        </div>
        {aside}
      </div>
      {children}
    </section>
  );
}

