import streamlit as st

from endpoints.dashboards.busca_produto_estoque_zero import busca_produto_estoque_zero
from endpoints.dashboards.busca_arrecadacao_liquida import busca_arrecadacao_liquida
from endpoints.dashboards.busca_ticket_medio import busca_ticket_medio
from endpoints.dashboards.busca_agendamento_hoje import busca_agendamento_hoje

from header.page_config import page_config, hide_sidebar
from header.navigation import navigation

def main():
    page_config()
    hide_sidebar()
    navigation()


if __name__ == "__main__":
    main()
    st.title("Dashboard")
    st.write("Welcome to the dashboard! Here you can monitor various metrics in real-time.")


    col_dashboard1, col_dashboard2, col_dashboard3, col_dashboard4 = st.columns([1, 1, 1, 1], border=True)

    with col_dashboard1:
        dados_estoque_produto = busca_produto_estoque_zero()    
        qtd_cliente = dados_estoque_produto.get('contagem', 0)

        if qtd_cliente == []:
            msg = "❓​🤔​"
            color = "gray"
        elif qtd_cliente > 0:
            msg = "⚠️ ALERTA ⚠️​"
            color = "red"
        elif qtd_cliente == 0:
            msg = "✅​"
            color = "green"

        st.metric(label="Produtos sem Estoque", value=qtd_cliente, delta=f"{msg}", delta_arrow="off", delta_color=f"{color}")

    with col_dashboard2:
        dados_arrecadacao_liquida = busca_arrecadacao_liquida()
        vl_arrecadacao = dados_arrecadacao_liquida.get('contagem', 0)

        if vl_arrecadacao == []:
            msg = "❓​🤔​"
            color = "gray"
        elif vl_arrecadacao < 0:
            msg = "⚠️ ALERTA ⚠️​"
            color = "red"
        elif vl_arrecadacao == 0:
            msg = "✅​"
            color = "green"
        
        st.metric(label="Arrecadação Líquida", value=f"R$ {vl_arrecadacao:,.2f}", delta=f"{msg}", delta_arrow="off", delta_color=f"{color}")


    with col_dashboard3:
        dados_ticket_medio = busca_ticket_medio()
        vl_ticket_medio = dados_ticket_medio.get('media', 0)

        if vl_ticket_medio == []:
            msg = "❓​🤔​"
            color = "gray"
        elif vl_ticket_medio < 0:
            msg = "⚠️ ALERTA ⚠️​"
            color = "red"
        elif vl_ticket_medio == 0:
            msg = "✅​"
            color = "green"

        st.metric(label="Ticket Médio", value=f"R$ {vl_ticket_medio:,.2f}", delta=f"{msg}", delta_arrow="off", delta_color=f"{color}")

    with col_dashboard4:
        dados_agendamento_hoje = busca_agendamento_hoje()
        qtd_agendamento_hoje = dados_agendamento_hoje.get('contagem', 0)

        if qtd_agendamento_hoje == []:
            msg = "❓​🤔​"
            color = "gray"
        elif qtd_agendamento_hoje < 0:
            msg = "⚠️ ALERTA ⚠️​"
            color = "red"
        elif qtd_agendamento_hoje == 0:
            msg = "✅​"
            color = "green"

        st.metric(label="Agenda de Hoje", value=qtd_agendamento_hoje, delta=f"{msg}", delta_arrow="off", delta_color=f"{color}")