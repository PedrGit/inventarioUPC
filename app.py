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

# Interface Streamlit
st.set_page_config(page_title="Inventário Automático", layout="wide")
st.title("📦 Inventário Automático de Planilha Excel")

# Upload da planilha
arquivo_excel = st.file_uploader("📂 Selecione a planilha Excel", type=["xlsx", "xls"])

if arquivo_excel:
    df = pd.read_excel(arquivo_excel)
    df.columns = df.columns.str.strip()  # remove espaços extras

    # Colunas desejadas
    colunas = [
        "ID",
        "Código",
        "Descrição",
        "Modelo Principal",
        "Referência Uso",
        "OS Fabricante",
        "Status garantia",
        "Status peça garantia",
        "Recebimento UPC",
    ]
    df = df[colunas]

    # Inicializar inventário na sessão
    if "inventario" not in st.session_state:
        st.session_state["inventario"] = pd.DataFrame(columns=colunas + ["Categoria"])

    # Layout em duas colunas
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🔍 Pesquisa")
        id_usuario = st.text_input("Digite o ID (6 dígitos):", value="", max_chars=6)
        categoria = st.radio("Categoria:", ["IN HOME", "LABORATÓRIO"])

        # Pesquisa automática
        if id_usuario and len(id_usuario) == 6 and id_usuario.isdigit():
            id_usuario = int(id_usuario)
            resultado = df[df["ID"] == id_usuario]

            if not resultado.empty:
                st.success(f"✅ ID {id_usuario} encontrado!")
                st.write(resultado)

                # Adicionar categoria
                resultado["Categoria"] = categoria

                # Adicionar ao inventário acumulado
                st.session_state["inventario"] = pd.concat(
                    [st.session_state["inventario"], resultado]
                ).drop_duplicates(subset=["ID"])

                # Exportar Excel individual
                nome_excel = f"resultado_{id_usuario}.xlsx"
                resultado.to_excel(nome_excel, index=False)
                with open(nome_excel, "rb") as f:
                    st.download_button("⬇️ Baixar Excel", f, file_name=nome_excel)

                # Exportar PDF individual
                dados = resultado.iloc[0].to_dict()
                nome_pdf = gerar_pdf(dados, id_usuario)
                with open(nome_pdf, "rb") as f:
                    st.download_button("⬇️ Baixar PDF", f, file_name=nome_pdf)

            else:
                st.error("❌ ID não encontrado.")

    with col2:
        st.subheader("📊 Inventário acumulado")

        if not st.session_state["inventario"].empty:
            # Abas para categorias
            aba = st.tabs(["IN HOME", "LABORATÓRIO"])

            with aba[0]:
                st.write(st.session_state["inventario"][
                    st.session_state["inventario"]["Categoria"] == "IN HOME"
                ])

            with aba[1]:
                st.write(st.session_state["inventario"][
                    st.session_state["inventario"]["Categoria"] == "LABORATÓRIO"
                ])

            # Opção de deletar um item
            id_delete = st.text_input("🗑️ Digite o ID para deletar:", value="", max_chars=6)
            if id_delete and len(id_delete) == 6 and id_delete.isdigit():
                id_delete = int(id_delete)
                if id_delete in st.session_state["inventario"]["ID"].values:
                    st.session_state["inventario"] = st.session_state["inventario"][
                        st.session_state["inventario"]["ID"] != id_delete
                    ]
                    st.success(f"ID {id_delete} removido do inventário.")
                else:
                    st.warning("ID não encontrado no inventário.")

            # Botão para deletar todo o inventário
            if st.button("🗑️ Deletar Inventário Completo"):
                st.session_state["inventario"] = pd.DataFrame(columns=colunas + ["Categoria"])
                st.success("Inventário completo deletado.")

            # Botão para baixar inventário completo em Excel (separado por abas)
            inventario_excel = "inventario_completo.xlsx"
            inventario_inhome = st.session_state["inventario"][
                st.session_state["inventario"]["Categoria"] == "IN HOME"
            ]
            inventario_lab = st.session_state["inventario"][
                st.session_state["inventario"]["Categoria"] == "LABORATÓRIO"
            ]

            with pd.ExcelWriter(inventario_excel) as writer:
                inventario_inhome.to_excel(writer, sheet_name="IN HOME", index=False)
                inventario_lab.to_excel(writer, sheet_name="LABORATÓRIO", index=False)

            with open(inventario_excel, "rb") as f:
                st.download_button("⬇️ Baixar Inventário Completo", f, file_name=inventario_excel)
