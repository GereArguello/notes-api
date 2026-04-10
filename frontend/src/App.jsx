import { useState } from "react";
import LoginForm from "./components/LoginForm";
import RegisterForm from "./components/RegisterForm";
import SubjectsPage from "./components/SubjectPage";

function App() {
  const [view, setView] = useState("login");
  const [token, setToken] = useState(localStorage.getItem("token"));

  //  si hay token → usuario logueado
  if (token) {
    return <SubjectsPage token={token}/>
  }

  if (view === "login") {
    return (
      <LoginForm
        onSwitch={() => setView("register")}
        onLogin={(token) => {
          localStorage.setItem("token", token);
          setToken(token);
        }}
      />
    );
  }

  return <RegisterForm onSwitch={() => setView("login")} />;
}

export default App;