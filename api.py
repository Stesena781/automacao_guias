from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os

# ✅ IMPORT PROTEGIDO (NÃO QUEBRA O RENDER)
try:
    from main import processar_guias, salvar_relatorio
except Exception as e:
    print("Erro ao importar main:", e)
    processar_guias = None
    salvar_relatorio = None

app = FastAPI()

# ✅ LIBERA ACESSO DO FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PASTA_UPLOAD = "guias_pdf"
OUTPUT_FILE = "output/relatorio_guias.xlsx"

# ✅ ROTA DE TESTE (IMPORTANTE PARA VALIDAR DEPLOY)
@app.get("/")
def home():
    return {"status": "API rodando ✅"}

# ================== UPLOAD ==================
@app.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    try:
        # ✅ verifica se processamento está disponível
        if processar_guias is None:
            return {"status": "erro", "message": "Processamento indisponível no momento"}

        os.makedirs(PASTA_UPLOAD, exist_ok=True)
        os.makedirs("output", exist_ok=True)

        # limpa pasta
        for f in os.listdir(PASTA_UPLOAD):
            os.remove(os.path.join(PASTA_UPLOAD, f))

        # salva arquivos enviados
        for file in files:
            caminho = os.path.join(PASTA_UPLOAD, file.filename)
            with open(caminho, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # processa
        resultados, erros = processar_guias()
        salvar_relatorio(resultados, erros)

        return {
            "status": "ok",
            "message": "Processado com sucesso",
            "total_processados": len(resultados),
            "erros": len(erros)
        }

    except Exception as e:
        return {
            "status": "erro",
            "message": str(e)
        }

# ================== DOWNLOAD ==================
@app.get("/download/")
def download():
    if os.path.exists(OUTPUT_FILE):
        return FileResponse(
            OUTPUT_FILE,
            filename="relatorio_guias.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    return {"status": "erro", "message": "Arquivo não encontrado"}