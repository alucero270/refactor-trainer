import type { PropsWithChildren } from "react";

import { WorkflowStateProvider } from "./WorkflowStateProvider";

export function AppProviders({ children }: PropsWithChildren) {
  return <WorkflowStateProvider>{children}</WorkflowStateProvider>;
}
