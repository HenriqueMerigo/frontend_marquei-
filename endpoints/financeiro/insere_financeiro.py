import re as regex
import requests as re
from datetime import date, datetime

porta = 5000
base = f"http://127.0.0.1:{porta}"

def insere_financeiro(id_agendamento, vl_valor):
    url = f"{base}/insere_financeiro"

    payload = {
        "id_agendamento": id_agendamento,
        "vl_total": vl_valor
    }
    response = re.post(url, json=payload)
    return response