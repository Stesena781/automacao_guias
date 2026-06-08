import pdfplumber
import pandas as pd
import re
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
import io

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FUNÇÃO PARA EXTRAIR DADOS
def extrair_dados_pdf(file_bytes):
    texto = ""

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                texto += txt + "\n"

    # LOCALIDADE
    localidade = None
    match_local = re.search(r'LOCALIDADE DE ORIGEM (.+)', texto)
    if match_local:
        localidade = match_local.group(1).strip()

    # DESCRIÇÃO
    descricao = None
    desc_match = re.search(
        r'DESCRIÇÃO DO MATERIAL(.*?)(Valor Total|ÍTEM|$)',
        texto,
        re.S
    )
    if desc_match:
        descricao = desc_match.group(1).strip()

    # PESO
    pesos = re.findall(
        r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*(?=R\$)',
        texto
    )
    peso = pesos[-1] if pesos else ""

    # VALOR TOTAL
    valores = re.findall(
        r'R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
        texto
    )
    valor_total = valores[-1] if valores else ""

    return {
        "Localidade": localidade,
        "Descricao": descricao,
        "Peso (kg)": peso,
        "Valor Total": valor_total
    }

# ENDPOINT
@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    resultados = []

    for file in files:
        file_bytes = await file.read()
        dados = extrair_dados_pdf(file_bytes)
        resultados.append(dados)

    # cria dataframe
    df = pd.DataFrame(resultados)

    # gera excel em memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=relatorio_guias.xlsx"}
    )
