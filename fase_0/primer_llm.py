import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODELO = "llama-3.3-70b-versatile"


def consultar_llm(mensaje: str, sistema: str = "Eres un asistente útil. Responde en español.") -> str:
    """Envía un mensaje al LLM y retorna la respuesta."""
    respuesta = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": sistema},
            {"role": "user", "content": mensaje},
        ],
        temperature=0.7,
        max_tokens=1000,
    )
    return respuesta.choices[0].message.content


if __name__ == "__main__":
    print(consultar_llm("Explícame como optiimzar procesos con power bi"))
