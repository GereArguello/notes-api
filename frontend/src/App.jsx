import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider, useAuth } from "./context/AuthContext";

import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";

import SubjectsPage from "./pages/subjects/SubjectsPage";
import CreateSubjectPage from "./pages/subjects/CreateSubjectPage";
import EditSubjectPage from "./pages/subjects/EditSubjectPage";

import TopicsPage from "./pages/topics/TopicsPage";
import CreateTopicPage from "./pages/topics/CreateTopicPage";
import EditTopicPage from "./pages/topics/EditTopicPage";

import PagesPage from "./pages/pages/PagesPage";
import CreatePagePage from "./pages/pages/CreatePagePage";
import EditPagePage from "./pages/pages/EditPagePage";
import PageDetailPage from "./pages/pages/PageDetailPage";


function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}


function AppRoutes() {
  const { token } = useAuth();

  return (
    <BrowserRouter>
      <Routes>

        {/* 🔓 Públicas */}
        <Route
          path="/login"
          element={
            token ? <Navigate to="/subjects" /> : <LoginPage />
          }
        />

        <Route
          path="/register"
          element={
            token ? <Navigate to="/subjects" /> : <RegisterPage />
          }
        />

        {/* 🔐 protegidas */}
        <Route
          path="/subjects"
          element={
            <ProtectedRoute>
              <SubjectsPage />
            </ProtectedRoute>
          }
        />

          <Route
            path="/subjects/new"
            element={
              <ProtectedRoute>
                <CreateSubjectPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/subjects/:id/edit"
            element={
              <ProtectedRoute>
                <EditSubjectPage />
              </ProtectedRoute>
            }
          />

          {/* 🔐 Topics */}
          <Route
            path="/subjects/:subject_id"
            element={
              <ProtectedRoute>
                <TopicsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/subjects/:subject_id/topics/new"
            element={
              <ProtectedRoute>
                <CreateTopicPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/subjects/:subject_id/topics/:topic_id/edit"
            element={
              <ProtectedRoute>
                <EditTopicPage />
              </ProtectedRoute>
            }
          />

          {/* 🔐 Pages */}
          <Route
            path="/subjects/:subject_id/topics/:topic_id"
            element={
              <ProtectedRoute>
                <PagesPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/subjects/:subject_id/topics/:topic_id/pages/new"
            element={
              <ProtectedRoute>
                <CreatePagePage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/subjects/:subject_id/topics/:topic_id/pages/:page_id/edit"
            element={
              <ProtectedRoute>
                <EditPagePage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/subjects/:subject_id/topics/:topic_id/pages/:page_id"
            element={
              <ProtectedRoute>
                <PageDetailPage />
              </ProtectedRoute>
            }
          />

          {/* 🔁 Default */}
          <Route
            path="*"
            element={<Navigate to={token ? "/subjects" : "/login"} />}
          />

        </Routes>
      </BrowserRouter>
  );
}

export default App;