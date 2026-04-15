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

        {/* Ruta pública */}
        <Route 
          path="/login" 
          element={
            token 
              ? <Navigate to="/subjects" /> 
              : <LoginPage onLogin={handleLogin} />
          } 
        />

        {/* Ruta pública */}
        <Route 
          path="/register" 
          element={
            token 
              ? <Navigate to="/subjects" /> 
              : <RegisterPage />
          } 
        /> 

        {/* Ruta protegida */}
        <Route 
          path="/subjects" 
          element={
            token 
              ? <SubjectsPage token={token} onLogout={handleLogout} />
              : <Navigate to="/login" />
          } 
        />

        <Route
          path="/subjects/new"
          element={
            token 
              ? <CreateSubjectPage token={token} />
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
        
        <Route
          path="/subjects/:subject_id"
          element={
            token 
              ? <TopicsPage token={token} />
              : <Navigate to="/login" />
          }
        />


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

        {/* Ruta por defecto */}
        <Route 
          path="*" 
          element={<Navigate to={token ? "/subjects" : "/login"} />} 
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;