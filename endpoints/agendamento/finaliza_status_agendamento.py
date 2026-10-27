import requests as re

porta = 5000
base = f"http://127.0.0.1:{porta}"

def finaliza_status_agendamento(id_agendamento):
    url = f"{base}/finaliza_status_agendamento/{id_agendamento}"
    
    try:
        response = re.put(url)
        
        # 200 OK: Sucesso ao atualizar
        if response.status_code == 200:
            return response.json()
            
        # 404 Not Found: Agendamento não existe
        elif response.status_code == 404:
            print("[AVISO]: Agendamento não encontrado.")
            return None
            
        # Erro de Servidor (500, etc.)
        else:
            print(f"[ERRO HTTP {response.status_code}]: {response.text}")
            return None
            
    except re.exceptions.RequestException as e:
        print(f"[ERRO CONEXÃO]: {e}")
        return None