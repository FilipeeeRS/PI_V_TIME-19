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

    # A JOGADA DE MESTRE: Uma lista de nomes genéricos e atuais. 
    # O código vai tentar um por um até o Google aceitar.
    modelos_tentativas = [
        "gemini-2.5-flash",
        "gemini-flash",
        "gemini-pro",
        "gemini-1.5-flash-latest"
    ]

    for modelo_atual in modelos_tentativas:
        try:
            print(f"🔄 Testando conexão com o modelo: {modelo_atual}...")
            response = client.models.generate_content(
                model=modelo_atual,
                contents=f"{prompt}\n\nTexto:\n{texto[:10000]}"
            )
            print(f"✅ Sucesso! O Google aceitou o modelo: {modelo_atual}")
            return response.text

        except Exception as e:
            mensagem_erro = str(e)
            print(f"❌ O modelo {modelo_atual} falhou: {mensagem_erro}")
            
            # Se o erro for "RESOURCE_EXHAUSTED" (429), significa que o limite da chave acabou.
            # Nesse caso não adianta tentar outros modelos, avisamos o usuário na tela.
            if "429" in mensagem_erro or "RESOURCE_EXHAUSTED" in mensagem_erro:
                return "A IA está dormindo 😴. O limite gratuito da API acabou. Tente novamente mais tarde ou use uma nova chave."

    # Se ele testar todos da lista e o Google recusar todos
    return "Erro técnico: A API do Google recusou a conexão. Verifique o terminal para detalhes."