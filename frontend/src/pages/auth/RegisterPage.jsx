import { useNavigate } from "react-router-dom";
import RegisterForm from "../../components/RegisterForm";

function RegisterPage() {
  const navigate = useNavigate();

  return (
    <div>
      <RegisterForm onSwitch={() => navigate("/login")} />
    </div>
  );
}

export default RegisterPage;