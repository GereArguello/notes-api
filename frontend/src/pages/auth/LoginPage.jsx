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
      <LoginForm
        onLogin={handleLoginSuccess}
        onSwitch={() => navigate("/register")}
      />
    </div>
  );
}

export default LoginPage;