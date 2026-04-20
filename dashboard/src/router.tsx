import { createBrowserRouter, Navigate } from "react-router-dom";
import Shell from "./components/layout/Shell";
import QueuePage from "./pages/QueuePage";
import ItemPage from "./pages/ItemPage";
import LogsPage from "./pages/LogsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Shell />,
    children: [
      { index: true, element: <Navigate to="/queue" replace /> },
      { path: "queue", element: <QueuePage /> },
      { path: "items/:id", element: <ItemPage /> },
      { path: "logs", element: <LogsPage /> },
    ],
  },
]);
