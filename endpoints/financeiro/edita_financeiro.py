import re as regex
import requests as re
from datetime import date, datetime

porta = 5000
base = f"http://127.0.0.1:{porta}"



def edita_financeiro(id_agendamento, vl_valor):
    url = f"{base}/edita_financeiro/{id_agendamento}"

    if id_agendamento is None or id_agendamento == 0:
        id_agendamento = 0
    payload = {
        "id_agendamento": id_agendamento,
        "vl_valor": vl_valor,
    }
    if not vl_valor:
        raise ValueError("O campo 'vl_valor' é obrigatório e deve ser preenchido corretamente.")

    response = re.put(url, json=payload)
    
    return response