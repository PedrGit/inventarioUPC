import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Função para gerar PDF
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
st.title("Inventário Automático de Planilha Excel")

# Upload da planilha
arquivo_excel = st.file_uploader("Selecione a planilha Excel", type=["xlsx", "xls"])

if arquivo_excel:
    df = pd.read_excel(arquivo_excel)
    df.columns = df.columns.str.strip()  # remove espaços extras

    # Selecionar apenas as colunas desejadas
    colunas = [
        "ID",
        "Código",
        "Modelo Principal",
        "Descrição",
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

    # Campo de entrada do ID
    id_usuario = st.text_input("Digite o ID (6 dígitos):", value="", max_chars=6)

    # Seleção da categoria
    categoria = st.radio("Selecione a categoria:", ["IN HOME", "LABORATÓRIO"])

    # Pesquisa automática: sempre que o campo tiver 6 dígitos
    if id_usuario and len(id_usuario) == 6 and id_usuario.isdigit():
        id_usuario = int(id_usuario)
        resultado = df[df["ID"] == id_usuario]

        if not resultado.empty:
            st.write("### Resultado encontrado:")
            st.write(resultado)

            # Adicionar categoria ao resultado
            resultado["Categoria"] = categoria

            # Adicionar ao inventário acumulado
            st.session_state["inventario"] = pd.concat(
                [st.session_state["inventario"], resultado]
            ).drop_duplicates(subset=["ID"])

            # Exportar Excel individual
            nome_excel = f"resultado_{id_usuario}.xlsx"
            resultado.to_excel(nome_excel, index=False)
            with open(nome_excel, "rb") as f:
                st.download_button("Baixar Excel", f, file_name=nome_excel)

            # Exportar PDF individual
            dados = resultado.iloc[0].to_dict()
            nome_pdf = gerar_pdf(dados, id_usuario)
            with open(nome_pdf, "rb") as f:
                st.download_button("Baixar PDF", f, file_name=nome_pdf)

        else:
            st.error("ID não encontrado.")

    # Mostrar inventário acumulado
    if not st.session_state["inventario"].empty:
        st.write("## Inventário acumulado")
        st.write(st.session_state["inventario"])

        # Botão para deletar um item do inventário
        id_delete = st.text_input("Digite o ID para deletar do inventário:", value="", max_chars=6)
        if id_delete and len(id_delete) == 6 and id_delete.isdigit():
            id_delete = int(id_delete)
            if id_delete in st.session_state["inventario"]["ID"].values:
                st.session_state["inventario"] = st.session_state["inventario"][
                    st.session_state["inventario"]["ID"] != id_delete
                ]
                st.success(f"ID {id_delete} removido do inventário.")
            else:
                st.warning("ID não encontrado no inventário.")

        # Botão para baixar inventário completo em Excel
        inventario_excel = "inventario_completo.xlsx"
        st.session_state["inventario"].to_excel(inventario_excel, index=False)
        with open(inventario_excel, "rb") as f:
            st.download_button("Baixar Inventário Excel", f, file_name=inventario_excel)
