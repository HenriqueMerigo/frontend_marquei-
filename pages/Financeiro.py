import time

import streamlit as st

from header.page_config import page_config, hide_sidebar
from header.navigation import navigation

from endpoints.financeiro.insere_financeiro import insere_financeiro

def financeiro():
    page_config()

    st.title("Financeiro")
    st.caption("Esta é a página de financeiro.")

@st.dialog("Inserir venda", width='large')
def modal_inserir_venda():
    st.write("Preencha os dados da nova venda:")

    val_movimenta = st.checkbox("Tem agendamento?", value=True)
    col_nome, col_preco = st.columns(2)
    with col_nome:
        id_agendamento = st.number_input("ID do agendamento:", min_value=0, disabled=not val_movimenta)
    with col_preco:
        vl_valor = st.number_input("Valor:", min_value=0.0, step=0.01, format="%.2f")

    if st.button("Salvar"):
        if id_agendamento is None or id_agendamento == 0:
            id_agendamento = 0
        elif not isinstance(id_agendamento, int):
            st.error("O ID do agendamento deve ser um número inteiro.")
            return

        response = insere_financeiro(id_agendamento, vl_valor)
        if response.status_code != 201:
            st.error(f"Erro ao inserir venda: {response.text}")
        else:
            st.success(f"Venda inserida com sucesso!")
            time.sleep(2)
            st.rerun()


    
if __name__ == "__main__":
    financeiro()

    col_venda = st.columns(1)

    with col_venda[0]:
        if st.button("Lancar Venda", width='stretch'):
            modal_inserir_venda()