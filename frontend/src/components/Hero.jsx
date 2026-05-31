import "./Hero.css";
import mascote from "../assets/mascote.png";

export default function Hero() {
  return (
    <div className="hero">

      {/* TEXTO ESQUERDA */}
      <div className="hero-left">

        <span className="tag">🌿 DESMOBILIZAÇÃO DE SITES</span>

        <h1>
          Sistema automático <br />
          de leitura de guias
        </h1>

        <p>
          Faça upload das suas guias em PDF e extraia os dados de forma rápida,
          segura e automatizada.
        </p>

        <div className="benefits">
          <span>⚡ Mais agilidade</span>
          <span>🔐 Mais segurança</span>
          <span>🌱 Mais sustentabilidade</span>
        </div>

      </div>

      {/* MASCOTE DIREITA */}
      <div className="hero-right">
        <img src={mascote} alt="mascote" />
      </div>

    </div>
  );
}
