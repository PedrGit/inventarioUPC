import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Função para gerar PDF individual
def gerar_pdf(dados, id_usuario):
    nome_arquivo = f"resultado_{id_usuario}.pdf"
    c = canvas.Canvas(nome_arquivo, pagesize=letter)
    c.drawString(100, 750, f"Resultados para ID: {id_usuario}")
    y = 700
    for coluna, valor in dados.items():
        c.drawString(100, y, f"{coluna}: {valor}")
        y -= 20
    c.save()
    return nome_arquivo

# Configuração da página
st.set_page_config(page_title="Inventário Automático", layout="wide")
st.title("📦 Inventário Automático de Planilha Excel")

# Upload da planilha
arquivo_excel = st.file_uploader("📂 Selecione a planilha Excel", type=["xlsx", "xls"])

if arquivo_excel:
    df = pd.read_excel(arquivo_excel)
    df.columns = df.columns.str.strip()

    # Colunas desejadas
    colunas = [
        "ID",
        "Código",
        "Descrição",
        "Referência Uso",
        "OS Fabricante",
        "Status garantia",
        "Status peça garantia",
        "Recebimento UPC",
        "Modelo Principal",
    ]
    df = df[colunas].set_index("ID")  # índice otimizado para busca rápida

    # Inicializar inventário
    if "inventario" not in st.session_state:
        st.session_state["inventario"] = pd.DataFrame(columns=colunas + ["Categoria"])

    # Layout em duas colunas
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🔍 Pesquisa")
        id_usuario = st.text_input("Digite o ID (6 dígitos):", key="id_usuario", max_chars=6)
        categoria = st.radio("Categoria:", ["IN HOME", "LABORATÓRIO"], key="categoria")

        # Busca rápida e segura
        if len(id_usuario) == 6 and id_usuario.isdigit():
            try:
                resultado = df.loc[[int(id_usuario)]].copy()
                resultado["Categoria"] = categoria

                # Adiciona ao inventário acumulado
                st.session_state["inventario"] = pd.concat(
                    [st.session_state["inventario"], resultado],
                    ignore_index=True
                ).drop_duplicates(subset=["ID"], keep="last")

                st.success(f"✅ ID {id_usuario} adicionado ao inventário.")

                # Limpa o campo automaticamente após a busca
                st.session_state["id_usuario"] = ""

            except KeyError:
                st.error("❌ ID não encontrado.")

    with col2:
        st.subheader("📊 Inventário acumulado")

        if not st.session_state["inventario"].empty:
            # Abas para categorias
            aba = st.tabs(["IN HOME", "LABORATÓRIO"])

            with aba[0]:
                inventario_inhome = st.session_state["inventario"][
                    st.session_state["inventario"]["Categoria"] == "IN HOME"
                ]
                st.dataframe(inventario_inhome, use_container_width=True)

            with aba[1]:
                inventario_lab = st.session_state["inventario"][
                    st.session_state["inventario"]["Categoria"] == "LABORATÓRIO"
                ]
                st.dataframe(inventario_lab, use_container_width=True)

            # Deletar apenas um item
            id_delete = st.text_input("🗑️ Digite o ID para deletar:", key="delete_id", max_chars=6)
            if len(id_delete) == 6 and id_delete.isdigit():
                id_delete = int(id_delete)
                if id_delete in st.session_state["inventario"]["ID"].values:
                    st.session_state["inventario"] = st.session_state["inventario"][
                        st.session_state["inventario"]["ID"] != id_delete
                    ]
                    st.success(f"ID {id_delete} removido do inventário.")
                else:
                    st.warning("ID não encontrado no inventário.")

            # Deletar todo o inventário
            if st.button("🗑️ Deletar Inventário Completo"):
                st.session_state["inventario"] = pd.DataFrame(columns=colunas + ["Categoria"])
                st.success("Inventário completo deletado.")

            # Baixar inventário completo em Excel (separado por abas)
            inventario_excel = "inventario_completo.xlsx"
            with pd.ExcelWriter(inventario_excel) as writer:
                inventario_inhome.to_excel(writer, sheet_name="IN HOME", index=False)
                inventario_lab.to_excel(writer, sheet_name="LABORATÓRIO", index=False)

            with open(inventario_excel, "rb") as f:
                st.download_button("⬇️ Baixar Inventário Completo", f, file_name=inventario_excel)
