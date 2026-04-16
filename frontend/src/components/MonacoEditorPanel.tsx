import Editor from "@monaco-editor/react";

type MonacoEditorPanelProps = {
  value: string;
};

export function MonacoEditorPanel({ value }: MonacoEditorPanelProps) {
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">Editor</p>
          <h2>Monaco placeholder</h2>
        </div>
        <span className="muted">Read-only scaffold panel</span>
      </div>
      <Editor
        defaultLanguage="python"
        height="320px"
        theme="vs-light"
        value={value}
        options={{ readOnly: true, minimap: { enabled: false } }}
      />
    </div>
  );
}

