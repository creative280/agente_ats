# Roadmap: Especialización en Agentes IA + Servidor Remoto + Apps de Mensajería

> **Perfil base:** Ing. Software VIII | Python, Node, JS, React, PHP, MySQL, SQL Server | Excel, Power BI
> **Meta:** Construir agentes de IA autónomos que se integren con WhatsApp, Telegram y otros canales, desplegados en servidores remotos.

---

## Visión General de Fases

```
FASE 0 ─ Fundamentos (2-3 semanas)
  │  LLMs, APIs de IA, prompting, entornos
  ▼
FASE 1 ─ Primer Agente Conversacional (3-4 semanas)
  │  Chatbot inteligente con OpenAI/Gemini + memoria
  ▼
FASE 2 ─ Integración con Mensajería (3-4 semanas)
  │  WhatsApp Business API, Telegram Bot, Webhooks
  ▼
FASE 3 ─ Agentes Autónomos con Herramientas (4-5 semanas)
  │  LangChain/LangGraph, tool calling, RAG
  ▼
FASE 4 ─ Infraestructura y Servidor Remoto (3-4 semanas)
  │  VPS, Docker, CI/CD, monitoreo
  ▼
FASE 5 ─ Automatización Avanzada (4-5 semanas)
  │  Workflows multi-agente, n8n, colas de tareas
  ▼
FASE 6 ─ Proyecto Integrador + Monetización (4-6 semanas)
  │  SaaS completo, clientes reales
  ▼
  ★  ESPECIALISTA EN AGENTES IA + AUTOMATIZACIÓN
```

---

## FASE 0: Fundamentos de IA Generativa y Entorno (2-3 semanas)

### Objetivos
- Entender cómo funcionan los LLMs (Large Language Models)
- Dominar las APIs de OpenAI, Google Gemini y modelos open-source
- Configurar un entorno de desarrollo profesional

### Conceptos Clave
| Concepto | Descripción |
|----------|------------|
| LLM | Modelo de lenguaje que predice tokens (GPT-4, Gemini, Llama) |
| Token | Unidad mínima de texto que procesa el modelo |
| Prompt Engineering | Técnica para diseñar instrucciones efectivas |
| Temperature | Control de creatividad vs determinismo (0.0 - 2.0) |
| System Prompt | Instrucción base que define el comportamiento del agente |
| Context Window | Cantidad máxima de tokens que el modelo puede procesar |

### Configuración del Entorno

```bash
# 1. Instalar Python 3.11+ y Node 20+
# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 3. Instalar dependencias base
pip install openai google-generativeai python-dotenv httpx pydantic

# 4. Archivo .env (NUNCA subir a git)
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=AI...
```

### Proyecto 0.1: Tu primer llamado a un LLM

```python
# fase_0/primer_llm.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def consultar_llm(mensaje: str, sistema: str = "Eres un asistente útil.") -> str:
    respuesta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": sistema},
            {"role": "user", "content": mensaje}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return respuesta.choices[0].message.content

if __name__ == "__main__":
    print(consultar_llm("Explícame qué es un agente de IA en 3 párrafos"))
```

### Proyecto 0.2: Prompt Engineering aplicado

```python
# fase_0/prompt_engineering.py
from primer_llm import consultar_llm

PROMPT_ANALISTA = """Eres un analista de datos senior especializado en retail.
Cuando recibas datos, debes:
1. Identificar patrones y anomalías
2. Dar recomendaciones accionables
3. Responder en formato estructurado con bullets
4. Incluir métricas específicas cuando sea posible

Formato de respuesta:
## Análisis
[tu análisis]

## Hallazgos Clave
- [hallazgo 1]
- [hallazgo 2]

## Recomendaciones
1. [recomendación con impacto estimado]
"""

datos = """
Ventas enero: $45,000 | Febrero: $38,000 | Marzo: $52,000
Producto estrella: Widget A (40% del total)
Devoluciones: 12% en febrero (promedio histórico: 5%)
"""

resultado = consultar_llm(datos, PROMPT_ANALISTA)
print(resultado)
```

### Proyecto 0.3: Streaming y manejo de costos

```python
# fase_0/streaming_costos.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def consulta_streaming(mensaje: str):
    """Respuesta en tiempo real token por token."""
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": mensaje}],
        stream=True
    )
    texto_completo = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            fragmento = chunk.choices[0].delta.content
            print(fragmento, end="", flush=True)
            texto_completo += fragmento
    print()
    return texto_completo

def estimar_costo(texto: str, modelo: str = "gpt-4o-mini") -> dict:
    """Estimación básica de tokens y costo."""
    tokens_aprox = len(texto.split()) * 1.3
    precios = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},   # por 1M tokens
        "gpt-4o": {"input": 2.50, "output": 10.00},
    }
    precio = precios.get(modelo, precios["gpt-4o-mini"])
    costo = (tokens_aprox / 1_000_000) * precio["input"]
    return {"tokens_aprox": int(tokens_aprox), "costo_usd": round(costo, 6)}

if __name__ == "__main__":
    respuesta = consulta_streaming("Dame 5 ideas de negocio con IA en Latinoamérica")
    print("\n", estimar_costo(respuesta))
```

### Recursos Fase 0
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Google AI Studio](https://aistudio.google.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## FASE 1: Primer Agente Conversacional (3-4 semanas)

### Objetivos
- Construir un chatbot con memoria de conversación
- Implementar diferentes personalidades/roles
- Manejar historial de mensajes y contexto
- Introducir FastAPI como backend

### Conceptos Clave
| Concepto | Descripción |
|----------|------------|
| Memoria conversacional | Mantener contexto entre mensajes del usuario |
| Session management | Gestionar múltiples conversaciones simultáneas |
| System prompt dinámico | Cambiar comportamiento del agente según contexto |
| Function calling | Permitir al LLM invocar funciones de tu código |

### Proyecto 1.1: Chatbot con memoria (CLI)

```python
# fase_1/chatbot_memoria.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI()

class ChatbotConMemoria:
    def __init__(self, personalidad: str, modelo: str = "gpt-4o-mini"):
        self.modelo = modelo
        self.historial: list[dict] = [
            {"role": "system", "content": personalidad}
        ]
        self.created_at = datetime.now()

    def enviar(self, mensaje: str) -> str:
        self.historial.append({"role": "user", "content": mensaje})

        respuesta = client.chat.completions.create(
            model=self.modelo,
            messages=self.historial,
            temperature=0.7
        )
        contenido = respuesta.choices[0].message.content
        self.historial.append({"role": "assistant", "content": contenido})
        return contenido

    def resumen_sesion(self) -> dict:
        return {
            "mensajes": len(self.historial) - 1,
            "inicio": self.created_at.isoformat(),
            "ultimo_mensaje": self.historial[-1]["content"][:100] if len(self.historial) > 1 else None
        }

if __name__ == "__main__":
    bot = ChatbotConMemoria(
        personalidad="""Eres un coach de carrera tech para desarrolladores 
        latinoamericanos. Hablas en español, eres motivador pero realista. 
        Das consejos prácticos basados en el mercado actual."""
    )
    print("Chat iniciado (escribe 'salir' para terminar)\n")
    while True:
        entrada = input("Tú: ")
        if entrada.lower() == "salir":
            print("\nResumen:", bot.resumen_sesion())
            break
        print(f"\nCoach: {bot.enviar(entrada)}\n")
```

### Proyecto 1.2: API REST con FastAPI + Múltiples sesiones

```python
# fase_1/api_chatbot.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chatbot_memoria import ChatbotConMemoria
import uuid

app = FastAPI(title="Agente Conversacional API")

sesiones: dict[str, ChatbotConMemoria] = {}

PERSONALIDADES = {
    "coach_tech": """Eres un coach de carrera tech para desarrolladores latinoamericanos.
        Das consejos prácticos y motivadores.""",
    "analista_datos": """Eres un analista de datos senior. Ayudas a interpretar datos,
        crear consultas SQL y diseñar dashboards.""",
    "soporte_tecnico": """Eres un agente de soporte técnico nivel 2. 
        Resuelves problemas paso a paso con paciencia.""",
}

class MensajeRequest(BaseModel):
    mensaje: str

class NuevaSesionRequest(BaseModel):
    personalidad: str = "coach_tech"

class MensajeResponse(BaseModel):
    session_id: str
    respuesta: str
    total_mensajes: int

@app.post("/sesiones", response_model=dict)
def crear_sesion(req: NuevaSesionRequest):
    if req.personalidad not in PERSONALIDADES:
        raise HTTPException(400, f"Personalidades disponibles: {list(PERSONALIDADES.keys())}")
    sid = str(uuid.uuid4())
    sesiones[sid] = ChatbotConMemoria(PERSONALIDADES[req.personalidad])
    return {"session_id": sid, "personalidad": req.personalidad}

@app.post("/sesiones/{session_id}/mensajes", response_model=MensajeResponse)
def enviar_mensaje(session_id: str, req: MensajeRequest):
    if session_id not in sesiones:
        raise HTTPException(404, "Sesión no encontrada")
    bot = sesiones[session_id]
    respuesta = bot.enviar(req.mensaje)
    return MensajeResponse(
        session_id=session_id,
        respuesta=respuesta,
        total_mensajes=len(bot.historial) - 1
    )

@app.get("/sesiones/{session_id}")
def obtener_sesion(session_id: str):
    if session_id not in sesiones:
        raise HTTPException(404, "Sesión no encontrada")
    return sesiones[session_id].resumen_sesion()

# Ejecutar: uvicorn api_chatbot:app --reload --port 8000
```

### Proyecto 1.3: Function Calling (el agente ejecuta acciones)

```python
# fase_1/agente_con_funciones.py
import os, json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI()

def obtener_clima(ciudad: str) -> dict:
    """Simula obtener el clima (en producción usarías una API real)."""
    climas = {
        "bogota": {"temp": 18, "condicion": "Nublado", "humedad": 75},
        "medellin": {"temp": 26, "condicion": "Soleado", "humedad": 60},
        "lima": {"temp": 22, "condicion": "Parcialmente nublado", "humedad": 80},
    }
    return climas.get(ciudad.lower(), {"temp": 20, "condicion": "Desconocido", "humedad": 50})

def buscar_en_bd(consulta_sql: str) -> list:
    """Simula una consulta a base de datos."""
    return [
        {"producto": "Widget A", "ventas": 150, "mes": "marzo"},
        {"producto": "Widget B", "ventas": 89, "mes": "marzo"},
    ]

def enviar_notificacion(destinatario: str, mensaje: str) -> dict:
    """Simula enviar una notificación."""
    return {"status": "enviado", "destinatario": destinatario, "timestamp": datetime.now().isoformat()}

HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Obtiene el clima actual de una ciudad",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {"type": "string", "description": "Nombre de la ciudad"}
                },
                "required": ["ciudad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_en_bd",
            "description": "Ejecuta una consulta SQL a la base de datos de ventas",
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta_sql": {"type": "string", "description": "Consulta SQL a ejecutar"}
                },
                "required": ["consulta_sql"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enviar_notificacion",
            "description": "Envía una notificación a un usuario",
            "parameters": {
                "type": "object",
                "properties": {
                    "destinatario": {"type": "string"},
                    "mensaje": {"type": "string"}
                },
                "required": ["destinatario", "mensaje"]
            }
        }
    }
]

FUNCIONES_DISPONIBLES = {
    "obtener_clima": obtener_clima,
    "buscar_en_bd": buscar_en_bd,
    "enviar_notificacion": enviar_notificacion,
}

def agente_con_herramientas(mensaje: str) -> str:
    mensajes = [
        {"role": "system", "content": "Eres un asistente empresarial que puede consultar el clima, "
         "buscar datos en la BD y enviar notificaciones. Usa las herramientas cuando sea necesario."},
        {"role": "user", "content": mensaje}
    ]

    respuesta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensajes,
        tools=HERRAMIENTAS,
        tool_choice="auto"
    )

    mensaje_respuesta = respuesta.choices[0].message

    while mensaje_respuesta.tool_calls:
        mensajes.append(mensaje_respuesta)
        for tool_call in mensaje_respuesta.tool_calls:
            nombre_fn = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"  [Ejecutando: {nombre_fn}({args})]")

            resultado = FUNCIONES_DISPONIBLES[nombre_fn](**args)

            mensajes.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(resultado, ensure_ascii=False)
            })

        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mensajes,
            tools=HERRAMIENTAS,
            tool_choice="auto"
        )
        mensaje_respuesta = respuesta.choices[0].message

    return mensaje_respuesta.content

if __name__ == "__main__":
    consultas = [
        "¿Cómo está el clima en Medellín y Bogotá?",
        "Muéstrame las ventas de marzo y envíale un resumen al gerente",
    ]
    for q in consultas:
        print(f"\nUsuario: {q}")
        print(f"Agente: {agente_con_herramientas(q)}")
```

### Recursos Fase 1
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

---

## FASE 2: Integración con Apps de Mensajería (3-4 semanas)

### Objetivos
- Conectar tu agente a WhatsApp via API oficial (Meta Cloud API)
- Crear un bot de Telegram completo
- Manejar webhooks, verificación y seguridad
- Implementar flujos conversacionales multicanal

### Arquitectura General

```
Usuario (WhatsApp/Telegram)
        │
        ▼
  [Webhook Endpoint]  ◄── tu servidor FastAPI
        │
        ▼
  [Router de Mensajes]
        │
    ┌───┴───┐
    ▼       ▼
 [Agente IA]  [BD Sesiones]
    │              │
    ▼              ▼
 [LLM API]    [PostgreSQL/Redis]
    │
    ▼
 [Respuesta] ──► API de WhatsApp/Telegram ──► Usuario
```

### Proyecto 2.1: Bot de Telegram

```python
# fase_2/telegram_bot.py
import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    ContextTypes, filters
)
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai_client = OpenAI()
logging.basicConfig(level=logging.INFO)

conversaciones: dict[int, list] = {}

SYSTEM_PROMPT = """Eres un asistente de productividad personal en Telegram.
Ayudas a los usuarios a organizar tareas, establecer recordatorios 
y dar consejos de productividad. Sé conciso porque es un chat."""

def obtener_respuesta_ia(user_id: int, mensaje: str) -> str:
    if user_id not in conversaciones:
        conversaciones[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    conversaciones[user_id].append({"role": "user", "content": mensaje})

    # Limitar contexto a últimos 20 mensajes para controlar costos
    mensajes_enviar = conversaciones[user_id][:1] + conversaciones[user_id][-20:]

    respuesta = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensajes_enviar,
        temperature=0.7,
        max_tokens=500
    )
    contenido = respuesta.choices[0].message.content
    conversaciones[user_id].append({"role": "assistant", "content": contenido})
    return contenido

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu asistente de productividad con IA.\n\n"
        "Puedo ayudarte a:\n"
        "- Organizar tus tareas\n"
        "- Planificar tu día\n"
        "- Dar consejos de productividad\n\n"
        "¡Escríbeme lo que necesites!"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversaciones.pop(user_id, None)
    await update.message.reply_text("Conversación reiniciada. ¡Empecemos de nuevo!")

async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mensaje = update.message.text

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    respuesta = obtener_respuesta_ia(user_id, mensaje)
    await update.message.reply_text(respuesta)

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    print("Bot de Telegram iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
```

### Proyecto 2.2: WhatsApp Business con Meta Cloud API

```python
# fase_2/whatsapp_webhook.py
import os
import hmac
import hashlib
import httpx
from fastapi import FastAPI, Request, HTTPException, Query
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI(title="WhatsApp Bot")
openai_client = OpenAI()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET")

conversaciones: dict[str, list] = {}

SYSTEM_PROMPT = """Eres un asistente de atención al cliente para una tienda online.
Puedes ayudar con: estado de pedidos, políticas de devolución, 
información de productos y horarios. Sé amable y conciso."""

async def enviar_mensaje_whatsapp(telefono: str, mensaje: str):
    """Envía un mensaje de texto via WhatsApp Cloud API."""
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {"body": mensaje}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

def obtener_respuesta_ia(telefono: str, mensaje: str) -> str:
    if telefono not in conversaciones:
        conversaciones[telefono] = [{"role": "system", "content": SYSTEM_PROMPT}]

    conversaciones[telefono].append({"role": "user", "content": mensaje})
    mensajes = conversaciones[telefono][:1] + conversaciones[telefono][-15:]

    respuesta = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensajes,
        temperature=0.5,
        max_tokens=300
    )
    contenido = respuesta.choices[0].message.content
    conversaciones[telefono].append({"role": "assistant", "content": contenido})
    return contenido

@app.get("/webhook")
async def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Verificación del webhook por Meta."""
    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(403, "Token de verificación inválido")

@app.post("/webhook")
async def recibir_mensaje(request: Request):
    """Recibe y procesa mensajes entrantes de WhatsApp."""
    body = await request.json()

    if body.get("object") != "whatsapp_business_account":
        return {"status": "ignored"}

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            mensajes = value.get("messages", [])

            for msg in mensajes:
                if msg.get("type") != "text":
                    continue

                telefono = msg["from"]
                texto = msg["text"]["body"]

                respuesta = obtener_respuesta_ia(telefono, texto)
                await enviar_mensaje_whatsapp(telefono, respuesta)

    return {"status": "ok"}

# Ejecutar: uvicorn whatsapp_webhook:app --reload --port 8000
# Exponer con ngrok: ngrok http 8000
```

### Proyecto 2.3: Router multicanal

```python
# fase_2/router_multicanal.py
from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class Canal(str, Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    WEB = "web"

class MensajeEntrante(BaseModel):
    canal: Canal
    usuario_id: str
    contenido: str
    timestamp: datetime = None
    metadata: dict = {}

class MensajeSaliente(BaseModel):
    canal: Canal
    usuario_id: str
    contenido: str
    timestamp: datetime = None

class RouterMulticanal:
    """Enruta mensajes de cualquier canal al agente y de vuelta."""

    def __init__(self, agente_ia):
        self.agente = agente_ia
        self.adaptadores = {}

    def registrar_adaptador(self, canal: Canal, adaptador):
        self.adaptadores[canal] = adaptador

    async def procesar(self, mensaje: MensajeEntrante) -> MensajeSaliente:
        # Normalizar: todos los canales pasan por el mismo pipeline
        clave_sesion = f"{mensaje.canal}:{mensaje.usuario_id}"

        respuesta_texto = self.agente.procesar(clave_sesion, mensaje.contenido)

        saliente = MensajeSaliente(
            canal=mensaje.canal,
            usuario_id=mensaje.usuario_id,
            contenido=respuesta_texto,
            timestamp=datetime.now()
        )

        # Enviar por el canal correcto
        adaptador = self.adaptadores.get(mensaje.canal)
        if adaptador:
            await adaptador.enviar(saliente)

        return saliente
```

### Recursos Fase 2
- [Meta WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [python-telegram-bot](https://docs.python-telegram-bot.org/)
- [ngrok](https://ngrok.com/) para exponer tu servidor local

---

## FASE 3: Agentes Autónomos con Herramientas - LangChain/LangGraph (4-5 semanas)

### Objetivos
- Dominar LangChain y LangGraph para agentes complejos
- Implementar RAG (Retrieval-Augmented Generation)
- Crear agentes que usan múltiples herramientas
- Manejar flujos de decisión complejos

### Conceptos Clave
| Concepto | Descripción |
|----------|------------|
| RAG | Búsqueda en documentos propios + generación con LLM |
| Vector Store | Base de datos de embeddings para búsqueda semántica |
| Tool/Agent | Componente que decide qué herramientas usar y cuándo |
| Chain | Secuencia de pasos de procesamiento |
| Graph (LangGraph) | Flujo de trabajo con nodos y decisiones condicionales |

### Proyecto 3.1: RAG - Chatbot sobre tus propios documentos

```python
# fase_3/rag_documentos.py
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, DirectoryLoader
)
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

def crear_base_conocimiento(directorio_docs: str) -> FAISS:
    """Carga documentos, los divide en chunks y crea vector store."""
    loader = DirectoryLoader(
        directorio_docs,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    documentos = loader.load()
    print(f"Documentos cargados: {len(documentos)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documentos)
    print(f"Chunks creados: {len(chunks)}")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("vectorstore_index")

    return vectorstore

def crear_chatbot_rag(vectorstore: FAISS) -> RetrievalQA:
    """Crea un chatbot que responde basado en los documentos."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        return_source_documents=True
    )
    return qa_chain

if __name__ == "__main__":
    # Primera vez: crear índice
    # vs = crear_base_conocimiento("./documentos")

    # Cargar índice existente
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vs = FAISS.load_local("vectorstore_index", embeddings, allow_dangerous_deserialization=True)

    chatbot = crear_chatbot_rag(vs)

    while True:
        pregunta = input("\nPregunta: ")
        if pregunta.lower() == "salir":
            break
        resultado = chatbot.invoke({"query": pregunta})
        print(f"\nRespuesta: {resultado['result']}")
        print(f"\nFuentes: {[d.metadata.get('source', 'N/A') for d in resultado['source_documents']]}")
```

### Proyecto 3.2: Agente con múltiples herramientas (LangChain)

```python
# fase_3/agente_multiherramienta.py
import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper
from dotenv import load_dotenv
import httpx

load_dotenv()

@tool
def calcular(expresion: str) -> str:
    """Calcula una expresión matemática. Ejemplo: '2 + 2' o '(15 * 3) / 7'"""
    try:
        resultado = eval(expresion, {"__builtins__": {}})
        return f"Resultado: {resultado}"
    except Exception as e:
        return f"Error: {e}"

@tool
def consultar_api_clima(ciudad: str) -> str:
    """Obtiene el clima actual de una ciudad usando OpenWeatherMap."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es"
    response = httpx.get(url)
    if response.status_code == 200:
        data = response.json()
        return (f"Clima en {ciudad}: {data['weather'][0]['description']}, "
                f"Temp: {data['main']['temp']}°C, Humedad: {data['main']['humidity']}%")
    return f"No se pudo obtener el clima para {ciudad}"

@tool
def consultar_base_datos(consulta: str) -> str:
    """Ejecuta una consulta a la base de datos de productos y ventas.
    Tablas: productos(id, nombre, precio, stock), ventas(id, producto_id, cantidad, fecha)"""
    # En producción, conectar a BD real con SQLAlchemy
    datos_ejemplo = {
        "productos": [
            {"id": 1, "nombre": "Laptop Pro", "precio": 1200, "stock": 15},
            {"id": 2, "nombre": "Mouse Inalámbrico", "precio": 25, "stock": 200},
        ],
        "ventas_marzo": {"total": 45000, "unidades": 380, "ticket_promedio": 118.4}
    }
    return str(datos_ejemplo)

def crear_agente():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres un asistente empresarial inteligente. Tienes acceso a herramientas
        para calcular, consultar el clima y acceder a la base de datos de la empresa.
        Usa las herramientas cuando sea necesario. Responde siempre en español."""),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    herramientas = [calcular, consultar_api_clima, consultar_base_datos]
    agent = create_openai_tools_agent(llm, herramientas, prompt)

    return AgentExecutor(
        agent=agent,
        tools=herramientas,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )

if __name__ == "__main__":
    agente = crear_agente()
    resultado = agente.invoke({
        "input": "¿Cuánto sería el ingreso si vendemos todo el stock de Laptops Pro? "
                 "También dime cómo está el clima en Bogotá."
    })
    print(f"\nRespuesta final: {resultado['output']}")
```

### Proyecto 3.3: Flujo complejo con LangGraph

```python
# fase_3/langgraph_flujo.py
import os
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

class EstadoConversacion(TypedDict):
    messages: Annotated[list, add_messages]
    categoria: str
    sentimiento: str
    requiere_humano: bool

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def clasificar_mensaje(state: EstadoConversacion) -> EstadoConversacion:
    """Clasifica el mensaje del usuario en categoría y sentimiento."""
    ultimo_mensaje = state["messages"][-1].content

    respuesta = llm.invoke([
        SystemMessage(content="""Clasifica el mensaje del usuario.
        Responde SOLO en este formato JSON:
        {"categoria": "ventas|soporte|queja|info", "sentimiento": "positivo|neutral|negativo"}"""),
        HumanMessage(content=ultimo_mensaje)
    ])

    import json
    try:
        clasificacion = json.loads(respuesta.content)
    except json.JSONDecodeError:
        clasificacion = {"categoria": "info", "sentimiento": "neutral"}

    return {
        **state,
        "categoria": clasificacion["categoria"],
        "sentimiento": clasificacion["sentimiento"]
    }

def decidir_ruta(state: EstadoConversacion) -> str:
    """Decide qué nodo sigue basado en la clasificación."""
    if state["sentimiento"] == "negativo" and state["categoria"] == "queja":
        return "escalar_humano"
    elif state["categoria"] == "ventas":
        return "agente_ventas"
    elif state["categoria"] == "soporte":
        return "agente_soporte"
    return "agente_general"

def agente_ventas(state: EstadoConversacion) -> EstadoConversacion:
    respuesta = llm.invoke([
        SystemMessage(content="Eres un vendedor experto. Responde consultas de ventas de forma persuasiva."),
        *state["messages"]
    ])
    return {"messages": [respuesta], "requiere_humano": False}

def agente_soporte(state: EstadoConversacion) -> EstadoConversacion:
    respuesta = llm.invoke([
        SystemMessage(content="Eres un agente de soporte técnico paciente. Da soluciones paso a paso."),
        *state["messages"]
    ])
    return {"messages": [respuesta], "requiere_humano": False}

def agente_general(state: EstadoConversacion) -> EstadoConversacion:
    respuesta = llm.invoke([
        SystemMessage(content="Eres un asistente amable. Responde preguntas generales."),
        *state["messages"]
    ])
    return {"messages": [respuesta], "requiere_humano": False}

def escalar_humano(state: EstadoConversacion) -> EstadoConversacion:
    from langchain_core.messages import AIMessage
    return {
        "messages": [AIMessage(content="Entiendo tu frustración. Estoy transfiriendo tu caso "
                     "a un agente humano que podrá ayudarte mejor. Un momento por favor.")],
        "requiere_humano": True
    }

# Construir el grafo
graph = StateGraph(EstadoConversacion)

graph.add_node("clasificar", clasificar_mensaje)
graph.add_node("agente_ventas", agente_ventas)
graph.add_node("agente_soporte", agente_soporte)
graph.add_node("agente_general", agente_general)
graph.add_node("escalar_humano", escalar_humano)

graph.set_entry_point("clasificar")
graph.add_conditional_edges("clasificar", decidir_ruta, {
    "agente_ventas": "agente_ventas",
    "agente_soporte": "agente_soporte",
    "agente_general": "agente_general",
    "escalar_humano": "escalar_humano",
})

graph.add_edge("agente_ventas", END)
graph.add_edge("agente_soporte", END)
graph.add_edge("agente_general", END)
graph.add_edge("escalar_humano", END)

app = graph.compile()

if __name__ == "__main__":
    mensajes_prueba = [
        "Quiero comprar 50 unidades del producto premium",
        "Mi pedido lleva 3 semanas y nadie me responde, estoy furioso",
        "¿Cuál es el horario de atención?",
        "La aplicación no carga, me sale error 500",
    ]

    for msg in mensajes_prueba:
        print(f"\n{'='*60}")
        print(f"Usuario: {msg}")
        resultado = app.invoke({
            "messages": [HumanMessage(content=msg)],
            "categoria": "",
            "sentimiento": "",
            "requiere_humano": False
        })
        print(f"Categoría: {resultado['categoria']}")
        print(f"Sentimiento: {resultado['sentimiento']}")
        print(f"Respuesta: {resultado['messages'][-1].content}")
        print(f"Escalado a humano: {resultado['requiere_humano']}")
```

### Recursos Fase 3
- [LangChain Docs](https://python.langchain.com/docs/get_started/introduction)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [FAISS](https://faiss.ai/)
- [ChromaDB](https://www.trychroma.com/) (alternativa a FAISS)

---

## FASE 4: Infraestructura y Servidor Remoto (3-4 semanas)

### Objetivos
- Desplegar agentes en un VPS (Virtual Private Server)
- Dockerizar aplicaciones
- Configurar CI/CD básico
- Implementar monitoreo y logging
- Manejar bases de datos en producción

### Proyecto 4.1: Dockerización completa

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: agente_db
      POSTGRES_USER: agente_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/conf:/etc/letsencrypt:ro
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

### Proyecto 4.2: Gestión de sesiones con Redis + PostgreSQL

```python
# fase_4/session_manager.py
import json
import asyncio
from datetime import datetime, timedelta
import redis.asyncio as redis
import asyncpg
from pydantic import BaseModel

class SesionChat(BaseModel):
    usuario_id: str
    canal: str
    mensajes: list[dict]
    created_at: datetime
    last_activity: datetime
    metadata: dict = {}

class SessionManager:
    """Maneja sesiones con Redis (cache rápido) + PostgreSQL (persistencia)."""

    def __init__(self, redis_url: str, postgres_url: str):
        self.redis_url = redis_url
        self.postgres_url = postgres_url
        self.redis: redis.Redis | None = None
        self.pg_pool: asyncpg.Pool | None = None
        self.ttl_sesion = 3600  # 1 hora en Redis

    async def conectar(self):
        self.redis = redis.from_url(self.redis_url, decode_responses=True)
        self.pg_pool = await asyncpg.create_pool(self.postgres_url)

        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sesiones (
                    id SERIAL PRIMARY KEY,
                    usuario_id VARCHAR(100) NOT NULL,
                    canal VARCHAR(50) NOT NULL,
                    mensajes JSONB NOT NULL DEFAULT '[]',
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    last_activity TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_sesiones_usuario 
                    ON sesiones(usuario_id, canal);
            """)

    async def obtener_sesion(self, usuario_id: str, canal: str) -> SesionChat | None:
        clave = f"sesion:{canal}:{usuario_id}"

        cached = await self.redis.get(clave)
        if cached:
            return SesionChat(**json.loads(cached))

        async with self.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM sesiones WHERE usuario_id=$1 AND canal=$2 "
                "ORDER BY last_activity DESC LIMIT 1",
                usuario_id, canal
            )
            if row:
                sesion = SesionChat(
                    usuario_id=row["usuario_id"],
                    canal=row["canal"],
                    mensajes=row["mensajes"],
                    created_at=row["created_at"],
                    last_activity=row["last_activity"],
                    metadata=row["metadata"] or {}
                )
                await self.redis.setex(clave, self.ttl_sesion, sesion.model_dump_json())
                return sesion
        return None

    async def guardar_sesion(self, sesion: SesionChat):
        clave = f"sesion:{sesion.canal}:{sesion.usuario_id}"
        sesion.last_activity = datetime.now()

        await self.redis.setex(clave, self.ttl_sesion, sesion.model_dump_json())

        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO sesiones (usuario_id, canal, mensajes, metadata, last_activity)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE SET
                    mensajes = EXCLUDED.mensajes,
                    metadata = EXCLUDED.metadata,
                    last_activity = EXCLUDED.last_activity
            """, sesion.usuario_id, sesion.canal,
                json.dumps(sesion.mensajes), json.dumps(sesion.metadata),
                sesion.last_activity)

    async def cerrar(self):
        if self.redis:
            await self.redis.close()
        if self.pg_pool:
            await self.pg_pool.close()
```

### Proyecto 4.3: Script de despliegue en VPS

```bash
#!/bin/bash
# fase_4/deploy.sh - Script de despliegue en VPS (Ubuntu)

set -euo pipefail

echo "=== Desplegando Agente IA ==="

SERVER_IP="tu_ip_vps"
SERVER_USER="deploy"
PROJECT_DIR="/opt/agente-ia"

# 1. Conectar y preparar servidor
ssh $SERVER_USER@$SERVER_IP << 'REMOTE_COMMANDS'
    # Actualizar sistema
    sudo apt update && sudo apt upgrade -y

    # Instalar Docker si no existe
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com | sh
        sudo usermod -aG docker $USER
    fi

    # Instalar Docker Compose
    if ! command -v docker compose &> /dev/null; then
        sudo apt install -y docker-compose-plugin
    fi

    # Crear directorio del proyecto
    sudo mkdir -p /opt/agente-ia
    sudo chown $USER:$USER /opt/agente-ia
REMOTE_COMMANDS

# 2. Subir archivos
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='.env' \
    ./ $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

# 3. Desplegar
ssh $SERVER_USER@$SERVER_IP << 'REMOTE_COMMANDS'
    cd /opt/agente-ia
    docker compose pull
    docker compose up -d --build
    docker compose ps
    echo "=== Despliegue completado ==="
REMOTE_COMMANDS
```

### Proveedores VPS recomendados (económicos)
| Proveedor | Precio/mes | RAM | Notas |
|-----------|-----------|-----|-------|
| Hetzner | ~$4-7 USD | 2-4GB | Excelente relación calidad/precio |
| DigitalOcean | $6 USD | 1GB | Simple, buen docs |
| Contabo | ~$7 USD | 8GB | Más RAM por el precio |
| Oracle Cloud | GRATIS | 1-4GB | Tier gratuito generoso |
| Railway | $5 USD | Variable | Deploy desde GitHub |

### Recursos Fase 4
- [Docker Docs](https://docs.docker.com/)
- [DigitalOcean Tutorials](https://www.digitalocean.com/community/tutorials)
- [Nginx Config Generator](https://www.digitalocean.com/community/tools/nginx)

---

## FASE 5: Automatización Avanzada (4-5 semanas)

### Objetivos
- Crear workflows multi-agente
- Integrar con n8n/Make para automatizaciones sin código
- Implementar colas de tareas con Celery/Redis
- Conectar con APIs externas (CRM, email, calendarios)

### Proyecto 5.1: Sistema multi-agente coordinado

```python
# fase_5/multi_agente.py
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class EstadoWorkflow(TypedDict):
    messages: Annotated[list, add_messages]
    tarea_original: str
    investigacion: str
    borrador: str
    revision: str
    resultado_final: str

llm_investigador = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
llm_redactor = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
llm_editor = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

def agente_investigador(state: EstadoWorkflow) -> dict:
    """Investiga y recopila información sobre el tema."""
    respuesta = llm_investigador.invoke([
        SystemMessage(content="""Eres un investigador experto. Tu trabajo es:
        1. Analizar el tema solicitado
        2. Identificar los puntos clave a cubrir
        3. Proporcionar datos y estadísticas relevantes
        4. Listar fuentes potenciales
        Sé exhaustivo y estructurado."""),
        HumanMessage(content=f"Investiga sobre: {state['tarea_original']}")
    ])
    return {"investigacion": respuesta.content}

def agente_redactor(state: EstadoWorkflow) -> dict:
    """Redacta el contenido basado en la investigación."""
    respuesta = llm_redactor.invoke([
        SystemMessage(content="""Eres un redactor profesional. 
        Basándote en la investigación proporcionada, escribe un contenido 
        atractivo, bien estructurado y optimizado. Usa un tono profesional 
        pero accesible."""),
        HumanMessage(content=f"Tarea: {state['tarea_original']}\n\n"
                     f"Investigación:\n{state['investigacion']}")
    ])
    return {"borrador": respuesta.content}

def agente_editor(state: EstadoWorkflow) -> dict:
    """Revisa y mejora el borrador."""
    respuesta = llm_editor.invoke([
        SystemMessage(content="""Eres un editor senior. Revisa el borrador y:
        1. Corrige errores gramaticales y de estilo
        2. Mejora la claridad y fluidez
        3. Verifica coherencia con la investigación
        4. Añade mejoras finales
        Devuelve la versión final pulida."""),
        HumanMessage(content=f"Tarea original: {state['tarea_original']}\n\n"
                     f"Borrador a revisar:\n{state['borrador']}")
    ])
    return {"resultado_final": respuesta.content}

# Construir el workflow
workflow = StateGraph(EstadoWorkflow)
workflow.add_node("investigador", agente_investigador)
workflow.add_node("redactor", agente_redactor)
workflow.add_node("editor", agente_editor)

workflow.set_entry_point("investigador")
workflow.add_edge("investigador", "redactor")
workflow.add_edge("redactor", "editor")
workflow.add_edge("editor", END)

pipeline = workflow.compile()

if __name__ == "__main__":
    resultado = pipeline.invoke({
        "messages": [],
        "tarea_original": "Escribe un artículo sobre cómo las PYMEs en Latinoamérica "
                         "pueden usar agentes de IA para automatizar su atención al cliente",
        "investigacion": "",
        "borrador": "",
        "revision": "",
        "resultado_final": ""
    })
    print(resultado["resultado_final"])
```

### Proyecto 5.2: Cola de tareas asíncronas con Celery

```python
# fase_5/tareas_celery.py
from celery import Celery
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "agente_tareas",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=300,
    worker_concurrency=4,
)

openai_client = OpenAI()

@celery_app.task(bind=True, max_retries=3)
def procesar_documento(self, documento_id: str, contenido: str, instrucciones: str):
    """Procesa un documento con IA de forma asíncrona."""
    try:
        respuesta = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": instrucciones},
                {"role": "user", "content": contenido}
            ],
            temperature=0.3
        )
        resultado = respuesta.choices[0].message.content
        return {
            "documento_id": documento_id,
            "resultado": resultado,
            "status": "completado"
        }
    except Exception as e:
        self.retry(countdown=60, exc=e)

@celery_app.task
def enviar_resumen_diario(destinatarios: list[str]):
    """Genera y envía un resumen diario de actividad."""
    # Lógica de generación de resumen + envío
    pass

@celery_app.task
def sincronizar_crm(datos_conversacion: dict):
    """Sincroniza datos de conversación con el CRM."""
    pass

# Ejecutar worker: celery -A tareas_celery worker --loglevel=info
# Ejecutar beat (tareas programadas): celery -A tareas_celery beat
```

### Proyecto 5.3: Integración con n8n (self-hosted)

```yaml
# fase_5/n8n-docker-compose.yml
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - WEBHOOK_URL=https://tu-dominio.com/
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

```python
# fase_5/webhook_n8n.py
"""
Endpoint que n8n puede llamar para procesar mensajes con tu agente.
Flujo en n8n:
  1. Trigger: Webhook (recibe mensaje de WhatsApp/Telegram)
  2. HTTP Request: Llama a este endpoint
  3. Condicional: Si requiere_humano → notificar Slack
  4. HTTP Request: Enviar respuesta al usuario
  5. Google Sheets: Registrar conversación
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class N8NRequest(BaseModel):
    usuario_id: str
    canal: str
    mensaje: str
    metadata: dict = {}

class N8NResponse(BaseModel):
    respuesta: str
    categoria: str
    sentimiento: str
    requiere_humano: bool
    acciones_sugeridas: list[str] = []

@app.post("/n8n/procesar", response_model=N8NResponse)
async def procesar_para_n8n(req: N8NRequest):
    """Endpoint optimizado para workflows de n8n."""
    # Aquí conectas tu agente IA
    # ... (usa tu agente de la Fase 3)
    return N8NResponse(
        respuesta="Respuesta del agente",
        categoria="soporte",
        sentimiento="neutral",
        requiere_humano=False,
        acciones_sugeridas=["crear_ticket", "enviar_email_seguimiento"]
    )
```

### Recursos Fase 5
- [LangGraph Multi-Agent](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [Celery Docs](https://docs.celeryq.dev/)
- [n8n Docs](https://docs.n8n.io/)

---

## FASE 6: Proyecto Integrador + Monetización (4-6 semanas)

### Proyecto Final: SaaS de Atención al Cliente con IA

Un sistema completo que empresas pueden contratar para automatizar su atención al cliente.

### Arquitectura del proyecto final

```
                    ┌─────────────────────────────┐
                    │      Dashboard React         │
                    │  (métricas, config, historial)│
                    └──────────┬──────────────────┘
                               │ API REST
                    ┌──────────▼──────────────────┐
                    │      FastAPI Backend         │
                    │  ┌─────────────────────┐     │
                    │  │  Router Multicanal   │     │
                    │  └──────┬──────────────┘     │
                    │         │                     │
                    │  ┌──────▼──────────────┐     │
                    │  │  Motor de Agentes    │     │
                    │  │  (LangGraph)         │     │
                    │  └──────┬──────────────┘     │
                    │         │                     │
                    │  ┌──────▼──────────────┐     │
                    │  │  RAG + Herramientas  │     │
                    │  └─────────────────────┘     │
                    └──────────┬──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼───┐   ┌───────▼────┐   ┌───────▼────┐
     │ PostgreSQL  │   │   Redis    │   │  Vector DB │
     │ (sesiones,  │   │ (cache,    │   │ (docs del  │
     │  usuarios)  │   │  colas)    │   │  cliente)  │
     └─────────────┘   └────────────┘   └────────────┘
```

### Funcionalidades clave

```
1. Multi-tenant: Cada empresa tiene su propia configuración
2. Base de conocimiento personalizada: RAG con documentos del cliente
3. Multicanal: WhatsApp + Telegram + Widget Web
4. Escalación inteligente: Detecta cuándo pasar a humano
5. Dashboard: Métricas en tiempo real (React + Power BI embebido)
6. Webhooks: Integración con CRM, email, Slack del cliente
7. API pública: Para que clientes integren en sus sistemas
```

### Modelos de monetización

```
Plan Starter:   $29/mes - 500 conversaciones, 1 canal, 1 agente
Plan Business:  $99/mes - 5,000 conversaciones, 3 canales, 5 agentes
Plan Enterprise: $299/mes - ilimitado, API, soporte prioritario

Servicios adicionales:
- Setup personalizado: $200-500 (una vez)
- Entrenamiento de RAG con docs del cliente: $100-300
- Integraciones custom: $50-150/hora
```

---

## Stack Tecnológico Completo

| Capa | Tecnología | Para qué |
|------|-----------|----------|
| **LLMs** | OpenAI GPT-4o-mini, Gemini | Motor de IA principal |
| **Framework Agentes** | LangChain + LangGraph | Orquestación de agentes |
| **Backend** | FastAPI (Python) | API REST, webhooks |
| **Frontend** | React + TypeScript | Dashboard de admin |
| **BD Relacional** | PostgreSQL | Usuarios, sesiones, config |
| **Cache/Colas** | Redis | Sesiones rápidas, pub/sub |
| **Vector DB** | FAISS / Chroma / Pinecone | RAG, búsqueda semántica |
| **Tareas Async** | Celery | Procesamiento en background |
| **Mensajería** | WhatsApp Cloud API, Telegram | Canales de comunicación |
| **Automatización** | n8n (self-hosted) | Workflows sin código |
| **Contenedores** | Docker + Docker Compose | Empaquetado y despliegue |
| **Servidor** | VPS (Hetzner/DO) + Nginx | Hosting en producción |
| **CI/CD** | GitHub Actions | Despliegue automático |
| **Monitoreo** | Sentry + Prometheus + Grafana | Logs, errores, métricas |

---

## Cronograma Sugerido

```
Mes 1:  Fase 0 + Fase 1 (fundamentos + primer agente)
Mes 2:  Fase 2 (integración con WhatsApp y Telegram)
Mes 3:  Fase 3 (LangChain, RAG, agentes con herramientas)
Mes 4:  Fase 4 (Docker, VPS, despliegue)
Mes 5:  Fase 5 (automatización avanzada, multi-agente)
Mes 6:  Fase 6 (proyecto integrador, primeros clientes)

Total: ~6 meses para tener un producto comercializable
```

---

## Recursos de Aprendizaje Continuo

### Cursos recomendados (gratuitos o económicos)
- [DeepLearning.AI - ChatGPT Prompt Engineering](https://www.deeplearning.ai/short-courses/)
- [DeepLearning.AI - LangChain for LLM Application Development](https://www.deeplearning.ai/short-courses/)
- [DeepLearning.AI - Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/short-courses/)
- [FreeCodeCamp - Docker Full Course](https://www.youtube.com/watch?v=fqMOX6JJhGo)

### Comunidades
- r/LangChain (Reddit)
- LangChain Discord
- Hugging Face Community
- AI Engineers (Twitter/X)

### Newsletters
- The Batch (Andrew Ng)
- AI Tidbits
- Superhuman AI

---

## Siguiente Paso Inmediato

> **Comienza por la Fase 0, Proyecto 0.1:**
> 1. Crea tu cuenta en OpenAI Platform
> 2. Genera tu API key
> 3. Crea el archivo `.env` con tu key
> 4. Ejecuta `primer_llm.py`
> 5. Experimenta cambiando el system prompt y la temperature
