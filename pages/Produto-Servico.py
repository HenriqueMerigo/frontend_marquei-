import streamlit as st
import pandas as pd
import time


from endpoints.funcionario.deleta_funcionario import deleta_funcionario
from endpoints.produto_servico.lanca_baixa_produto import lanca_baixa_produto
from header.page_config import page_config

from endpoints.produto_servico.insere_produto_servico import insere_produto_servico
from endpoints.produto_servico.busca_produto_servico import busca_produto_servico, busca_produto, busca_servico
from endpoints.produto_servico.edita_produto_servico import edita_produto_servico
from endpoints.produto_servico.deleta_produto_servico import deleta_produto_servico
from endpoints.produto_servico.lanca_compra_produto import lanca_compra_produto

def produto():
    page_config()

    st.title("Produto/Servico")


@st.dialog("Inserir Produto Servico", width='large')
def modal_inserir_produto_servico():
    st.write("Preencha os dados do novo produto/servico:")

    ds_produto_servico = st.text_input("Descricao")
    col_descricao, col_estoque = st.columns(2)
    with col_descricao:
        ds_categoria = st.selectbox("Categoria", ("Produto", "Servico"))
        vl_unitario_produto_compra = st.number_input("Valor de compra:")
    with col_estoque:
        qt_estoque = st.number_input("Quantidade em Estoque", value=0, min_value=0)
        vl_unitario_produto_venda = st.number_input("Valor de venda:")

    if st.button("Salvar"):
        response = insere_produto_servico(ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda)
        if response.status_code != 201:
            st.error(f"Erro ao inserir produto: {response.text}")
        else:
            st.toast(f"O {ds_categoria} foi inserido com sucesso!", icon="✅")
            time.sleep(2)
            st.rerun()

@st.dialog("Editar Produto Servico", width='large')
def modal_editar_produto_servico():
    action = st.selectbox("Selecione o produto para editar", options=[f"{c['id_produto_servico']} - {c['ds_produto_servico']}" for c in busca_produto_servico()])

    if action:
        id_produto_servico = int(action.split(" - ")[0])
        produto_servico_data = next((c for c in busca_produto_servico() if c['id_produto_servico'] == id_produto_servico), None)

        if produto_servico_data:
            st.write(f"Editando produto/servico: {produto_servico_data['ds_produto_servico']}")

            ds_produto_servico = st.text_input("Descricao", value=produto_servico_data['ds_produto_servico'])
            col_nome, col_telefone = st.columns(2)
            with col_nome:
                ds_categoria = st.selectbox("Categoria", ("Produto", "Servico"))
                vl_unitario_produto_compra = st.number_input("Valor de compra do produto/servico", value=produto_servico_data['vl_unitario_produto_compra'])
            with col_telefone:
                qt_estoque = st.number_input("Quantidade em Estoque", value=int(produto_servico_data['qt_estoque']), min_value=0)
                vl_unitario_produto_venda = st.number_input("Valor de venda do produto/servico", value=produto_servico_data['vl_unitario_produto_venda'])

            if st.button("Salvar Alterações"):
                st.warning("Aguarde enquanto as alterações são salvas...")
                time.sleep(2)
                response = edita_produto_servico(id_produto_servico, ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda)
                if response.status_code != 200:
                    st.error(f"Erro ao editar cliente: {response.text}")
                else:
                    st.toast("Alterações salvas com sucesso!", icon="✅")
                    time.sleep(2)
                    st.rerun()

@st.dialog("Deletar Produto", width="large")
def modal_deletar_produto_servico():
    produto_servico_busca = busca_produto_servico()

    if not produto_servico_busca:
        st.info("Nenhum produto/servico encontrado.")
        return

    lista_produto_servico = [
        item for item in busca_produto_servico() if isinstance(item, dict)
    ]

    if not lista_produto_servico:
        st.info("Nenhum produto/servico válido encontrado.")
        return

    produto_servico_selecionado = st.selectbox(
        "Selecione o produto/servico para deletar",
        options=lista_produto_servico,
        format_func=lambda c: f"ID Produto/Servico {c.get('id_produto_servico')} - {c.get('ds_produto_servico')}",
    )

    if produto_servico_selecionado:
        id_produto_servico = int(produto_servico_selecionado.get("id_produto_servico"))
        confirmar = st.checkbox("Tenho certeza de que desejo excluir este produto/servico")

        if st.button(
            "Deletar produto/servico",
            type="primary",
            width='stretch',
            disabled=not confirmar,
        ):
            response = deleta_produto_servico(id_produto_servico)

            if response.status_code == 200:
                st.session_state["confirmar_delete"] = False
                st.success("Produto/Servico deletado com sucesso!")
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"Erro ao deletar produto/servico: {response.text}")

@st.dialog("Registrar Compra", width="large")
def modal_registrar_compra():
    produtos = busca_produto()
    
    if not produtos:
        st.info("Nenhum produto encontrado.")
        return

    col1, col2 = st.columns([1, 1])
    with col1:
        action = st.selectbox(
            "Selecione o produto para inserir na compra",
            options=[f"{c['id_produto_servico']} - {c['ds_produto_servico']}" for c in produtos]
        )
        valor_prod_atual = next((c['vl_unitario_produto_compra'] for c in produtos if f"{c['id_produto_servico']} - {c['ds_produto_servico']}" == action), None)
        valor_prod_atual = st.number_input("Valor unitario do produto (Valor pago na compra)", value=valor_prod_atual)
    with col2:
        vl_edicao = st.number_input("Quantidade comprada", step=1, min_value=1)
        if action:
            st.space("small")
            id_produto_servico = int(action.split(" - ")[0])
            st.session_state["confirmar_delete"] = False
            if st.button("Registrar Compra", width='stretch'):
                response = lanca_compra_produto(id_produto_servico, vl_edicao, valor_prod_atual)
                
                if response.status_code == 200:
                    st.toast("Compra registrada com sucesso!", icon="✅")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Erro ao registrar compra: {response.text}")

@st.dialog("Registrar Baixa", width="large")
def modal_registrar_baixa():
    produtos = busca_produto()
    
    if not produtos:
        st.info("Nenhum produto encontrado.")
        return

    col1, col2 = st.columns([1, 1])
    with col1:
        action = st.selectbox(
            "Selecione o produto para remover do estoque",
            options=[f"{c['id_produto_servico']} - {c['ds_produto_servico']}" for c in produtos]
        )
        
    with col2:
        vl_edicao = st.number_input("Quantidade a remover", step=1, min_value=1)
        if action:
            st.space("small")
            id_produto_servico = int(action.split(" - ")[0])
            st.session_state["confirmar_delete"] = False
            if st.button("Registrar Baixa", width='stretch'):
                response = lanca_baixa_produto(id_produto_servico, vl_edicao)
                
                if response.status_code == 200:
                    st.toast("Baixa registrada com sucesso!", icon="✅")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Erro ao registrar baixa: {response.text}")


def modulo_todos():
    col_modulo_1, col_modulo_2, col_modulo_3 = st.columns([1, 1, 1])
    with col_modulo_1:
        if st.button("Inserir Produto/Servico", width='stretch'):
            modal_inserir_produto_servico()

    with col_modulo_2:
        if st.button("Editar Produto/Servico", width='stretch'):
            modal_editar_produto_servico()

    with col_modulo_3:
        if st.button("Deletar Produto/Servico", width='stretch'):
            modal_deletar_produto_servico()

def modulo():
    col_modulo_1, col_modulo_2, col_modulo_3 = st.columns([1, 1, 1])
    with col_modulo_1:
        if st.button("Inserir Produto/Servico", width='stretch'):
            modal_inserir_produto_servico()

    with col_modulo_2:
        if st.button("Editar Produto/Servico", width='stretch'):
            modal_editar_produto_servico()

    with col_modulo_3:
        if st.button("Deletar Produto/Servico", width='stretch'):
            modal_deletar_produto_servico()

def busca_dados():
    df = pd.DataFrame(dados)

    colunas_ordem = [
        "id_produto_servico",
        "ds_produto_servico",
        "ds_categoria",
        "qt_estoque",
        "vl_unitario_produto_compra",
        "vl_unitario_produto_venda",
        "dh_ultima_movimentacao"
    ]
    df = df[colunas_ordem]

    df = df.rename(columns={
        "id_produto_servico": "Código",
        "ds_produto_servico": "Descricao do Produto/Servico",
        "ds_categoria": "Categoria",
        "qt_estoque": "Estoque",
        "vl_unitario_produto_compra": "Valor de Compra",
        "vl_unitario_produto_venda": "Valor de Venda",
        "dh_ultima_movimentacao": "Ultima Venda"
    })
    st.dataframe(df, hide_index=True, width="content")

if __name__ == "__main__":
    produto()
    option_map = { 
        0: "Todos",
        1: "Servicos",
        2: "Produtos"
    }
    selection = st.pills(
        "Selecione a secao que deseja acessar:",
        options=option_map.keys(),
        format_func=lambda option: option_map[option],
        selection_mode="single",
    )

    if selection == 0 or selection == None:
        modulo()

        dados = busca_produto_servico()
        if dados:
            busca_dados()

    elif selection == 1:
        modulo()

        dados = busca_servico()
        if dados:
            busca_dados()
    else:
        modulo()

        dados = busca_produto()
        if dados:
            busca_dados()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Registrar Compra", width='stretch'):
            modal_registrar_compra()
    with col2:
        if st.button("Registrar Baixa", width='stretch'):
            modal_registrar_baixa()