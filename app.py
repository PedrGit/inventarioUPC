import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

st.set_page_config(page_title="Inventário Automático", layout="wide")
st.title("📦 Inventário Automático de Planilha Excel")

arquivo_excel = st.file_uploader("📂 Selecione a planilha Excel", type=["xlsx", "xls"])

if arquivo_excel:
    df = pd.read_excel(arquivo_excel)
    df.columns = df.columns.str.strip()

    colunas = [
        "ID", "Código", "Descrição", "Referência Uso", "OS Fabricante",
        "Status garantia", "Status peça garantia", "Recebimento UPC", "Modelo Principal",
    ]
    df = df[colunas].set_index("ID")

    if "inventario" not in st.session_state:
        st.session_state["inventario"] = pd.DataFrame(columns=colunas + ["Categoria"])

    def buscar_ids():
        ids_input = st.session_state["ids_input"]
        categoria = st.session_state["categoria"]

        ids_lista = [i.strip() for i in ids_input.replace(",", " ").split() if i.strip().isdigit()]
        encontrados = []

        for i in ids_lista:
            try:
                resultado = df.loc[[int(i)]].copy()
                resultado["Categoria"] = categoria
                encontrados.append(resultado)
            except KeyError:
                st.warning(f"❌ ID {i} não encontrado.")

        if encontrados:
            resultados = pd.concat(encontrados)
            st.session_state["inventario"] = pd.concat(
                [st.session_state["inventario"], resultados],
                ignore_index=True
            ).drop_duplicates(subset=["ID"], keep="last")
            st.success(f"✅ {len(resultados)} IDs adicionados ao inventário.")

        # só limpa o campo depois de processar todos
        st.session_state["ids_input"] = ""

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🔍 Pesquisa")
        st.text_area(
            "Digite os IDs (separados por vírgula ou espaço):",
            key="ids_input",
            on_change=buscar_ids
        )
        st.radio("Categoria:", ["IN HOME", "LABORATÓRIO"], key="categoria")

    with col2:
        st.subheader("📊 Inventário acumulado")

        if not st.session_state["inventario"].empty:
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

            if st.button("🗑️ Deletar Inventário Completo"):
                st.session_state["inventario"] = pd.DataFrame(columns=colunas + ["Categoria"])
                st.success("Inventário completo deletado.")

            inventario_excel = "inventario_completo.xlsx"
            with pd.ExcelWriter(inventario_excel) as writer:
                inventario_inhome.to_excel(writer, sheet_name="IN HOME", index=False)
                inventario_lab.to_excel(writer, sheet_name="LABORATÓRIO", index=False)

            with open(inventario_excel, "rb") as f:
                st.download_button("⬇️ Baixar Inventário Completo", f, file_name=inventario_excel)
