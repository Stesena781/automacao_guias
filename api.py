from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os

# ================= IMPORT PROCESSAMENTO =================
try:
    from main import processar_guias, salvar_relatorio
except Exception as e:
    print("Erro ao importar main:", e)
    processar_guias = None
    salvar_relatorio = None

# ================= APP =================
app = FastAPI()

# ✅ CORS (libera React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= CONFIG =================
PASTA_UPLOAD = "guias_pdf"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "relatorio_guias.xlsx")

# ================= UPLOAD =================
@app.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    try:
        if processar_guias is None or salvar_relatorio is None:
            return {
                "status": "erro",
                "message": "Módulo de processamento indisponível"
            }

        os.makedirs(PASTA_UPLOAD, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # limpa pasta
        for f in os.listdir(PASTA_UPLOAD):
            caminho = os.path.join(PASTA_UPLOAD, f)
            if os.path.isfile(caminho):
                os.remove(caminho)

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
            "message": "Processamento concluído",
            "total_processados": len(resultados),
            "total_erros": len(erros)
        }

    except Exception as e:
        print("Erro no upload:", e)
        return {
            "status": "erro",
            "message": str(e)
        }

# ================= DOWNLOAD =================
@app.get("/download/")
def download():
    if os.path.exists(OUTPUT_FILE):
        return FileResponse(
            OUTPUT_FILE,
            filename="relatorio_guias.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    return {
        "status": "erro",
        "message": "Relatório ainda não foi gerado"
    }

# ================= FRONTEND (REACT) =================
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")
