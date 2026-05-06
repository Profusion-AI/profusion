import { createBrowserRouter, Navigate } from "react-router-dom";
import Shell from "./components/layout/Shell";
import QueuePage from "./pages/QueuePage";
import ItemPage from "./pages/ItemPage";
import LogsPage from "./pages/LogsPage";
import FailuresPage from "./pages/FailuresPage";
import ApprovalsPage from "./pages/ApprovalsPage";
import EvidencePage from "./pages/EvidencePage";
import SystemPage from "./pages/SystemPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Shell />,
    children: [
      { index: true, element: <Navigate to="/queue" replace /> },
      { path: "queue", element: <QueuePage /> },
      { path: "failures", element: <FailuresPage /> },
      { path: "approvals", element: <ApprovalsPage /> },
      { path: "evidence", element: <EvidencePage /> },
      { path: "items/:id", element: <ItemPage /> },
      { path: "logs", element: <LogsPage /> },
      { path: "system", element: <SystemPage /> },
    ],
  },
]);
