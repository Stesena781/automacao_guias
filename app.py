import streamlit as st
import os
from main import processar_guias, salvar_relatorio

# ================= CONFIG DA PÁGINA =================
st.set_page_config(
    page_title="Leitor de Guias",
    layout="centered"
)

# ================= CSS CUSTOM (FONTE + POSIÇÃO) =================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* título no canto */
.titulo-canto {
    position: fixed;
    top: 20px;
    right: 30px;
    font-size: 18px;
    color: #666;
    z-index: 999;
}
</style>
""", unsafe_allow_html=True)

# ================= TITULO NO CANTO =================
st.markdown('<div class="titulo-canto">Leitor de Guias</div>', unsafe_allow_html=True)

# ================= LOGO CENTRAL =================
st.markdown("<br><br>", unsafe_allow_html=True)
st.image("assets/logo.png", width=220)

st.markdown("""
<h3 style='text-align: center; color: #444;'>
Sistema automático de leitura de guias
</h3>
""", unsafe_allow_html=True)

st.divider()

# ================= UPLOAD =================
st.subheader("📥 Upload de arquivos")

arquivos = st.file_uploader(
    "Selecione os arquivos PDF",
    type=["pdf"],
    accept_multiple_files=True
)

# ================= PROCESSAMENTO =================
if arquivos:

    st.success(f"✅ {len(arquivos)} arquivo(s) selecionado(s)")

    with st.expander("📂 Ver arquivos enviados"):
        for arq in arquivos:
            st.write(f"• {arq.name}")

    st.divider()

    if st.button("🚀 Processar", use_container_width=True):

        pasta = "guias_pdf"

        os.makedirs(pasta, exist_ok=True)

        for f in os.listdir(pasta):
            os.remove(os.path.join(pasta, f))

        for arquivo in arquivos:
            caminho = os.path.join(pasta, arquivo.name)
            with open(caminho, "wb") as f:
                f.write(arquivo.read())

        with st.spinner("Processando guias... ⏳"):
            resultados, erros = processar_guias()
            salvar_relatorio(resultados, erros)

        st.success("✅ Processamento concluído!")

        # ================= RESUMO =================
        st.subheader("📊 Resumo")

        col1, col2 = st.columns(2)

        col1.metric("Guias processadas", len(resultados))
        col2.metric("Erros", len(erros))

        st.divider()

        # ================= DOWNLOAD =================
        caminho_relatorio = "output/relatorio_guias.xlsx"

        with open(caminho_relatorio, "rb") as f:
            st.download_button(
                label="📥 Baixar relatório",
                data=f,
                file_name="relatorio_guias.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# ================= RODAPÉ =================
st.divider()
st.caption("Sistema interno • Automação de guias")