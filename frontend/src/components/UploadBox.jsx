import "./UploadBox.css";
import { useState } from "react";

export default function UploadBox() {
  const [arquivos, setArquivos] = useState([]);
  const [loading, setLoading] = useState(false);

  // selecionar arquivos
  const handleFiles = (e) => {
    setArquivos(Array.from(e.target.files));
  };

  // enviar arquivos (VERSÃO CORRIGIDA)
  const enviarArquivos = async () => {
    const formData = new FormData();

    arquivos.forEach((file) => {
      formData.append("files", file);
    });

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      console.log("Status RESPONSE:", response.status);

      // ✅ usa status HTTP (não quebra mais)
      if (response.status === 200) {
        alert("✅ Processamento concluído com sucesso!");
      } else {
        alert("⚠️ Processado, mas com retorno inesperado");
      }

    } catch (erro) {
      console.error("Erro ao enviar:", erro);
      alert("❌ Falha de conexão com o servidor");
    }

    setLoading(false);
  };

  // baixar relatório
  const baixarRelatorio = () => {
    window.open("http://127.0.0.1:8000/download/");
  };

  return (
    <div className="upload-container">

      <h2>📥 Upload de arquivos</h2>

      <p>
        Selecione os arquivos PDF para iniciar a leitura automática
      </p>

      <div className="upload-box">

        {/* INPUT OCULTO */}
        <input
          type="file"
          multiple
          accept=".pdf"
          id="fileInput"
          style={{ display: "none" }}
          onChange={handleFiles}
        />

        {/* BOTÃO DE SELEÇÃO */}
        <label htmlFor="fileInput" className="upload-button">
          Selecionar arquivos
        </label>

        <span className="info">
          200MB por arquivo • Formato PDF
        </span>

        {/* LISTA DE ARQUIVOS */}
        {arquivos.length > 0 && (
          <div className="file-list">

            {arquivos.map((file, index) => (
              <div key={index}>📄 {file.name}</div>
            ))}

            {/* BOTÃO PROCESSAR */}
            <button
              className="upload-button"
              onClick={enviarArquivos}
              disabled={loading}
            >
              {loading ? "⏳ Processando..." : "🚀 Processar"}
            </button>

            {/* BOTÃO BAIXAR */}
            <button
              className="download-button"
              onClick={baixarRelatorio}
            >
              📥 Baixar relatório
            </button>

          </div>
        )}

      </div>

    </div>
  );
}