import "./Header.css";

export default function Header() {
  return (
    <div className="header">
      
      {/* LOGO (ESQUERDA) */}
      <div className="logo">
        <img src="/logo.png" alt="logo" />
      </div>

      {/* MENU (DIREITA) */}
      <div className="menu">
        <span className="help">❓ Ajuda</span>

        <div className="user-container">
          <div className="user-circle">U</div>
          <span>Usuário</span>
        </div>
      </div>

    </div>
  );
}
