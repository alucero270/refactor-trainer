import type { PropsWithChildren, ReactNode } from "react";

type LayoutProps = PropsWithChildren<{
  header: ReactNode;
}>;

export function Layout({ header, children }: LayoutProps) {
  return (
    <div className="app-shell">
      <header className="app-header">{header}</header>
      <main className="content-grid">{children}</main>
    </div>
  );
}

