import streamlit as st

def navigation():
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 1])

    with col_nav1:
        if st.button("Agendamento", width='stretch'):
            st.switch_page("pages/agendamento.py")
        elif st.button("Funcionario", width='stretch'):
            st.switch_page("pages/funcionario.py")
                        

    with col_nav2:
        if st.button("Financeiro", width='stretch', disabled=True):
            st.switch_page("pages/financeiro.py")

    with col_nav3:
        if st.button("Cliente", width='stretch'):
            st.switch_page("pages/cliente.py")

    with col_nav4:
        if st.button("Produto/Servico", width='stretch'):
            st.switch_page("pages/Produto-Servico.py")