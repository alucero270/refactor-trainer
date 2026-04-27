import { createContext, useContext, useState } from "react";
import type { PropsWithChildren } from "react";

import type {
  AttemptFeedbackResponse,
  Candidate,
  Exercise,
  HintBundle,
  SubmitCodeResponse,
} from "../types/api";

type WorkflowState = {
  submission: SubmitCodeResponse | null;
  candidates: Candidate[];
  selectedCandidate: Candidate | null;
  exercise: Exercise | null;
  editorCode: string;
  hints: HintBundle | null;
  feedback: AttemptFeedbackResponse | null;
};

type WorkflowStateContextValue = WorkflowState & {
  setSubmission: (submission: SubmitCodeResponse) => void;
  setCandidates: (candidates: Candidate[]) => void;
  selectCandidate: (candidate: Candidate) => void;
  setExercise: (exercise: Exercise) => void;
  setEditorCode: (code: string) => void;
  setHints: (hints: HintBundle) => void;
  setFeedback: (feedback: AttemptFeedbackResponse) => void;
};

const WorkflowStateContext = createContext<WorkflowStateContextValue | null>(null);

const initialState: WorkflowState = {
  submission: null,
  candidates: [],
  selectedCandidate: null,
  exercise: null,
  editorCode: "",
  hints: null,
  feedback: null,
};

export function WorkflowStateProvider({ children }: PropsWithChildren) {
  const [state, setState] = useState<WorkflowState>(initialState);

  const setSubmission = (submission: SubmitCodeResponse) =>
    setState((current) =>
      current.submission?.submission_id === submission.submission_id
        ? { ...current, submission }
        : { ...initialState, submission },
    );

  const setCandidates = (candidates: Candidate[]) =>
    setState((current) => ({ ...current, candidates }));

  const selectCandidate = (candidate: Candidate) =>
    setState((current) =>
      current.selectedCandidate?.id === candidate.id
        ? { ...current, selectedCandidate: candidate }
        : {
            ...current,
            selectedCandidate: candidate,
            exercise: null,
            editorCode: "",
            hints: null,
            feedback: null,
          },
    );

  const setExercise = (exercise: Exercise) =>
    setState((current) =>
      current.exercise?.exercise_id === exercise.exercise_id
        ? { ...current, exercise }
        : { ...current, exercise, editorCode: "", hints: null, feedback: null },
    );

  const setEditorCode = (editorCode: string) =>
    setState((current) => ({ ...current, editorCode }));

  const setHints = (hints: HintBundle) =>
    setState((current) => ({ ...current, hints }));

  const setFeedback = (feedback: AttemptFeedbackResponse) =>
    setState((current) => ({ ...current, feedback }));

  const value: WorkflowStateContextValue = {
    ...state,
    setSubmission,
    setCandidates,
    selectCandidate,
    setExercise,
    setEditorCode,
    setHints,
    setFeedback,
  };

  return <WorkflowStateContext.Provider value={value}>{children}</WorkflowStateContext.Provider>;
}

export function useWorkflowState() {
  const context = useContext(WorkflowStateContext);
  if (!context) {
    throw new Error("useWorkflowState must be used within WorkflowStateProvider.");
  }
  return context;
}
