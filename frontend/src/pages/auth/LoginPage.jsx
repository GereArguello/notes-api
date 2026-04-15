import { useNavigate } from "react-router-dom";
import LoginForm from "../../components/LoginForm";

function LoginPage({ onLogin }) {
  const navigate = useNavigate();

  const handleLoginSuccess = (token) => {
    onLogin(token);
    navigate("/subjects");
  };

  return (
    <div>
      <h1>Iniciar sesión</h1>

      <LoginForm
        onLogin={handleLoginSuccess}
        onSwitch={() => navigate("/register")}
      />
    </div>
  );
}

export default LoginPage;