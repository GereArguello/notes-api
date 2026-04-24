import { useState } from "react";
// TO DO: Crear fetchPublic
import { fetchWithAuth } from "../api/fetchWithAuth";

function RegisterForm({ onSwitch }) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await fetchWithAuth("/users", null, {
        method: "POST",
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          email,
          password,
          password2,
        }),
      });

      setMessage("Usuario creado correctamente ✅");

      setTimeout(() => {
        onSwitch();
      }, 1500);

    } catch (error) {
      console.error("Register error:", error);
      setMessage(error.message || "Error de conexión ❌");
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Crear usuario</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="text"
            placeholder="Nombre"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
        </div>

        <div>
          <input
            type="text"
            placeholder="Apellido"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
        </div>

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

        <div>
          <input
            type="password"
            placeholder="Confirmar password"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            required
          />
        </div>

        <button type="submit">Crear usuario</button>
      </form>

      <p>
        ¿Ya tenés cuenta?{" "}
        <button onClick={onSwitch}>Iniciar sesión</button>
      </p>

      {message && <p>{message}</p>}
    </div>
  );
}

export default RegisterForm;