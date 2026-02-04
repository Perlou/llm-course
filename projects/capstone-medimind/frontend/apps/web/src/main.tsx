import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { configure } from "@medimind/api-client";
import App from "./App";
import "./index.css";

// 配置 API 客户端
configure({
  baseUrl: "/api/v1",
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
