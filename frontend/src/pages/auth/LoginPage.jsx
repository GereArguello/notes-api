import { useNavigate } from "react-router-dom";
import LoginForm from "../../components/LoginForm";
import { useAuth } from "../../context/AuthContext";

function LoginPage({ onLogin }) {
  const navigate = useNavigate();
  const {login} = useAuth();

  const handleLoginSuccess = (token) => {
    login(token);
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