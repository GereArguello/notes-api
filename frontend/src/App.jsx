import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

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
  const [token, setToken] = useState(() => localStorage.getItem("token"));

  const handleLogin = (token) => {
    localStorage.setItem("token", token);
    setToken(token);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  return (
    <BrowserRouter>
      <Routes>

        {/* 🔓 Públicas */}
        <Route
          path="/login"
          element={
            token
              ? <Navigate to="/subjects" />
              : <LoginPage onLogin={handleLogin} />
          }
        />

        <Route
          path="/register"
          element={
            token
              ? <Navigate to="/subjects" />
              : <RegisterPage />
          }
        />

        {/* 🔐 Subjects */}
        <Route
          path="/subjects/new"
          element={
            token
              ? <CreateSubjectPage token={token} />
              : <Navigate to="/login" />
          }
        />

        {/* 🔐 Pages - Create */}
        <Route
          path="/subjects/:subject_id/topics/:topic_id/pages/new"
          element={
            token
              ? <CreatePagePage token={token} />
              : <Navigate to="/login" />
          }
        />

        {/* 🔐 Pages - Edit */}
        <Route
          path="/subjects/:subject_id/topics/:topic_id/pages/:page_id/edit"
          element={
            token
              ? <EditPagePage token={token} />
              : <Navigate to="/login" />
          }
        />

        {/* 🔐 Page Detail */}
        <Route
          path="/subjects/:subject_id/topics/:topic_id/pages/:page_id"
          element={
            token
              ? <PageDetailPage token={token} />
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/subjects/:id/edit"
          element={
            token
              ? <EditSubjectPage token={token} />
              : <Navigate to="/login" />
          }
        />

        {/* 🔐 Topics */}
        <Route
          path="/subjects/:subject_id/topics/new"
          element={
            token
              ? <CreateTopicPage token={token} />
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/subjects/:subject_id/topics/:topic_id/edit"
          element={
            token
              ? <EditTopicPage token={token} />
              : <Navigate to="/login" />
          }
        />

        {/* 🔐 Pages (más específica que TopicsPage) */}
        <Route
          path="/subjects/:subject_id/topics/:topic_id"
          element={
            token
              ? <PagesPage token={token} />
              : <Navigate to="/login" />
          }
        />

        {/* 🔐 Topics list */}
        <Route
          path="/subjects/:subject_id"
          element={
            token
              ? <TopicsPage token={token} />
              : <Navigate to="/login" />
          }
        />

        {/* 🔐 Subjects list */}
        <Route
          path="/subjects"
          element={
            token
              ? <SubjectsPage token={token} onLogout={handleLogout} />
              : <Navigate to="/login" />
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