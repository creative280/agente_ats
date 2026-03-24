import os
import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path, override=True)

app = FastAPI(title="Chat IA - Fase 0")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODELO = "llama-3.3-70b-versatile"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# --- Agente BD (se activa solo si DATABASE_URL está configurada) ---
agente_bd = None
bd_disponible = False

if os.getenv("DATABASE_URL"):
    try:
        from agente_sql import AgenteBD
        agente_bd = AgenteBD()
        bd_disponible = True
        print("[APP] Agente de Base de Datos ACTIVADO")
    except Exception as e:
        print(f"[APP] No se pudo conectar a la BD: {e}")
        print("[APP] El modo 'Analista BD' no estará disponible")

PERSONALIDADES = {
    "asistente": "Eres un asistente útil y amigable. Responde en español de forma clara y concisa.",
    "analista": (
        "Eres un analista de datos senior. Cuando recibas datos, identifica patrones, "
        "anomalías y da recomendaciones accionables con métricas. Responde en español."
    ),
    "coach": (
        "Eres un coach de carrera tech para desarrolladores latinoamericanos. "
        "Eres motivador pero realista. Das consejos prácticos. Responde en español."
    ),
    "programador": (
        "Eres un programador senior experto en Python, JavaScript y SQL. "
        "Explicas conceptos con ejemplos de código claros. Responde en español."
    ),
}

if bd_disponible:
    PERSONALIDADES["analista_bd"] = "Conectado a la base de datos real de la empresa."

sesiones: dict[str, list[dict]] = {}


class MensajeRequest(BaseModel):
    mensaje: str
    session_id: str = "default"
    personalidad: str = "asistente"


class CambiarBDRequest(BaseModel):
    nombre_bd: str


def _persistir_database_url(nueva_url: str) -> bool:
    """
    Guarda DATABASE_URL en .env.
    Retorna True si se pudo persistir, False si no.
    """
    try:
        if ENV_PATH.exists():
            lineas = ENV_PATH.read_text(encoding="utf-8").splitlines()
        else:
            lineas = []

        actualizado = False
        nuevas_lineas = []
        for linea in lineas:
            if linea.strip().startswith("DATABASE_URL="):
                nuevas_lineas.append(f"DATABASE_URL={nueva_url}")
                actualizado = True
            else:
                nuevas_lineas.append(linea)

        if not actualizado:
            if nuevas_lineas and nuevas_lineas[-1].strip() != "":
                nuevas_lineas.append("")
            nuevas_lineas.append(f"DATABASE_URL={nueva_url}")

        ENV_PATH.write_text("\n".join(nuevas_lineas) + "\n", encoding="utf-8")
        return True
    except Exception:
        return False


def obtener_historial(session_id: str, personalidad: str) -> list[dict]:
    if session_id not in sesiones:
        sesiones[session_id] = [
            {"role": "system", "content": PERSONALIDADES.get(personalidad, PERSONALIDADES["asistente"])}
        ]
    return sesiones[session_id]


@app.post("/chat")
async def chat(req: MensajeRequest):
    if req.personalidad == "analista_bd" and agente_bd:
        respuesta_texto = agente_bd.consultar(req.mensaje)
        return {"respuesta": respuesta_texto, "modelo": MODELO, "modo": "base_de_datos"}

    historial = obtener_historial(req.session_id, req.personalidad)
    historial.append({"role": "user", "content": req.mensaje})
    mensajes_enviar = historial[:1] + historial[-20:]

    respuesta = client.chat.completions.create(
        model=MODELO,
        messages=mensajes_enviar,
        temperature=0.7,
        max_tokens=2000,
    )
    contenido = respuesta.choices[0].message.content
    historial.append({"role": "assistant", "content": contenido})

    return {
        "respuesta": contenido,
        "modelo": MODELO,
        "mensajes_en_sesion": len(historial) - 1,
    }


@app.post("/chat/stream")
async def chat_stream(req: MensajeRequest):
    if req.personalidad == "analista_bd" and agente_bd:
        def generar_bd():
            yield from agente_bd.consultar_stream(req.mensaje)
        return StreamingResponse(generar_bd(), media_type="text/plain")

    historial = obtener_historial(req.session_id, req.personalidad)
    historial.append({"role": "user", "content": req.mensaje})
    mensajes_enviar = historial[:1] + historial[-20:]

    def generar():
        stream = client.chat.completions.create(
            model=MODELO,
            messages=mensajes_enviar,
            temperature=0.7,
            max_tokens=2000,
            stream=True,
        )
        texto_completo = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                texto_completo += delta
                yield delta
        historial.append({"role": "assistant", "content": texto_completo})

    return StreamingResponse(generar(), media_type="text/plain")


@app.post("/reset")
async def reset(session_id: str = "default"):
    sesiones.pop(session_id, None)
    if agente_bd:
        agente_bd.reset()
    return {"status": "ok", "mensaje": "Sesión reiniciada"}


@app.get("/personalidades")
async def listar_personalidades():
    return {k: v[:80] + "..." for k, v in PERSONALIDADES.items()}


@app.get("/bd/status")
async def bd_status():
    """Estado de la conexión a la BD."""
    if not agente_bd:
        return {"conectado": False, "mensaje": "DATABASE_URL no configurada en .env"}
    from database import test_conexion
    return test_conexion(agente_bd.engine)


@app.get("/bd/esquema")
async def bd_esquema():
    """Retorna el esquema completo de la BD."""
    if not agente_bd:
        return {"error": "BD no conectada"}
    return {"tablas": agente_bd.tablas, "total": len(agente_bd.tablas), "tipo": agente_bd.tipo_bd}


@app.get("/bd/base")
async def bd_base_actual():
    """Retorna el nombre de la base de datos configurada actualmente."""
    from sqlalchemy.engine import make_url

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"conectado": False, "mensaje": "DATABASE_URL no configurada"}

    try:
        url = make_url(database_url)
        return {
            "conectado": bool(agente_bd),
            "nombre_bd": url.database,
            "driver": url.drivername,
            "host": url.host,
            "puerto": url.port,
        }
    except Exception as e:
        return {"conectado": False, "error": f"DATABASE_URL inválida: {e}"}


@app.get("/bd/bases")
async def bd_bases_disponibles():
    """Lista las bases de datos disponibles para el usuario actual."""
    from sqlalchemy.engine import make_url
    from database import listar_bases_disponibles

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "mensaje": "DATABASE_URL no configurada en .env", "bases": []},
        )

    try:
        actual = make_url(database_url).database
        bases = listar_bases_disponibles(database_url)
        return {
            "status": "ok",
            "base_actual": actual,
            "bases": bases,
            "total": len(bases),
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "mensaje": f"No se pudieron listar las bases disponibles: {e}", "bases": []},
        )


@app.post("/bd/base")
async def bd_cambiar_base(req: CambiarBDRequest):
    """
    Cambia el nombre de la BD en DATABASE_URL y reconecta el agente.
    Solo modifica el nombre de base; mantiene servidor, usuario y credenciales.
    """
    global agente_bd, bd_disponible

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "mensaje": "DATABASE_URL no configurada en .env"},
        )

    try:
        from database import cambiar_nombre_bd_en_url, listar_bases_disponibles
        bases_disponibles = listar_bases_disponibles(database_url)
        if bases_disponibles and req.nombre_bd not in bases_disponibles:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "mensaje": f"La base '{req.nombre_bd}' no está disponible para este usuario.",
                    "bases_disponibles": bases_disponibles,
                },
            )

        nueva_url = cambiar_nombre_bd_en_url(database_url, req.nombre_bd)
        os.environ["DATABASE_URL"] = nueva_url

        from agente_sql import AgenteBD
        agente_bd = AgenteBD()
        bd_disponible = True
        persistido = _persistir_database_url(nueva_url)

        return {
            "status": "ok",
            "mensaje": (
                f"Base de datos cambiada a '{req.nombre_bd}' y agente reconectado."
                if persistido
                else f"Base de datos cambiada a '{req.nombre_bd}' y agente reconectado (no se pudo guardar en .env)."
            ),
            "nombre_bd": req.nombre_bd,
            "persistido_en_env": persistido,
        }
    except Exception as e:
        bd_disponible = bool(agente_bd)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "mensaje": f"No se pudo cambiar la base de datos: {e}"},
        )


_CONTEXTO_PATH = Path(__file__).resolve().parent / "bd_contexto.json"


@app.get("/bd/contexto")
async def bd_contexto_get():
    """Lee el archivo de contexto de negocio."""
    if _CONTEXTO_PATH.exists():
        return json.loads(_CONTEXTO_PATH.read_text(encoding="utf-8"))
    return {"descripcion_bd": "", "tablas": {}, "ejemplos_sql": [], "reglas_negocio": []}


@app.post("/bd/contexto")
async def bd_contexto_post(request: Request):
    """Guarda el contexto de negocio y recarga en el agente."""
    data = await request.json()
    _CONTEXTO_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if agente_bd:
        agente_bd.recargar_contexto()
    return {"status": "ok", "mensaje": "Contexto guardado y recargado"}


@app.get("/bd/config", response_class=HTMLResponse)
async def bd_config_page():
    """Página de configuración del contexto de BD."""
    with open(os.path.join(os.path.dirname(__file__), "bd_config.html"), encoding="utf-8") as f:
        return f.read()


@app.get("/", response_class=HTMLResponse)
async def root():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8") as f:
        return f.read()
