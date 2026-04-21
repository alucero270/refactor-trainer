import { createContext, useContext, useMemo, useState } from "react";
import type { PropsWithChildren } from "react";

import type { AttemptFeedbackResponse, Candidate, Exercise, SubmitCodeResponse } from "../types/api";

type WorkflowState = {
  submission: SubmitCodeResponse | null;
  candidates: Candidate[];
  selectedCandidate: Candidate | null;
  exercise: Exercise | null;
  editorCode: string;
  feedback: AttemptFeedbackResponse | null;
};

type WorkflowStateContextValue = WorkflowState & {
  setSubmission: (submission: SubmitCodeResponse) => void;
  setCandidates: (candidates: Candidate[]) => void;
  selectCandidate: (candidate: Candidate) => void;
  setExercise: (exercise: Exercise) => void;
  setEditorCode: (code: string) => void;
  setFeedback: (feedback: AttemptFeedbackResponse) => void;
};

const WorkflowStateContext = createContext<WorkflowStateContextValue | null>(null);

const initialState: WorkflowState = {
  submission: null,
  candidates: [],
  selectedCandidate: null,
  exercise: null,
  editorCode: "",
  feedback: null,
};

export function WorkflowStateProvider({ children }: PropsWithChildren) {
  const [state, setState] = useState<WorkflowState>(initialState);

  const value = useMemo<WorkflowStateContextValue>(
    () => ({
      ...state,
      setSubmission: (submission) =>
        setState({
          submission,
          candidates: [],
          selectedCandidate: null,
          exercise: null,
          editorCode: "",
          feedback: null,
        }),
      setCandidates: (candidates) =>
        setState((current) => ({
          ...current,
          candidates,
          selectedCandidate: null,
          exercise: null,
          editorCode: "",
          feedback: null,
        })),
      selectCandidate: (candidate) =>
        setState((current) => ({
          ...current,
          selectedCandidate: candidate,
          exercise: null,
          editorCode: "",
          feedback: null,
        })),
      setExercise: (exercise) =>
        setState((current) => ({
          ...current,
          exercise,
          editorCode: "",
          feedback: null,
        })),
      setEditorCode: (editorCode) =>
        setState((current) => ({
          ...current,
          editorCode,
        })),
      setFeedback: (feedback) =>
        setState((current) => ({
          ...current,
          feedback,
        })),
    }),
    [state],
  );

  return <WorkflowStateContext.Provider value={value}>{children}</WorkflowStateContext.Provider>;
}

export function useWorkflowState() {
  const context = useContext(WorkflowStateContext);
  if (!context) {
    throw new Error("useWorkflowState must be used within WorkflowStateProvider.");
  }
  return context;
}
