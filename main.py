import os
import re
import pandas as pd
from PyPDF2 import PdfReader
import logging
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse

# ================= CONFIG =================
OUTPUT_DIR = "output"
TEMP_DIR = "temp"
LOG_FILE = "log_execucao.txt"

# garante pasta temp e output
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= FASTAPI =================
app = FastAPI()

# ================= LOG =================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ================= VALIDAR NOME =================
def validar_nome(nome):
    padrao = r'_GUIA_.*_\d+-\d{2}\.pdf$'
    return bool(re.search(padrao, nome))


# ================= EXTRAÇÃO DE TEXTO =================
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


# ================= NUMERO DA GUIA =================
def extrair_numero_guia(nome_arquivo):
    match = re.search(r'\d{6,}-\d{2}', nome_arquivo)
    return match.group() if match else "Não encontrado"


# ================= VALOR TOTAL =================
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

    except Exception as e:
        logging.error(f"Erro ao converter valores: {e}")
        return None


# ================= LOCALIDADE =================
def extrair_localidade(texto):
    match = re.search(
        r'LOCALIDADE DE ORIGEM\s*(.*?)\n',
        texto,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return "Não encontrado"


# ================= PROCESSAMENTO (UPLOAD ✅) =================
def processar_arquivos(files):
    resultados = []
    erros = []

    for file in files:
        try:
            print(f"\n📄 Processando: {file.filename}")

            caminho_temp = f"{TEMP_DIR}/{file.filename}"

            # salva temporário
            with open(caminho_temp, "wb") as f:
                f.write(file.file.read())

            texto = extrair_texto_pdf(caminho_temp)

            print(f"→ Tamanho do texto: {len(texto)}")

            numero_guia = extrair_numero_guia(file.filename)
            total = extrair_valor_total(texto)
            localidade = extrair_localidade(texto)

            if total is None:
                logging.warning(f"Valor não encontrado: {file.filename}")
                total = 0

            print(f"→ Número: {numero_guia}")
            print(f"→ Localidade: {localidade}")
            print(f"→ Valor: {total}")

            resultados.append({
                "Arquivo": file.filename,
                "Número Guia": numero_guia,
                "Localidade": localidade,
                "Valor (R$)": total,
                "Status": "OK" if total > 0 else "Verificar"
            })

        except Exception as e:
            print(f"⚠️ Erro em {file.filename}: {e}")
            logging.error(f"Erro: {file.filename} - {e}")

            erros.append({
                "Arquivo": file.filename,
                "Erro": str(e)
            })

    return resultados, erros


# ================= RELATÓRIO =================
def salvar_relatorio(resultados, erros):
    df = pd.DataFrame(resultados)
    df_erros = pd.DataFrame(erros)

    total_geral = df["Valor (R$)"].sum() if not df.empty else 0

    resumo = pd.DataFrame({
        "Descrição": ["Total de Guias", "Total Geral (R$)", "Erros"],
        "Valor": [len(df), total_geral, len(df_erros)]
    })

    caminho = os.path.join(OUTPUT_DIR, "relatorio_guias.xlsx")

    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Dados", index=False)
        resumo.to_excel(writer, sheet_name="Resumo", index=False)

        if not df_erros.empty:
            df_erros.to_excel(writer, sheet_name="Erros", index=False)

    return caminho


# ================= ROTAS =================

@app.post("/upload/")
async def upload(files: list[UploadFile]):

    resultados, erros = processar_arquivos(files)

    caminho = salvar_relatorio(resultados, erros)

    return {"mensagem": "Processamento concluído"}


@app.get("/download/")
def download():
    caminho = os.path.join(OUTPUT_DIR, "relatorio_guias.xlsx")
    return FileResponse(caminho, filename="relatorio_guias.xlsx")