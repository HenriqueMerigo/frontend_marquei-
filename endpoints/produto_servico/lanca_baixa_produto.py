import re as regex
import requests as re

porta = 5000
base = f"http://127.0.0.1:{porta}"



def lanca_baixa_produto(id_produto_servico: int, vl_edicao: int):
    
    url = f"{base}/lanca_baixa_produto"

    payload = {
        "id_produto_servico": id_produto_servico,
        "vl_edicao": vl_edicao
    }
    if not vl_edicao or not id_produto_servico:
        raise ValueError("Os campos 'vl_edicao' e 'id_produto_servico' são obrigatórios e devem ser preenchidos corretamente.")

    response = re.put(url, json=payload)
    
    return response