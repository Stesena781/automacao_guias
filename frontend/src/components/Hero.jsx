import "./Hero.css";

export default function Hero() {
  return (
    <div className="hero">

      <div className="hero-left">

        <span className="tag">
          🌿 DESMOBILIZAÇÃO DE SITES
        </span>

        <h1>
          Sistema automático <br />
          de leitura de guias
        </h1>

        <p>
          Faça upload das suas guias em PDF e extraia os dados
          de forma rápida, segura e automatizada.
        </p>

        <div className="benefits">
          <div>⚡ Mais agilidade</div>
          <div>🔐 Mais segurança</div>
          <div>🌱 Mais sustentabilidade</div>
        </div>

      </div>

      {/* 👉 MASCOTE AQUI */}
      <div className="hero-right">
        <img src="/mascote.png" alt="mascote" />
      </div>

    </div>
  );
}
