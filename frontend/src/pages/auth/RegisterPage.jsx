import { useNavigate } from "react-router-dom";
import RegisterForm from "../../components/RegisterForm";

function RegisterPage() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Crear cuenta</h1>

      <RegisterForm onSwitch={() => navigate("/login")} />
    </div>
  );
}

export default RegisterPage;