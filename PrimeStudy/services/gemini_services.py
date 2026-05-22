from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPTS = {
    'resumo': """
Gere um resumo fiel ao texto abaixo.
- Não invente informações
- Use tópicos claros
- Destaque os conceitos principais
""",

    'flashcard': """
Gere flashcards de estudo no formato:
P: [pergunta]
R: [resposta]

Crie entre 5 e 10 flashcards com os conceitos mais importantes.
""",

    'questoes': """
Gere 5 questões de múltipla escolha sobre o texto.

Formato:
1. [pergunta]
a) ...
b) ...
c) ...
d) ...

Resposta correta: [letra]
""",

    'mapa': """
Gere um mapa mental em formato hierárquico.

Exemplo:
Tema Principal
  Subtema
    Detalhe
""",

    'checklist': """
Gere um checklist de estudo.

Formato:
[ ] Tópico
""",

    'topicos': """
Liste os principais tópicos do texto usando bullet points.
"""
}

def gerar_conteudo(tipo, texto):

    prompt = PROMPTS.get(tipo)
    if not prompt:
        return "Tipo inválido."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""{prompt}Texto:{texto[:2000]}""",
            config={
                "max_output_tokens": 300,
                "temperature": 0.5
            }
        )
        return response.text
    except Exception as e:
        print("Erro Gemini:", e)
        return "Erro ao gerar conteúdo."
