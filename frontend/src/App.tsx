import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { RequireAuth } from "./components/RequireAuth";
import { RouteMeta } from "./components/RouteMeta";
import CoachesPage from "./pages/CoachesPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import MatchesPage from "./pages/MatchesPage";
import PlayersPage from "./pages/PlayersPage";
import StatisticsPage from "./pages/StatisticsPage";
import TeamsPage from "./pages/TeamsPage";
import TrainingPage from "./pages/TrainingPage";
import UsersPage from "./pages/UsersPage";

export default function App() {
  return (
    <>
      <RouteMeta />
      <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/*"
        element={
          <RequireAuth>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/teams" element={<TeamsPage />} />
                <Route path="/players" element={<PlayersPage />} />
                <Route path="/coaches" element={<CoachesPage />} />
                <Route path="/matches" element={<MatchesPage />} />
                <Route path="/training" element={<TrainingPage />} />
                <Route
                  path="/statistics"
                  element={<StatisticsPage />}
                />
                <Route path="/users" element={<UsersPage />} />
                <Route
                  path="*"
                  element={<Navigate to="/" replace />}
                />
              </Routes>
            </Layout>
          </RequireAuth>
        }
      />
    </Routes>
    </>
  );
}
