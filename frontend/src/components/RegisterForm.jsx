import { useState } from "react";

function RegisterForm({ onSwitch }) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault(); // evita recarga de página

    try {
      const response = await fetch("http://localhost:8000/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          email,
          password,
          password2,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage("Error: " + JSON.stringify(data));
        return;
      }

      setMessage("Usuario creado correctamente ✅");

      setTimeout(() => {
      onSwitch();
      }, 2000);
      } catch (error) {
        setMessage("Error de conexión ❌");
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