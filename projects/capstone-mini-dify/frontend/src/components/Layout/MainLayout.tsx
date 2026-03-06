import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

export default function MainLayout() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main
        className="flex-1 overflow-y-auto"
        style={{ backgroundColor: "var(--color-bg)" }}
      >
        <Outlet />
      </main>
    </div>
  );
}
