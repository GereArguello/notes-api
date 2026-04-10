import { useState } from "react";
import LoginForm from "./components/LoginForm";
import RegisterForm from "./components/RegisterForm";

function App() {
  const [view, setView] = useState("login");
  const [token, setToken] = useState(null);

  //  si hay token → usuario logueado
  if (token) {
    return <h1>Estás logueado ✅</h1>;
  }

  if (view === "login") {
    return (
      <LoginForm
        onSwitch={() => setView("register")}
        onLogin={(token) => setToken(token)}
      />
    );
  }

  return <RegisterForm onSwitch={() => setView("login")} />;
}

export default App;