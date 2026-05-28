from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os
from main import processar_guias, salvar_relatorio

app = FastAPI()

# ✅ LIBERA ACESSO DO REACT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PASTA_UPLOAD = "guias_pdf"
OUTPUT_FILE = "output/relatorio_guias.xlsx"

# ================== UPLOAD ==================
@app.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    try:
        os.makedirs(PASTA_UPLOAD, exist_ok=True)

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
    return FileResponse(
        OUTPUT_FILE,
        filename="relatorio_guias.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ================== SERVIR REACT ==================
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")
