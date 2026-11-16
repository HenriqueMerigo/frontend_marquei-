import calendar
from datetime import date, datetime
import time
import requests
import streamlit as st
import pandas as pd

from endpoints.agendamento.finaliza_status_agendamento import finaliza_status_agendamento
from endpoints.agendamento.busca_agendamento import (
    busca_agendamento, 
    busca_agendamento_detalhes, 
    busca_agendamento_front, 
    busca_id_agendamento_insere_agendamento_produto_servico
)
from endpoints.agendamento.deleta_agendamento import deleta_agendamento
from endpoints.agendamento.insere_agendamento import (
    insere_agendamento, 
    insere_agendamento_produto_servico, 
    remove_estoque_agendamento
)
from endpoints.agendamento.edita_agendamento import edita_agendamento
from endpoints.produto_servico.busca_produto_servico import busca_produto, busca_servico
from endpoints.funcionario.busca_funcionario import busca_funcionario
from endpoints.cliente.busca_cliente import busca_cliente

from endpoints.financeiro.insere_financeiro import insere_financeiro

from header.page_config import page_config


st.session_state.setdefault("itens_selecionados", [])


def _parse_data_agendamento(valor):
    if not isinstance(valor, str):
        return None

    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return None

@st.dialog("Inserir Agendamento", width="large")
def modal_inserir_agendamento():
    st.write("Preencha os dados do novo agendamento:")

    dados_funcionario = busca_funcionario() or []
    dados_cliente = busca_cliente() or []

    # 1. Campos de Identificação
    col_1, col_2 = st.columns(2)
    with col_1:
        funcionario_obj = st.selectbox(
            "Funcionario:", 
            options=dados_funcionario,
            format_func=lambda x: x.get('ds_funcionario', '') if isinstance(x, dict) else str(x)
        )
        dia_agendamento = st.date_input("Data do Agendamento:")
    with col_2:
        cliente_obj = st.selectbox(
            "Cliente:", 
            options=dados_cliente,
            format_func=lambda x: x.get('ds_cliente', '') if isinstance(x, dict) else str(x)
        )
        horario_agendamento = st.time_input("Horário Início:")

    st.divider()

    # 2. Seleção de Categoria e Itens
    col_opcao, col_item = st.columns(2)

    with col_opcao:
        option = st.selectbox("Categoria", ("Servico", "Produto"), key="select_cat_inserir")

    if option == "Produto":
        dados_produto_servico = busca_produto() or []
        label_select = "Selecione o Produto"
    else:
        dados_produto_servico = busca_servico() or []
        label_select = "Selecione o Servico"

    lista_opcoes = [
        item
        for item in dados_produto_servico
        if isinstance(item, dict) and item.get("ds_produto_servico")
    ]

    with col_item:
        produto_servico = st.selectbox(
            label_select,
            options=lista_opcoes,
            format_func=lambda item: item.get("ds_produto_servico", ""),
            key="select_item_inserir"
        )

    if st.button("Inserir Produto / Servico", key="btn_insere_prod_serv_inserir"):
        if produto_servico:
            id_produto_servico = produto_servico.get("id_produto_servico")
            try:
                preco = float(
                    produto_servico.get("vl_unitario_produto_venda") or 0
                )
            except (TypeError, ValueError):
                st.error("O preço do produto/serviço selecionado é inválido.")
            else:
                if id_produto_servico is None:
                    st.error("Não foi possível identificar o produto/serviço selecionado.")
                else:
                    st.session_state.itens_selecionados.append({
                        "ID do Produto/Serviço": id_produto_servico,
                        "Descrição": produto_servico["ds_produto_servico"],
                        "Quantidade do Produto/Serviço": 1,
                        "Preço Unitário": preco
                    })

    st.write("### Itens Adicionados")
    colunas_itens = [
        "ID do Produto/Serviço",
        "Descrição",
        "Quantidade do Produto/Serviço",
        "Preço Unitário"
    ]
    df_exibicao = pd.DataFrame(
        st.session_state.itens_selecionados,
        columns=colunas_itens
    )
    st.dataframe(df_exibicao, width='stretch')

    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        vl_desconto_agendamento = st.number_input("Valor de Desconto Previo:", min_value=0.0, key="desc_inserir")

    with col_2:
        vl_gorjeta_agendamento = st.number_input("Valor de Gorjeta Previa:", min_value=0.0, key="gorjeta_inserir")

    vl_total_bruto_agendamento = sum(item["Preço Unitário"] for item in st.session_state.itens_selecionados)
    vl_total_liquido_agendamento = vl_total_bruto_agendamento - vl_desconto_agendamento + vl_gorjeta_agendamento
    with col_3:
        st.metric("Valor Total", f"R$ {vl_total_liquido_agendamento:,.2f}")

    col_limpar, col_status = st.columns(2)
    with col_limpar:
        st.write("")
        if st.button("Limpar Lista de Produtos/Servicos", key="btn_limpar_inserir"):
            st.session_state.itens_selecionados = []
    with col_status:
        ds_status = st.selectbox("Status do Agendamento", options=["AGENDADO", "CANCELADO", "CONCLUIDO"], index=0, key="status_inserir")

    st.divider()

    dh_agendamento = f"{dia_agendamento} {horario_agendamento}"

    id_funcionario = funcionario_obj.get('id_funcionario') if isinstance(funcionario_obj, dict) else None
    id_cliente = cliente_obj.get('id_cliente') if isinstance(cliente_obj, dict) else None

    if st.button("Inserir agendamento", type="primary", key="btn_submit_inserir"):
        if id_cliente is None or id_funcionario is None:
            st.error("Selecione um Cliente e um Funcionário válidos!")
        elif not st.session_state.itens_selecionados:
            st.error("Adicione pelo menos um produto ou serviço ao agendamento!")
        else:
            st.warning("Aguarde enquanto o agendamento é inserido...")

            response = insere_agendamento(
                id_cliente,
                id_funcionario,
                ds_status,
                vl_total_bruto_agendamento,
                vl_desconto_agendamento,
                vl_gorjeta_agendamento,
                vl_total_liquido_agendamento,
                dh_agendamento
            )
            if response.status_code != 201:
                st.error(f"Erro ao inserir agendamento: {response.text}")
                return

            agendamento = busca_id_agendamento_insere_agendamento_produto_servico()
            id_agendamento = (
                agendamento.get("id_agendamento")
                if isinstance(agendamento, dict)
                else None
            )
            if id_agendamento is None:
                st.error("Agendamento criado, mas não foi possível recuperar seu ID.")
                return

            if ds_status == "CONCLUIDO":
                response_financeiro = insere_financeiro(
                    id_agendamento, vl_total_liquido_agendamento, 'Agendamento'
                )
                if response_financeiro.status_code != 201:
                    st.error(f"Erro ao inserir lançamento financeiro: {response_financeiro.text}")
                    return

            sucesso_itens = True
            for item in st.session_state.itens_selecionados:
                id_prod_serv = item.get("ID do Produto/Serviço")
                if id_prod_serv is None:
                    st.error(f"Erro: O ID do item '{item.get('Descrição')}' está nulo!")
                    sucesso_itens = False
                    continue

                quantidade = int(item.get("qt_produto", 1))
                vl_unitario = float(item.get("Preço Unitário", 0.0))
                id_prod_serv = int(id_prod_serv)
                resp_item = insere_agendamento_produto_servico(
                    id_produto_servico=id_prod_serv,
                    qt_produto=quantidade,
                    vl_unitario_produto=vl_unitario,
                    vl_total_produto=vl_unitario * quantidade
                )

                if resp_item.status_code != 201:
                    sucesso_itens = False
                    st.error(f"Erro ao vincular item '{item.get('Descrição')}': {resp_item.text}")
                    continue

                resp_estoque = remove_estoque_agendamento(
                    vl_subtracao=quantidade,
                    id_produto_servico=id_prod_serv
                )
                if resp_estoque.status_code == 400:
                    sucesso_itens = False
                    st.error(f"Item nao possui estoque suficiente para '{item.get('Descrição')}'")
                elif resp_estoque.status_code != 200:
                    sucesso_itens = False
                    st.error(f"Erro ao atualizar estoque do item '{item.get('Descrição')}': {resp_estoque.text}")

            if sucesso_itens:
                st.session_state.itens_selecionados = []
                time.sleep(2)
                st.toast("Agendamento e itens inseridos com sucesso!", icon="✅")
                time.sleep(1)
                st.rerun()


@st.dialog("Editar Agendamento", width="large")
def modal_editar_agendamento():
    st.write("Selecione o agendamento que deseja alterar:")

    agendamento_busca = busca_agendamento() or []
    lista_agendamentos = [item for item in agendamento_busca if isinstance(item, dict)]

    if not lista_agendamentos:
        st.info("Nenhum agendamento encontrado para edição.")
        return

    agendamento_selecionado = st.selectbox(
        "Selecione o Agendamento:",
        options=lista_agendamentos,
        format_func=lambda c: f"ID: {c.get('id_agendamento')} | Cliente: {c.get('ds_cliente')} | Data: {c.get('dh_agendamento')} | Status: {c.get('ds_status')}"
    )

    if not agendamento_selecionado:
        return

    id_agendamento_atual = agendamento_selecionado.get("id_agendamento")

    dados_funcionario = busca_funcionario() or []
    dados_cliente = busca_cliente() or []

    func_atual_idx = 0
    for idx, f in enumerate(dados_funcionario):
        if isinstance(f, dict) and f.get('id_funcionario') == agendamento_selecionado.get('id_funcionario'):
            func_atual_idx = idx
            break

    cliente_atual_idx = 0
    for idx, c in enumerate(dados_cliente):
        if isinstance(c, dict) and c.get('id_cliente') == agendamento_selecionado.get('id_cliente'):
            cliente_atual_idx = idx
            break

    dh_str = agendamento_selecionado.get("dh_agendamento", "")
    parsed_dt = _parse_data_agendamento(dh_str)
    default_date = parsed_dt.date() if parsed_dt else date.today()
    default_time = parsed_dt.time() if parsed_dt else datetime.now().time()

    # 1. Campos de Identificação pré-preenchidos
    col_1, col_2 = st.columns(2)
    with col_1:
        funcionario_obj = st.selectbox(
            "Funcionario:", 
            options=dados_funcionario,
            index=func_atual_idx,
            format_func=lambda x: x.get('ds_funcionario', '') if isinstance(x, dict) else str(x),
            key="edit_func"
        )
        dia_agendamento = st.date_input("Data do Agendamento:", value=default_date, key="edit_data")
    with col_2:
        cliente_obj = st.selectbox(
            "Cliente:", 
            options=dados_cliente,
            index=cliente_atual_idx,
            format_func=lambda x: x.get('ds_cliente', '') if isinstance(x, dict) else str(x),
            key="edit_cliente"
        )
        horario_agendamento = st.time_input("Horário Início:", value=default_time, key="edit_hora")

    st.divider()

    edit_state_key = f"itens_edit_{id_agendamento_atual}"
    if edit_state_key not in st.session_state:
        detalhes_atuais = busca_agendamento_detalhes(id_agendamento_atual) or []
        itens_iniciais = []
        for det in detalhes_atuais:
            if isinstance(det, dict):
                itens_iniciais.append({
                    "ID do Produto/Serviço": det.get("id_produto_servico"),
                    "Descrição": det.get("ds_produto_servico", "N/A"),
                    "Quantidade do Produto/Serviço": det.get("qt_produto", 1),
                    "Preço Unitário": float(det.get("vl_unitario_produto", 0))
                })
        st.session_state[edit_state_key] = itens_iniciais

    # 2. Seleção de Categoria e Itens
    col_opcao, col_item = st.columns(2)

    with col_opcao:
        option = st.selectbox("Categoria", ("Servico", "Produto"), key="edit_cat")

    if option == "Produto":
        dados_produto_servico = busca_produto() or []
        label_select = "Selecione o Produto"
    else:
        dados_produto_servico = busca_servico() or []
        label_select = "Selecione o Servico"

    lista_opcoes = [
        item
        for item in dados_produto_servico
        if isinstance(item, dict) and item.get("ds_produto_servico")
    ]

    with col_item:
        produto_servico = st.selectbox(
            label_select,
            options=lista_opcoes,
            format_func=lambda item: item.get("ds_produto_servico", ""),
            key="edit_item_select"
        )

    if st.button("Inserir Produto / Servico", key="btn_inserir_item_edit"):
        if produto_servico:
            id_produto_servico = produto_servico.get("id_produto_servico")
            try:
                preco = float(produto_servico.get("vl_unitario_produto_venda") or 0)
            except (TypeError, ValueError):
                st.error("O preço do produto/serviço selecionado é inválido.")
            else:
                if id_produto_servico is None:
                    st.error("Não foi possível identificar o produto/serviço selecionado.")
                else:
                    st.session_state[edit_state_key].append({
                        "ID do Produto/Serviço": id_produto_servico,
                        "Descrição": produto_servico["ds_produto_servico"],
                        "Quantidade do Produto/Serviço": 1,
                        "Preço Unitário": preco
                    })

    st.write("### Itens do Agendamento")
    colunas_itens = [
        "ID do Produto/Serviço",
        "Descrição",
        "Quantidade do Produto/Serviço",
        "Preço Unitário"
    ]
    df_exibicao = pd.DataFrame(
        st.session_state[edit_state_key],
        columns=colunas_itens
    )
    st.dataframe(df_exibicao, width='stretch')

    col_1, col_2, col_3 = st.columns(3)

    desconto_banco = float(agendamento_selecionado.get("vl_desconto_agendamento") or 0)
    gorjeta_banco = float(agendamento_selecionado.get("vl_gorjeta_agendamento") or 0)

    with col_1:
        vl_desconto_agendamento = st.number_input("Valor de Desconto Previo:", value=desconto_banco, min_value=0.0, key="edit_desc")

    with col_2:
        vl_gorjeta_agendamento = st.number_input("Valor de Gorjeta Previa:", value=gorjeta_banco, min_value=0.0, key="edit_gorjeta")

    vl_total_bruto_agendamento = sum(item["Preço Unitário"] * item.get("Quantidade do Produto/Serviço", 1) for item in st.session_state[edit_state_key])
    vl_total_liquido_agendamento = vl_total_bruto_agendamento - vl_desconto_agendamento + vl_gorjeta_agendamento
    with col_3:
        st.metric("Valor Total", f"R$ {vl_total_liquido_agendamento:,.2f}")

    col_limpar, col_status = st.columns(2)
    with col_limpar:
        st.write("")
        if st.button("Limpar Lista de Produtos/Servicos", key="btn_limpar_edit"):
            st.session_state[edit_state_key] = []
    with col_status:
        status_opcoes = ["AGENDADO", "CANCELADO", "CONCLUIDO"]
        status_atual = agendamento_selecionado.get("ds_status", "AGENDADO")
        status_index = status_opcoes.index(status_atual) if status_atual in status_opcoes else 0
        ds_status = st.selectbox("Status do Agendamento", options=status_opcoes, index=status_index, key="edit_status")

    st.divider()

    dh_agendamento = f"{dia_agendamento} {horario_agendamento}"
    id_funcionario = funcionario_obj.get('id_funcionario') if isinstance(funcionario_obj, dict) else None
    id_cliente = cliente_obj.get('id_cliente') if isinstance(cliente_obj, dict) else None

    if st.button("Salvar Alterações", type="primary", key="btn_submit_edit"):
        if id_cliente is None or id_funcionario is None:
            st.error("Selecione um Cliente e um Funcionário válidos!")
        elif not st.session_state[edit_state_key]:
            st.error("Adicione pelo menos um produto ou serviço ao agendamento!")
        else:
            st.warning("Aguarde enquanto o agendamento é atualizado...")

            # Mapeamento seguro com fallback para garantir que o ID do produto/serviço nunca vá nulo
            itens_payload = [
                {
                    "id_produto_servico": item.get("ID do Produto/Serviço") or item.get("id_produto_servico"),
                    "quantidade": item.get("Quantidade do Produto/Serviço") or item.get("qt_produto", 1),
                    "vl_unitario": item.get("Preço Unitário") or item.get("vl_unitario_produto", 0.0)
                }
                for item in st.session_state[edit_state_key]
            ]

            payload = {
                "id_cliente": id_cliente,
                "id_funcionario": id_funcionario,
                "ds_status": ds_status,
                "vl_total_bruto_agendamento": vl_total_bruto_agendamento,
                "vl_desconto_agendamento": vl_desconto_agendamento,
                "vl_gorjeta_agendamento": vl_gorjeta_agendamento,
                "vl_total_liquido_agendamento": vl_total_liquido_agendamento,
                "dh_agendamento": dh_agendamento,
                "itens": itens_payload
            }

            response = edita_agendamento(id_agendamento_atual, payload)

            if response.status_code == 200:
                del st.session_state[edit_state_key]
                time.sleep(1)
                st.toast("Agendamento atualizado com sucesso!", icon="✅")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Erro ao atualizar agendamento: {response.text}")


@st.dialog("Deletar Agendamento", width="large")
def modal_deletar_agendamento():
    agendamento_busca = busca_agendamento()

    if not agendamento_busca:
        st.info("Nenhum agendamento encontrado.")
        return

    lista_agendamentos = [
        item for item in agendamento_busca if isinstance(item, dict)
    ]

    if not lista_agendamentos:
        st.info("Nenhum agendamento válido encontrado.")
        return

    agendamento_selecionado = st.selectbox(
        "Selecione o agendamento para deletar",
        options=lista_agendamentos,
        format_func=lambda c: f"ID: {c.get('id_agendamento')} | Func: {c.get('id_funcionario')} | Cliente: {c.get('id_cliente')} | Data: {c.get('dh_agendamento')} | R$ {c.get('vl_total_liquido_agendamento')}",
    )

    if agendamento_selecionado:
        id_agendamento = int(agendamento_selecionado.get("id_agendamento"))
        confirmar = st.checkbox("Tenho certeza de que desejo excluir este agendamento")

        if st.button(
            "Deletar agendamento",
            type="primary",
            disabled=not confirmar,
        ):
            response = deleta_agendamento(id_agendamento)

            if response.status_code == 200:
                time.sleep(2)
                st.toast("Agendamento deletado com sucesso!", icon="✅")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Erro ao deletar agendamento: {response.text}")


@st.dialog("Agendamentos Pendentes", width="large")
def modal_agendamentos_pendentes():
    agendamento_busca = busca_agendamento() or []

    agendamento_pendentes = [
        item for item in agendamento_busca
        if isinstance(item, dict) and item.get("ds_status") == "AGENDADO"
    ]

    if not agendamento_pendentes:
        st.info("Nenhum agendamento pendente encontrado.")
        return

    col_desc, col_botao = st.columns([3, 1])
    for agendamento in agendamento_pendentes:
        id_agendamento = agendamento.get("id_agendamento")
        if id_agendamento is None:
            continue

        with col_desc:
            with st.container(border=True):
                st.write(
                    f"**Agendamento ID:** {id_agendamento} | "
                    f"**Funcionário:** {agendamento.get('ds_funcionario', 'N/A')} | "
                    f"**Cliente:** {agendamento.get('ds_cliente', 'N/A')} | "
                    f"**Data/Hora:** {agendamento.get('dh_agendamento', 'N/A')} | "
                    f"**Valor Total:** R$ {float(agendamento.get('vl_total_liquido_agendamento') or 0):.2f}"
                )
                st.write(f"**Status:** {agendamento.get('ds_status', 'N/A')}")

        with col_botao:
            if st.button("Finalizar", key=f"btn_finalizar_{id_agendamento}"):
                response = finaliza_status_agendamento(id_agendamento)
                if response is None:
                    st.error(f"Erro ao finalizar o agendamento {id_agendamento}.")
                else:
                    st.rerun()

            confirmar_exclusao = st.checkbox("Confirmo exclusão", key=f"checkbox_delete_{id_agendamento}")
            if st.button("Deletar", key=f"btn_deletar_{id_agendamento}", disabled=not confirmar_exclusao):
                response = deleta_agendamento(id_agendamento)
                if response.status_code == 200:
                    time.sleep(2)
                    st.toast("Agendamento deletado com sucesso!", icon="✅")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Erro ao deletar agendamento: {response.text}")
        st.divider()


@st.dialog("Finalizar Agendamento", width="large")
def modal_finalizar_agendamento():
    agendamento_busca = busca_agendamento() or []

    agendamento_pendentes = [
        item for item in agendamento_busca
        if isinstance(item, dict) and (item.get("ds_status") == "AGENDADO" or item.get("ds_status") == "CANCELADO")
    ]

    if not agendamento_pendentes:
        st.info("Nenhum agendamento disponível para finalizar.")
        return

    id_agendamento = st.selectbox(
        "Selecione o agendamento para finalizar", 
        agendamento_pendentes,
        format_func=lambda c: f"ID: {c.get('id_agendamento')} | Cliente: {c.get('id_cliente')} | Data: {c.get('dh_agendamento')} | Status: {c.get('ds_status')}"
    )

    if st.button("Finalizar agendamento", type="primary"):
        if id_agendamento:
            finaliza_status_agendamento(id_agendamento.get("id_agendamento"))
            insere_financeiro(id_agendamento.get("id_agendamento"), id_agendamento.get("vl_total_liquido_agendamento"), "Agendamento")
            st.success("Agendamento finalizado com sucesso!")
            time.sleep(1)
            st.rerun()


def interacoes():
    col_novo, col_editar, col_remover, col_pendente, col_finaliza = st.columns(5)

    with col_novo:
        if st.button("Agendar Novo", width='stretch'):
            st.session_state.itens_selecionados = []
            modal_inserir_agendamento()

    with col_editar:
        if st.button("Editar Agendamento", width='stretch'):
            modal_editar_agendamento()

    with col_remover:
        if st.button("Remover Agendamento", width='stretch'):
            modal_deletar_agendamento()

    with col_pendente:
        if st.button("Agendamentos Pendentes", width='stretch'):
            st.session_state["data_selecionada"] = None
            modal_agendamentos_pendentes()

    with col_finaliza:
        if st.button("Finalizar Agendamento", width='stretch'):
            st.session_state["data_selecionada"] = None
            modal_finalizar_agendamento()


def calendario():
    hoje = date.today()

    col_mes, col_ano = st.columns([2, 1])
    with col_mes:
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
        ]
        mes_nome = st.selectbox("Mês", meses, index=hoje.month - 1)
        mes_num = meses.index(mes_nome) + 1

    with col_ano:
        ano = st.number_input(
            "Ano", min_value=2024, max_value=2030, value=hoje.year
        )

    ano = int(ano)
    matriz_mes = calendar.Calendar(
        firstweekday=calendar.SUNDAY
    ).monthdayscalendar(ano, mes_num)

    st.markdown("---")

    agendamentos = busca_agendamento() or []
    dias_com_agendamento = {
        data_agendamento.day
        for item in agendamentos
        if isinstance(item, dict)
        for data_agendamento in [_parse_data_agendamento(item.get("dh_agendamento"))]
        if data_agendamento is not None
        and data_agendamento.year == ano
        and data_agendamento.month == mes_num
    }

    dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    cols_header = st.columns(7)
    for idx, col in enumerate(cols_header):
        col.markdown(f"<div style='text-align: center;'><b>{dias_semana[idx]}</b></div>", unsafe_allow_html=True)

    for semana in matriz_mes:
        cols = st.columns(7)
        for i in range(7):
            dia = semana[i]
            with cols[i]:
                if dia == 0:
                    st.write("")
                else:
                    data_atual_btn = date(ano, mes_num, dia)
                    tem_agendamento = dia in dias_com_agendamento
                    eh_hoje = data_atual_btn == hoje

                    if eh_hoje and tem_agendamento:
                        label_dia = f"🟢 📅 {dia}"
                    elif eh_hoje:
                        label_dia = f"🟢 {dia}"
                    elif tem_agendamento:
                        label_dia = f"📅 {dia}"
                    else:
                        label_dia = str(dia)

                    if st.button(
                        label=label_dia,
                        key=f"btn_data_{ano}_{mes_num}_{dia}",
                        width='stretch',
                    ):
                        st.session_state["data_selecionada"] = data_atual_btn
                        abrir_modal_data(data_atual_btn)


@st.dialog("Detalhes da Data", width="large")
def abrir_modal_data(data):
    data_formatada = data.strftime("%d/%m/%Y")
    data_api = data.strftime("%Y-%m-%d")

    st.write(f"Você selecionou o dia **{data_formatada}**.")

    resultado = busca_agendamento_front(data_api)

    if resultado is None:
        st.error("Erro ao buscar dados do servidor. Verifique a conexão com a API.")
        return

    if resultado:
        agora = datetime.now()
        agendamentos_ordenados = [
            (item, _parse_data_agendamento(item.get("dh_agendamento")))
            for item in resultado
            if isinstance(item, dict)
        ]
        agendamentos_ordenados.sort(
            key=lambda agendamento: (
                agendamento[1] is None,
                abs(agendamento[1] - agora)
                if agendamento[1] is not None
                else 0
            )
        )

        for item, data_hora in agendamentos_ordenados:
            agendamento_selecionado = item["id_agendamento"]
            hora_str = (
                data_hora.strftime("%H:%M")
                if data_hora is not None
                else str(item.get("dh_agendamento", ""))
            )
            if st.button(
                f"⏰ {hora_str} | Cliente: {item.get('ds_cliente', 'N/A')} | Prof: {item.get('ds_funcionario', 'N/A')} — R$ {float(item.get('vl_total_liquido_agendamento') or 0):.2f}",
                key=f"btn_{agendamento_selecionado}_{item.get('id', hora_str)}",
                width='stretch'
            ):
                dados = busca_agendamento_detalhes(agendamento_selecionado)

                if dados and isinstance(dados, list):
                    detalhes = dados[0]

                    id_agendamento = detalhes.get('id_agendamento', 'N/A')
                    ds_status = detalhes.get('ds_status', 'N/A')
                    ds_cliente = detalhes.get('ds_cliente', 'N/A')
                    vl_total_bruto_agendamento = sum(
                        float(det_item.get('vl_total_produto') or 0) for det_item in dados
                    )
                    vl_desconto_agendamento = float(
                        detalhes.get('vl_desconto_agendamento') or 0
                    )
                    vl_gorjeta_agendamento = float(
                        detalhes.get('vl_gorjeta_agendamento') or 0
                    )
                    vl_total_liquido_agendamento = vl_total_bruto_agendamento - vl_desconto_agendamento + vl_gorjeta_agendamento

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"**ID:** {id_agendamento}")
                    with col2:
                        st.write(f"**Status:** {ds_status}")
                    with col3:
                        st.write(f"**Funcionário:** {detalhes.get('ds_funcionario', 'N/A')}")
                    with col4:
                        st.write(f"**Cliente:** {ds_cliente}")

                    dados_df = [
                        {
                            'Produto': det_item.get('ds_produto_servico', 'N/A'),
                            'Quantidade': det_item.get('qt_produto', 0),
                            'Valor Unitário': det_item.get('vl_unitario_produto', 0),
                            'Valor Total': det_item.get('vl_total_produto', 0),
                        }
                        for det_item in dados
                    ]

                    df = pd.DataFrame(dados_df)
                    st.dataframe(df, width='stretch', hide_index=True)

                    col4, col5, col6 = st.columns(3)
                    with col4:
                        st.write(f"**Desconto:** R$ {vl_desconto_agendamento:.2f}")
                    with col5:
                        st.write(f"**Gorjeta:** R$ {vl_gorjeta_agendamento:.2f}")
                    with col6:
                        st.write(f"**Total:** R$ {vl_total_liquido_agendamento:.2f}")

                else:
                    st.error("Não foi possível carregar os detalhes deste agendamento.")

    elif resultado == []:
        st.warning("Nenhum agendamento marcado para esta data.")


def agendamento():
    page_config()
    st.title("Agendamento")
    st.caption("Selecione um dia no calendário para visualizar os horários.")

    interacoes()
    calendario()

if __name__ == "__main__":
    agendamento()