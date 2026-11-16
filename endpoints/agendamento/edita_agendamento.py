import requests

porta = 5000
base = f"http://127.0.0.1:{porta}"

def edita_agendamento(id_agendamento, dados_payload):
    url = f"{base}/edita_agendamento/{id_agendamento}" # Ajuste para a URL da sua API se necessário
    try:
        response = requests.put(url, json=dados_payload)
        return response
    except Exception as e:
        class FakeResponse:
            status_code = 500
            text = str(e)
        return FakeResponse()