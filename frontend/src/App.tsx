import { NavLink, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { AttemptFeedbackPage } from "./pages/AttemptFeedbackPage";
import { CandidateListPage } from "./pages/CandidateListPage";
import { ExerciseViewPage } from "./pages/ExerciseViewPage";
import { GitHubImportPage } from "./pages/GitHubImportPage";
import { ProviderSetupPage } from "./pages/ProviderSetupPage";
import { UploadPastePage } from "./pages/UploadPastePage";

const navItems = [
  { to: "/", label: "Provider Setup" },
  { to: "/upload", label: "Upload / Paste" },
  { to: "/github", label: "GitHub Import" },
  { to: "/candidates", label: "Candidate List" },
  { to: "/exercise", label: "Exercise View" },
  { to: "/feedback", label: "Attempt Feedback" },
];

export default function App() {
  return (
    <Layout
      header={
        <>
          <div>
            <p className="eyebrow">Refactor Trainer</p>
            <h1>Initial product scaffold</h1>
          </div>
          <nav className="nav">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </>
      }
    >
      <Routes>
        <Route path="/" element={<ProviderSetupPage />} />
        <Route path="/upload" element={<UploadPastePage />} />
        <Route path="/github" element={<GitHubImportPage />} />
        <Route path="/candidates" element={<CandidateListPage />} />
        <Route path="/exercise" element={<ExerciseViewPage />} />
        <Route path="/feedback" element={<AttemptFeedbackPage />} />
      </Routes>
    </Layout>
  );
}

