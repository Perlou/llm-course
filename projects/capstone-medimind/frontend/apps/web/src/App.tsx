import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import HealthQAPage from "./pages/HealthQAPage";
import DrugSearchPage from "./pages/DrugSearchPage";
import ReportPage from "./pages/ReportPage";
import TriagePage from "./pages/TriagePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="health" element={<HealthQAPage />} />
        <Route path="drug" element={<DrugSearchPage />} />
        <Route path="report" element={<ReportPage />} />
        <Route path="triage" element={<TriagePage />} />
      </Route>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
    </Routes>
  );
}

export default App;
