import requests
import json

from api_key import OPENAI_API_KEY,GEMINI_API_KEY

# ========= CONFIGURAÇÕES =========

# Configuração da API Gemini
gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
gemini_headers = {
    "Content-Type": "application/json",
}

# Configuração da API OpenAI
openai_url = "https://api.openai.com/v1/chat/completions"
openai_headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

openai_model = "gpt-3.5-turbo"

# ========= FUNÇÕES =========

def consultar_gemini():

    prompt = (
        "PRECISO QUE Você SEJA um crawler, e eu preciso que você pesquise na web, "
        "repositórios de códigos que contenham algum tipo de code smells, "
        "fornecendo um arquivo com o código fonte do smell e o link do repositório. "
        "Códigos em Java. "
        "Me entregue no seguinte formato JSON:\n"
        "{\n"
        "   \"God Class\": {\n"
        "       \"codigo\": \"...\",\n"
        "       \"link\": \"https://...\"\n"
        "   },\n"
        "   \"Long Method\": {\n"
        "       \"codigo\": \"...\",\n"
        "       \"link\": \"https://...\"\n"
        "   }\n"
        "}\n"
        "Liste pelo menos 3 tipos de code smells diferentes."
    )

    params = {
        "key": GEMINI_API_KEY
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(gemini_url, headers=gemini_headers, params=params, json=body)

    if response.status_code == 200:
        print(f"AQUIIIII --- {response.json()}")
        resposta_gemini = response.json()
        try:
            # A resposta vem como um texto dentro de candidates[0]['content']['parts'][0]['text']
            resposta_texto = resposta_gemini["candidates"][0]["content"]["parts"][0]["text"]
            return resposta_texto
        except (KeyError, IndexError):
            print("Erro ao extrair resposta da Gemini.")
            return None
    else:
        print(f"Erro na requisição para Gemini: {response.status_code}")
        print(response.text)
        return None


def salvar_json(conteudo_json):
    with open("code_smells.json", "w", encoding="utf-8") as arquivo:
        json.dump(conteudo_json, arquivo, indent=4, ensure_ascii=False)
    print("Código salvo com sucesso no arquivo 'code_smells.json'!")


def ler_json():
    with open("code_smells.json", "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def consultar_openai(code_snippet):
    prompt = (
        "Analise o código a seguir e identifique se ele contém algum code smell. "
        "Explique qual é o smell identificado e por quê.\n\n"
        f"{code_snippet}"
    )

    body = {
        "model": openai_model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(openai_url, headers=openai_headers, json=body)

    if response.status_code == 200:
        resposta = response.json()
        resposta_texto = resposta["choices"][0]["message"]["content"]
        return resposta_texto
    else:
        print(f"Erro na requisição para OpenAI: {response.status_code}")
        print(response.text)
        return None


# ========= FLUXO PRINCIPAL =========

def main():
    print("Consultando Gemini para obter exemplos de code smells em Java...\n")
    resposta_gemini = consultar_gemini()

    if resposta_gemini is None:
        print("Não foi possível obter resposta da Gemini.")
        return

    try:
        conteudo_json = json.loads(resposta_gemini)
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON da resposta da Gemini.")
        print("Resposta bruta da Gemini:")
        print(resposta_gemini)
        return

    salvar_json(conteudo_json)

    print("\nConsultando OpenAI para análise dos códigos...\n")

    conteudo = ler_json()

    for tipo_smell, dados in conteudo.items():
        codigo_fonte = dados["codigo"]
        link_repositorio = dados["link"]

        print(f"Analisando '{tipo_smell}' do repositório: {link_repositorio}\n")
        resposta_openai = consultar_openai(codigo_fonte)

        if resposta_openai:
            print(f"Resposta da OpenAI para '{tipo_smell}':\n{resposta_openai}\n")
        print("-" * 80)


if __name__ == "__main__":
    main()
