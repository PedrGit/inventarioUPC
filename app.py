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
st.title("Consulta Automática de Planilha Excel")

# Upload da planilha
arquivo_excel = st.file_uploader("Selecione a planilha Excel", type=["xlsx", "xls"])

if arquivo_excel:
    df = pd.read_excel(arquivo_excel)
    df.columns = df.columns.str.strip()  # remove espaços extras

    # Selecionar apenas as colunas desejadas
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
    df = df[colunas]

    # Campo de entrada do ID
    id_usuario = st.text_input("Digite o ID (6 dígitos):", value="", max_chars=6)

    # Pesquisa automática: sempre que o campo tiver 6 dígitos
    if id_usuario and len(id_usuario) == 6 and id_usuario.isdigit():
        id_usuario = int(id_usuario)
        resultado = df[df["ID"] == id_usuario]

        if not resultado.empty:
            st.write("### Resultado encontrado:")
            st.write(resultado)

            # Exportar Excel
            nome_excel = f"resultado_{id_usuario}.xlsx"
            resultado.to_excel(nome_excel, index=False)
            with open(nome_excel, "rb") as f:
                st.download_button("Baixar Excel", f, file_name=nome_excel)

            # Exportar PDF
            dados = resultado.iloc[0].to_dict()
            nome_pdf = gerar_pdf(dados, id_usuario)
            with open(nome_pdf, "rb") as f:
                st.download_button("Baixar PDF", f, file_name=nome_pdf)

        else:
            st.error("ID não encontrado.")
