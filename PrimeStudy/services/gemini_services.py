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
- Apenas o necessario
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
Gere um mapa mental em formato de texto indentado com 2 espaços por nível.

Regras OBRIGATÓRIAS:
- Primeira linha: o tema principal (sem indentação)
- Subtemas: indentados com 2 espaços
- Detalhes: indentados com 4 espaços
- Mantenha acentos e português correto
- Não adicione marcadores, hífens, asteriscos ou numeração
- Não adicione nenhum texto fora da estrutura
- Máximo de 6 subtemas e 3 detalhes por subtema

Exemplo:
Tema Principal
  Subtema 1
    Detalhe 1
    Detalhe 2
  Subtema 2
    Detalhe 3
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
            contents=f"""{prompt}Texto:{texto[:20000]}""",
            config={
                "max_output_tokens": 100000,
                "temperature": 0.5
            }
        )
        return response.text
    except Exception as e:
        print("Erro Gemini:", e)
        return "Erro ao gerar conteúdo."
