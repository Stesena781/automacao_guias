import "./Header.css";
import logo from "../assets/logo.png";

export default function Header() {
  return (
    <div className="header">

      {/* LOGO (ESQUERDA) */}
      <div className="logo-container">
        <img src={logo} alt="logo da aplicação" className="logo-img" />
      </div>

      {/* MENU (DIREITA) */}
      <div className="menu">
        <span className="help">❓ Ajuda</span>

        <div className="user-container">
          <div className="user-circle">U</div>
          <span className="user-name">Usuário</span>
        </div>
      </div>

    </div>
  );
}
