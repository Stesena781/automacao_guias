import os
import re
import pandas as pd
from PyPDF2 import PdfReader
import logging

# ================= CONFIG =================
PASTA_PDFS = "guias_pdf"
OUTPUT_DIR = "output"
LOG_FILE = "log_execucao.txt"

# ================= LOG =================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ================= VALIDAR NOME (FLEXÍVEL ✅) =================
def validar_nome(nome):
    # aceita variação de site e número
    padrao = r'_GUIA_.*_\d+-\d{2}\.pdf$'
    return bool(re.search(padrao, nome))


# ================= EXTRAÇÃO DE TEXTO =================
def extrair_texto_pdf(caminho):
    reader = PdfReader(caminho)
    texto = ""

    for pagina in reader.pages:
        conteudo = pagina.extract_text()
        if conteudo:
            texto += conteudo + "\n"

    return texto


# ================= NUMERO DA GUIA =================
def extrair_numero_guia(nome_arquivo):
    match = re.search(r'\d+-\d{2}', nome_arquivo)
    return match.group() if match else "Não encontrado"


# ================= VALOR TOTAL =================
def extrair_valor_total(texto):
    partes = texto.split("Valor Total")

    if len(partes) > 1:
        antes = partes[0]

        valores = re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}', antes)

        if valores:
            ultimo = valores[-1]

            return float(
                ultimo.replace('.', '').replace(',', '.')
            )

    return None


# ================= LOCALIDADE =================
def extrair_localidade(texto):
    match = re.search(
        r'LOCALIDADE DE ORIGEM\s*(.*?)\n',
        texto
    )

    if match:
        return match.group(1).strip()

    return "Não encontrado"


# ================= PROCESSAMENTO =================
def processar_guias():
    resultados = []
    erros = []

    print(f"📁 Lendo pasta: {PASTA_PDFS}")
    logging.info("Início do processamento")

    if not os.path.exists(PASTA_PDFS):
        print("❌ Pasta de PDFs NÃO encontrada!")
        logging.error("Pasta não encontrada")
        return [], []

    arquivos = sorted(os.listdir(PASTA_PDFS))

    if not arquivos:
        print("⚠️ Pasta vazia!")
        logging.warning("Pasta vazia")
        return [], []

    for arquivo in arquivos:
        if arquivo.lower().endswith(".pdf"):

            caminho = os.path.join(PASTA_PDFS, arquivo)
            print(f"📄 Processando: {arquivo}")

            # ✅ valida, mas NÃO bloqueia
            if not validar_nome(arquivo):
                logging.warning(f"Nome fora do padrão: {arquivo}")

            try:
                texto = extrair_texto_pdf(caminho)

                if not texto.strip():
                    raise ValueError("PDF sem texto (scan)")

                numero_guia = extrair_numero_guia(arquivo)
                total = extrair_valor_total(texto)
                localidade = extrair_localidade(texto)

                if total is None:
                    raise ValueError("Valor total não encontrado")

                resultados.append({
                    "Arquivo": arquivo,
                    "Número Guia": numero_guia,
                    "Localidade": localidade,
                    "Valor (R$)": total,
                    "Status": "OK"
                })

                logging.info(f"Sucesso: {arquivo}")

            except Exception as e:
                print(f"⚠️ Erro em {arquivo}: {e}")
                logging.error(f"Erro em {arquivo}: {e}")

                erros.append({
                    "Arquivo": arquivo,
                    "Erro": str(e)
                })

    logging.info("Fim do processamento")
    return resultados, erros


# ================= RELATÓRIO =================
def salvar_relatorio(resultados, erros):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

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

    print("\n✅ RELATÓRIO GERADO")
    print(f"📁 Arquivo: {caminho}")
    print(f"💰 TOTAL GERAL: R$ {total_geral:,.2f}")
    print(f"⚠️ Erros: {len(df_erros)}")

    logging.info(f"Total geral: {total_geral}")
    logging.info(f"Erros: {len(df_erros)}")


# ================= EXECUÇÃO =================
def main():
    print("\n🚀 PROCESSANDO GUIAS...\n")

    resultados, erros = processar_guias()
    salvar_relatorio(resultados, erros)


if __name__ == "__main__":
    main()