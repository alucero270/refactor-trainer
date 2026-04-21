import Editor from "@monaco-editor/react";

type MonacoEditorPanelProps = {
  value: string;
  onChange?: (value: string) => void;
  readOnly?: boolean;
  title?: string;
  eyebrow?: string;
  aside?: string;
};

export function MonacoEditorPanel({
  value,
  onChange,
  readOnly = false,
  title = "Editor",
  eyebrow = "Python",
  aside,
}: MonacoEditorPanelProps) {
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2>{title}</h2>
        </div>
        {aside ? <span className="muted">{aside}</span> : null}
      </div>
      <Editor
        defaultLanguage="python"
        height="320px"
        onChange={(nextValue) => onChange?.(nextValue ?? "")}
        theme="vs-light"
        value={value}
        options={{ readOnly, minimap: { enabled: false } }}
      />
    </div>
  );
}
