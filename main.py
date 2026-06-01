import os
import re
import pandas as pd
from PyPDF2 import PdfReader
import logging
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, JSONResponse

# ================= CONFIG =================
OUTPUT_DIR = "output"
TEMP_DIR = "temp"
LOG_FILE = "log_execucao.txt"

# cria pastas
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ variável global para guardar o último relatório
ultimo_relatorio = None

# ================= FASTAPI =================
app = FastAPI()

# ================= LOG =================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ================= EXTRAÇÃO =================
def extrair_texto_pdf(caminho):
    try:
        reader = PdfReader(caminho)
        texto = ""

        for pagina in reader.pages:
            conteudo = pagina.extract_text()
            if conteudo:
                texto += conteudo + "\n"

        return texto

    except Exception as e:
        logging.error(f"Erro ao ler PDF {caminho}: {e}")
        return ""


def extrair_numero_guia(nome_arquivo):
    match = re.search(r'\d{6,}-\d{2}', nome_arquivo)
    return match.group() if match else "Não encontrado"


def extrair_valor_total(texto):
    valores = re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}', texto)

    if not valores:
        return None

    try:
        valores_convertidos = [
            float(v.replace('.', '').replace(',', '.'))
            for v in valores
        ]
        return max(valores_convertidos)
    except:
        return None


def extrair_localidade(texto):
    match = re.search(r'LOCALIDADE DE ORIGEM\s*(.*?)\n', texto, re.IGNORECASE)
    return match.group(1).strip() if match else "Não encontrado"


# ================= PROCESSAMENTO =================
def processar_arquivos(files):
    resultados = []
    erros = []

    for file in files:
        try:
            print(f"\n📄 Processando: {file.filename}")

            caminho_temp = os.path.join(TEMP_DIR, file.filename)

            with open(caminho_temp, "wb") as f:
                f.write(file.file.read())

            texto = extrair_texto_pdf(caminho_temp)

            numero_guia = extrair_numero_guia(file.filename)
            total = extrair_valor_total(texto)
            localidade = extrair_localidade(texto)

            if total is None:
                total = 0

            resultados.append({
                "Arquivo": file.filename,
                "Número Guia": numero_guia,
                "Localidade": localidade,
                "Valor (R$)": total,
                "Status": "OK" if total > 0 else "Verificar"
            })

            os.remove(caminho_temp)

        except Exception as e:
            logging.error(f"Erro em {file.filename}: {e}")
            erros.append({
                "Arquivo": file.filename,
                "Erro": str(e)
            })

    return resultados, erros


# ================= RELATÓRIO =================
def salvar_relatorio(resultados, erros):
    global ultimo_relatorio

    caminho = os.path.join(OUTPUT_DIR, "relatorio_guias.xlsx")

    df = pd.DataFrame(resultados)
    df_erros = pd.DataFrame(erros)

    total_geral = df["Valor (R$)"].sum() if not df.empty else 0

    resumo = pd.DataFrame({
        "Descrição": ["Total de Guias", "Total Geral (R$)", "Erros"],
        "Valor": [len(df), total_geral, len(df_erros)]
    })

    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Dados", index=False)
        resumo.to_excel(writer, sheet_name="Resumo", index=False)

        if not df_erros.empty:
            df_erros.to_excel(writer, sheet_name="Erros", index=False)

    print("✅ Relatório salvo em:", caminho)

    # ✅ guarda o caminho em memória
    ultimo_relatorio = caminho

    return caminho


# ================= ROTAS =================

@app.post("/upload/")
async def upload(files: list[UploadFile]):

    global ultimo_relatorio

    if not files:
        return JSONResponse({"status": "erro", "message": "Nenhum arquivo enviado"})

    resultados, erros = processar_arquivos(files)

    caminho = salvar_relatorio(resultados, erros)

    if not os.path.exists(caminho):
        return JSONResponse({"status": "erro", "message": "Erro ao gerar relatório"})

    return {"status": "ok", "mensagem": "Processamento concluído"}


@app.get("/download/")
def download():
    global ultimo_relatorio

    if not ultimo_relatorio or not os.path.exists(ultimo_relatorio):
        return JSONResponse({
            "status": "erro",
            "message": "Relatório ainda não foi gerado"
        })

    return FileResponse(
        ultimo_relatorio,
        filename="relatorio_guias.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
