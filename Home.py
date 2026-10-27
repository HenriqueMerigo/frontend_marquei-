import streamlit as st

from endpoints.dashboards.busca_produto_estoque_zero import busca_produto_estoque_zero

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
        st.metric(label="Dashboard 2", value="Teste", delta="Teste")
    with col_dashboard3:
        st.metric(label="Dashboard 3", value="Teste", delta="Teste")
    with col_dashboard4:
        st.metric(label="Dashboard 4", value="Teste", delta="Teste")