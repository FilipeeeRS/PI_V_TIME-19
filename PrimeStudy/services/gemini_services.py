import os
import json
from google import genai
from google.genai import types

def gerar_conteudo(tipo, texto, historico=""):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Erro: Chave da API do Gemini não encontrada."

        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(temperature=0.7)

        regra_formatacao = (
            "IMPORTANTE: Retorne APENAS o conteúdo usando tags HTML básicas (<b>, <ul>, <li>, <br>, <p>, <h3>). "
            "NÃO inclua blocos de código markdown, NÃO inclua tags <style>. "
            "Retorne APENAS o HTML puro do conteúdo.\n\n"
        )

        # Regra que força a IA a não repetir o que já foi gerado
        aviso_historico = ""
        if historico:
            aviso_historico = f"ATENÇÃO: O utilizador solicitou MAIS itens. Você DEVE gerar conteúdo INÉDITO, sendo criativo e garantindo que seja diferente destes que já existem:\n{historico}\n\n"

        if tipo == 'resumo':
            prompt = regra_formatacao + aviso_historico + f"Faça um resumo detalhado e organizado do seguinte texto:\n\n{texto}"
        elif tipo == 'resumo_menor':
            prompt = regra_formatacao + f"Faça um resumo MUITO CURTO, direto ao ponto e altamente sintetizado do texto abaixo:\n\n{texto}"
        elif tipo == 'topicos':
            prompt = regra_formatacao + aviso_historico + f"Extraia os principais pontos do texto abaixo em formato de tópicos curtos e diretos:\n\n{texto}"
        elif tipo == 'flashcards':
            prompt = regra_formatacao + aviso_historico + f"Crie flashcards de estudo baseados no texto no formato '<p><b>Pergunta:</b> ... <br> <b>Resposta:</b> ...</p>':\n\n{texto}"
        elif tipo == 'questoes':
            prompt = (
                aviso_historico +
                "Crie 5 questões de múltipla escolha sobre o texto, com 4 alternativas cada. "
                "O formato deve ser ESTRITAMENTE este JSON:\n"
                "[\n  {\n    \"pergunta\": \"Texto?\",\n    \"alternativas\": [\"A\", \"B\", \"C\", \"D\"],\n    \"correta\": 1\n  }\n]\n"
                "Nota: O campo 'correta' deve ser o índice (0 a 3) da alternativa certa.\n\n"
                f"Texto:\n{texto}"
            )
            config = types.GenerateContentConfig(temperature=0.8, response_mime_type="application/json")
        elif tipo == 'sugerir_materia':
            prompt = f"Analise este texto e sugira um nome genérico e curto de disciplina/matéria (máximo de 3 palavras). Retorne APENAS o nome:\n\n{texto}"
        else:
            prompt = regra_formatacao + aviso_historico + f"Analise o texto e traga as informações principais:\n\n{texto}"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )

        resultado_limpo = response.text.replace('```html', '').replace('```json', '').replace('```', '').strip()

        if tipo == 'questoes':
            try:
                json.loads(resultado_limpo)
            except json.JSONDecodeError:
                return '[{"pergunta": "Erro ao gerar questões.", "alternativas": ["-", "-", "-", "-"], "correta": 0}]'

        return resultado_limpo

    except Exception as e:
        print(f"Erro Gemini: {e}") 
        return f"<p>Erro ao gerar conteúdo.</p>"