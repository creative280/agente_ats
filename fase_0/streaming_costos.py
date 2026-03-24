import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODELO = "llama-3.3-70b-versatile"


def consulta_streaming(mensaje: str):
    """Respuesta en tiempo real token por token."""
    stream = client.chat.completions.create(
        model=MODELO,
        messages=[{"role": "user", "content": mensaje}],
        stream=True,
    )
    texto_completo = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            texto_completo += delta
    print()
    return texto_completo


def info_uso(texto: str) -> dict:
    """Información sobre el uso del tier gratuito de Groq."""
    palabras = len(texto.split())
    tokens_aprox = int(palabras * 1.3)
    return {
        "palabras_respuesta": palabras,
        "tokens_aprox": tokens_aprox,
        "costo": "GRATIS (tier gratuito de Groq)",
        "limite": "30 requests/minuto | 14,400 requests/día",
        "modelo": MODELO,
    }


if __name__ == "__main__":
    respuesta = consulta_streaming(
        "Dame 5 ideas de negocio con IA en Latinoamérica"
    )
    print()
    info = info_uso(respuesta)
    for k, v in info.items():
        print(f"  {k}: {v}")
