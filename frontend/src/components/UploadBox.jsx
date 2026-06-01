import "./UploadBox.css";
import { useState } from "react";

export default function UploadBox() {
  const [arquivos, setArquivos] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFiles = (e) => {
    setArquivos(Array.from(e.target.files));
  };

  const limparArquivos = () => {
    setArquivos([]);
  };

  // ✅ FUNÇÃO CORRIGIDA
  const enviarArquivos = async () => {
    const formData = new FormData();

    arquivos.forEach((file) => {
      formData.append("files", file);
    });

    setLoading(true);

    try {
      const response = await fetch(
        "https://automacao-guias.onrender.com/upload/",
        {
          method: "POST",
          body: formData,
        }
      );

      // ✅ RECEBE O ARQUIVO EXCEL
      const blob = await response.blob();

      // ✅ CRIA DOWNLOAD AUTOMÁTICO
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "relatorio_guias.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();

      alert("✅ Processamento concluído e download iniciado!");

    } catch (erro) {
      console.error("Erro:", erro);
      alert("❌ Falha no envio ou processamento");
    }

    setLoading(false);
  };

  return (
    <div className="upload-container">

      <h2>📥 Upload de arquivos</h2>

      <p>
        Selecione os arquivos PDF para iniciar o processamento
      </p>

      <div className="upload-box">

        <input
          type="file"
          multiple
          accept=".pdf"
          id="fileInput"
          style={{ display: "none" }}
          onChange={handleFiles}
        />

        <label htmlFor="fileInput" className="upload-button">
          Selecionar arquivos
        </label>

        <span className="info">
          200MB por arquivo • PDF
        </span>

        {arquivos.length > 0 && (
          <div className="file-list">

            {arquivos.map((file, index) => (
              <div key={index}>📄 {file.name}</div>
            ))}

            <button
              className="upload-button"
              onClick={enviarArquivos}
              disabled={loading}
            >
              {loading ? "⏳ Processando..." : "🚀 Processar"}
            </button>

            <button
              className="clear-button"
              onClick={limparArquivos}
            >
              🗑️ Limpar arquivos
            </button>

          </div>
        )}

      </div>

    </div>
  );
}
