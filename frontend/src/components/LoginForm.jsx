import { useState } from "react";

function LoginForm({ onSwitch, onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: email, // OAuth2 espera "username"
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage("Error: " + JSON.stringify(data));
        return;
      }

      
      onLogin(data.access_token);
      setMessage("Login correcto ✅");
    } catch (error) {
      console.error(error);
      setMessage("Error de conexión ❌");
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Iniciar sesión</h1>

      <form onSubmit={handleSubmit}>
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

      <p>
        ¿No tenés cuenta?{" "}
        <button onClick={onSwitch}>Crear una</button>
      </p>

      {message && <p>{message}</p>}
    </div>
  );
}

export default LoginForm;