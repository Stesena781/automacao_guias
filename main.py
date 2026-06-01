import os
import re
import pandas as pd
from PyPDF2 import PdfReader
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ================= CONFIG =================
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI()

# ✅ CORS (ESSENCIAL para frontend no Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pode restringir depois
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= EXTRAÇÃO =================

def extrair_texto_pdf(caminho):
    reader = PdfReader(caminho)
    texto = ""

    for pagina in reader.pages:
        conteudo = pagina.extract_text()
        if conteudo:
            texto += conteudo + "\n"

    return texto


def extrair_numero_guia(nome_arquivo):
    match = re.search(r'\d{6,}-\d{2}', nome_arquivo)
    return match.group() if match else "Não encontrado"


def extrair_localidade(texto):
    match = re.search(
        r'LOCALIDADE DE ORIGEM\s*(.*?)-\s*SP',
        texto,
        re.IGNORECASE
    )

    if match:
        return match.group(0).strip()

    return "Não encontrado"


def extrair_valor_total(texto):
    valores = re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}', texto)

    if not valores:
        return 0

    valores_convertidos = [
        float(v.replace('.', '').replace(',', '.'))
        for v in valores
    ]

    return max(valores_convertidos)

# ================= PROCESSAMENTO =================

def processar_arquivos(files):
    resultados = []

    for file in files:
        try:
            print(f"📄 Processando: {file.filename}")

            caminho = os.path.join(TEMP_DIR, file.filename)

            with open(caminho, "wb") as f:
                f.write(file.file.read())

            texto = extrair_texto_pdf(caminho)

            resultados.append({
                "Arquivo": file.filename,
                "Número Guia": extrair_numero_guia(file.filename),
                "Localidade": extrair_localidade(texto),
                "Valor (R$)": extrair_valor_total(texto)
            })

            os.remove(caminho)

        except Exception as e:
            resultados.append({
                "Arquivo": file.filename,
                "Erro": str(e)
            })

    return resultados

# ================= RELATÓRIO =================

def gerar_excel(dados):
    caminho = "relatorio_guias.xlsx"

    df = pd.DataFrame(dados)

    total_geral = df["Valor (R$)"].sum() if "Valor (R$)" in df else 0

    resumo = pd.DataFrame({
        "Descrição": ["Total de Guias", "Total Geral (R$)"],
        "Valor": [len(df), total_geral]
    })

    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Dados", index=False)
        resumo.to_excel(writer, sheet_name="Resumo", index=False)

    return caminho

# ================= API =================

@app.post("/upload/")
async def upload(files: list[UploadFile] = File(...)):

    if not files:
        return JSONResponse({"erro": "Nenhum arquivo enviado"})

    dados = processar_arquivos(files)

    caminho = gerar_excel(dados)

    return FileResponse(
        caminho,
        filename="relatorio_guias.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )