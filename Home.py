import streamlit as st

from endpoints.dashboards.dashboard import dashboard

from header.page_config import page_config, hide_sidebar
from header.navigation import navigation

def main():
    page_config()
    hide_sidebar()
    navigation()

    st.title("Dashboard")
    st.write("Welcome to the dashboard! Here you can monitor various metrics in real-time.")

if __name__ == "__main__":
    main()

    dados_dashboard = dashboard()
    produto_sem_estoque = dados_dashboard.get('produtos_estoque_zero', 0)
    arrecadacao_liquida = dados_dashboard.get('arrecadacao_liquida', 0)
    percentual_aumento_mes_anterior = dados_dashboard.get('percentual_aumento_mes_anterior', 0)
    ticket_medio = dados_dashboard.get('ticket_medio', 0)
    agendamentos_hoje = dados_dashboard.get('agendamentos_hoje', 0)

    col_dash_produto_sem_estoque, col_dash_arrecadacao_liquida, col_dash_ticket_medio, col_dash_agendamentos_hoje = st.columns([1, 1, 1, 1], border=True)

    with col_dash_produto_sem_estoque:
        if produto_sem_estoque == 0:
            msg_produto_sem_estoque = "✅​"
            color_produto_sem_estoque = "green"
        elif produto_sem_estoque > 0:
            msg_produto_sem_estoque = "Valide os Produtos"
            color_produto_sem_estoque = "red"
        elif produto_sem_estoque == []:
            msg_produto_sem_estoque = "❓​🤔​"
            color_produto_sem_estoque = "gray"

        st.metric(label="Produtos sem Estoque", value=produto_sem_estoque, delta=f"{msg_produto_sem_estoque}", delta_arrow="off", delta_color=f"{color_produto_sem_estoque}")

    with col_dash_arrecadacao_liquida:
        if arrecadacao_liquida > 0:
            color_arrecadacao_liquida = "green"
        elif arrecadacao_liquida <= 0:
            color_arrecadacao_liquida = "red"
        else:
            color_arrecadacao_liquida = "gray"

        st.metric(label="Arrecadação Líquida (Mes)", value=f"R$ {arrecadacao_liquida:,.2f}", delta=f"{percentual_aumento_mes_anterior:.2f}% comparado ao mes anterior", delta_arrow="auto", delta_color=f"{color_arrecadacao_liquida}")

    with col_dash_ticket_medio:
        if ticket_medio > 0:
            msg_ticket_medio = "✅​"
            color_ticket_medio = "green"
        elif ticket_medio < 0:
            msg_ticket_medio = "⚠️​"
            color_ticket_medio = "red"
        else:
            msg_ticket_medio = "❓​🤔​"
            color_ticket_medio = "gray"

        st.metric(label="Ticket Médio (Mes)", value=f"R$ {ticket_medio:,.2f}", delta=f"{msg_ticket_medio}", delta_arrow="off", delta_color=f"{color_ticket_medio}")

    with col_dash_agendamentos_hoje:
        if agendamentos_hoje > 0:
            msg_agendamentos_hoje = "✅​"
            color_agendamentos_hoje = "green"
        elif agendamentos_hoje == 0:
            msg_agendamentos_hoje = "⚠️"
            color_agendamentos_hoje = "red"
        else:
            msg_agendamentos_hoje = "❓​🤔​"
            color_agendamentos_hoje = "gray"

        st.metric(label="Agenda de Hoje", value=agendamentos_hoje, delta=f"{msg_agendamentos_hoje}", delta_arrow="off", delta_color=f"{color_agendamentos_hoje}")