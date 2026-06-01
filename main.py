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


# ================= VALOR TOTAL (ROBUSTO ✅) =================
def extrair_valor_total(texto):
    valores = re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}', texto)

    if not valores:
        return None

    try:
        valores_convertidos = [
            float(v.replace('.', '').replace(',', '.'))
            for v in valores
        ]

        # pega o maior valor → geralmente é o total
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
            print(f"\n📄 Processando: {arquivo}")

            if not validar_nome(arquivo):
                logging.warning(f"Nome fora do padrão: {arquivo}")

            try:
                texto = extrair_texto_pdf(caminho)

                if not texto.strip():
                    logging.warning(f"PDF sem texto (scan?): {arquivo}")

                numero_guia = extrair_numero_guia(arquivo)
                total = extrair_valor_total(texto)
                localidade = extrair_localidade(texto)

                if total is None:
                    logging.warning(f"Valor não encontrado: {arquivo}")
                    total = 0

                print(f"→ Número: {numero_guia}")
                print(f"→ Localidade: {localidade}")
                print(f"→ Valor: {total}")

                resultados.append({
                    "Arquivo": arquivo,
                    "Número Guia": numero_guia,
                    "Localidade": localidade,
                    "Valor (R$)": total,
                    "Status": "OK" if total > 0 else "Verificar"
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