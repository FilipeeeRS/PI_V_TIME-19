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
Para cada questão, indique a resposta correta.
Formato:
1. [pergunta]
a) ...  b) ...  c) ...  d) ...
Resposta: [letra]
""",
    'mapa': """
Gere um mapa mental em formato de texto estruturado com hierarquia.
Use indentação para mostrar os níveis.
Exemplo:
Tema Central
  Subtema 1
    Detalhe A
    Detalhe B
  Subtema 2
""",
    'checklist': """
Gere um checklist de estudo com os tópicos principais do texto.
Formato:
[ ] Tópico 1
[ ] Tópico 2
""",
    'topicos': """
Liste os principais tópicos e conceitos do texto.
Use bullet points e seja objetivo.
""",
}

def gerar_conteudo(tipo, texto):
    prompt = PROMPTS.get(tipo)
    if not prompt:
        return "Tipo inválido."

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{prompt}\n\nTexto:\n{texto[:10000]}"
        )
        return response.text
    except Exception as e:
        print("Erro Gemini:", e)
        return "Erro ao gerar conteúdo."