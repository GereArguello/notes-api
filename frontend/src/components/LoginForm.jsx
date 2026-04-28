import { useState } from "react";
// TO DO: Crear fetchPublic
import { fetchWithAuth } from "../api/fetchWithAuth";

function LoginForm({ onSwitch, onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const data = await fetchWithAuth("/auth/login", null, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      onLogin(data.access_token);
      setMessage("Login correcto ✅");

    } catch (error) {
      console.error("Login error:", error);
      setMessage(error.message || "Error de conexión ❌");
    }
  };

  return (
    <div className="auth-container">
      <h1>Iniciar sesión</h1>

      <form onSubmit={handleSubmit} className="auth-form">
        <div>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit">Ingresar</button>
      </form>

      <p className="auth-switch">
        ¿No tenés cuenta?{" "}
        <button onClick={onSwitch}>Crear una</button>
      </p>

      {message && <p className="auth-message">{message}</p>}
    </div>
  );
}

export default LoginForm;
