import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "./components/Layout/MainLayout";
import ModelHubPage from "./pages/ModelHub";
import PromptStudioPage from "./pages/PromptStudio";
import DatasetsPage from "./pages/Datasets";
import AgentBuilderPage from "./pages/AgentBuilder";
import WorkflowPage from "./pages/Workflow";
import AppsPage from "./pages/Apps";
import AnalyticsPage from "./pages/Analytics";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Navigate to="/models" replace />} />
          <Route path="/models" element={<ModelHubPage />} />
          <Route path="/prompts" element={<PromptStudioPage />} />
          <Route path="/datasets" element={<DatasetsPage />} />
          <Route path="/agents" element={<AgentBuilderPage />} />
          <Route path="/workflows" element={<WorkflowPage />} />
          <Route path="/apps" element={<AppsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
