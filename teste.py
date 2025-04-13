import requests
from api_key import OPENAI_API_KEY,GEMINI_API_KEY



# Endpoint para listar os modelos
url = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_API_KEY}"

# Cabeçalhos da requisição
headers = {
    "Content-Type": "application/json"
}

# Requisição GET para listar os modelos
response = requests.get(url, headers=headers)

# Verificar a resposta
if response.status_code == 200:
    models = response.json()
    print("Modelos disponíveis:")
    for model in models.get("models", []):
        print(f"- {model['name']}")
else:
    print(f"Erro: {response.status_code}")
    print(response.text)
