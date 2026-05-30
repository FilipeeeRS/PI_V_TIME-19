import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel


class Questao(BaseModel):
    """Schema de saída estruturada para questões de múltipla escolha."""
    pergunta: str
    alternativas: list[str]
    correta: int
    explicacao: str


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
            regras_quiz = (
                "Você é um professor especialista em elaborar avaliações de múltipla escolha. "
                "Gere as questões em português do Brasil, baseadas ESTRITAMENTE no texto fornecido — "
                "nunca invente fatos que não estejam no texto.\n"
                "Regras de qualidade (siga todas):\n"
                "1. Cada questão deve testar COMPREENSÃO e raciocínio, não apenas memorização literal.\n"
                "2. Exatamente UMA alternativa correta e inequívoca; as outras 3 devem ser plausíveis, "
                "do mesmo assunto e de tamanho parecido, sem serem obviamente erradas.\n"
                "3. Varie a posição da alternativa correta entre as questões (não deixe sempre no mesmo índice).\n"
                "4. Não use 'todas as anteriores' nem 'nenhuma das anteriores'.\n"
                "5. Enunciados claros e autossuficientes; evite ambiguidade, negativas duplas e pegadinhas.\n"
                "6. Aborde partes diferentes do texto, não apenas o começo.\n"
                "7. Sempre exatamente 4 alternativas por questão.\n"
                "8. 'correta' é o índice (0 a 3) da alternativa certa dentro de 'alternativas'.\n"
                "9. 'explicacao' é 1 ou 2 frases curtas justificando por que a alternativa correta está certa."
            )
            prompt = (
                aviso_historico +
                "Crie 5 questões de múltipla escolha sobre o texto a seguir.\n\n"
                f"Texto:\n{texto}"
            )
            config = types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
                response_schema=list[Questao],
                system_instruction=regras_quiz,
            )
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
                dados = json.loads(resultado_limpo)
                questoes_validas = []
                for q in dados:
                    alternativas = q.get('alternativas') or []
                    if len(alternativas) < 2 or not q.get('pergunta'):
                        continue
                    correta = q.get('correta', 0)
                    if not isinstance(correta, int) or correta < 0 or correta >= len(alternativas):
                        correta = 0
                    questoes_validas.append({
                        'pergunta': q.get('pergunta', ''),
                        'alternativas': alternativas,
                        'correta': correta,
                        'explicacao': q.get('explicacao', '')
                    })
                if not questoes_validas:
                    raise ValueError('Nenhuma questão válida foi gerada')
                resultado_limpo = json.dumps(questoes_validas, ensure_ascii=False)
            except (json.JSONDecodeError, ValueError, AttributeError, TypeError):
                return '[{"pergunta": "Erro ao gerar questões.", "alternativas": ["-", "-", "-", "-"], "correta": 0, "explicacao": ""}]'

        return resultado_limpo

    except Exception as e:
        print(f"Erro Gemini: {e}") 
        return f"<p>Erro ao gerar conteúdo.</p>"