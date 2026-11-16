import time

import streamlit as st
from numpy.random import default_rng as rng
import pandas as pd

from header.page_config import page_config
from endpoints.dashboards.dashboard import busca_resumo_financeiro, busca_resumo_produtos

from endpoints.financeiro.insere_financeiro import insere_financeiro

def financeiro():
    page_config()

    st.title("Financeiro")
    st.caption("Esta é a página de financeiro.")

@st.dialog("Inserir venda", width='large')
def modal_inserir_venda():
    st.write("Preencha os dados da nova venda:")

    col_confirma_agendamento, col_agendamento = st.columns([1,7])
    with col_confirma_agendamento:
        st.space('small')
        val_movimenta = st.checkbox("Tem agendamento?", value=True, width="stretch")
    with col_agendamento:
        id_agendamento = st.number_input("ID do agendamento:", min_value=0, disabled=not val_movimenta)

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
            time.sleep(2)
            st.toast("Venda inserida com sucesso!", icon="✅")
            time.sleep(1)
            st.rerun()


if __name__ == "__main__":
    financeiro()

    col_venda = st.columns(1)

    with col_venda[0]:
        if st.button("Lancar Venda", width='stretch'):
            modal_inserir_venda()

    col_grafico_financeiro, col_grafico_produtos = st.columns(2)

    with col_grafico_financeiro:
        st.write("Gráfico de resumo financeiro")
        dados = busca_resumo_financeiro()
        df_servicos = pd.DataFrame.from_dict(
            dados.get("servicos", {}), orient="index", columns=["Agendamentos"]
        )
        df_compras = pd.DataFrame.from_dict(
            dados.get("compras", {}), orient="index", columns=["Compras"]
        )

        df_final = pd.concat([df_servicos, df_compras], axis=1).fillna(0)

        df_final.index = pd.to_datetime(df_final.index)
        df_final = df_final.sort_index()

        st.line_chart(df_final)

    with col_grafico_produtos:
            st.write("Gráfico de produtos/servicos mais vendidos")
            dados_produtos = busca_resumo_produtos()
            
            df_produtos = pd.DataFrame(
                {
                    "Produto": dados_produtos.get("ds_produto_servico", []),
                    "Vendas": dados_produtos.get("qtd_vendido", []),
                }
            )
            
            if not df_produtos.empty:
                df_produtos = df_produtos.set_index("Produto")
                st.bar_chart(df_produtos["Vendas"])
            else:
                st.info("Nenhum dado de produto encontrado.")