from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def gerar_resumo(texto):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
Gere um resumo fiel ao texto abaixo.
- Não invente informações
- Use tópicos claros
- Destaque conceitos principais

Texto:
{texto[:10000]}
"""
        )

        return response.text

    except Exception as e:
        print("Erro Gemini:", e)
        return "Erro ao gerar resumo."