# Agente ATS - Plataforma de Agentes IA

> Sistema de agentes de inteligencia artificial con chat conversacional, análisis de bases de datos mediante lenguaje natural y API REST.

---

## Descripción

**Agente ATS** es un proyecto modular de agentes IA diseñado para evolucionar en fases, desde fundamentos de IA generativa hasta un SaaS completo con integración multicanal (WhatsApp, Telegram) y automatización avanzada.

### Estado Actual: Fase 0 - Fundamentos + Agente SQL

La Fase 0 implementa:

- **Chat conversacional** con múltiples personalidades (asistente, analista, coach, programador)
- **Agente SQL** que convierte preguntas en español a consultas SQL, las ejecuta y analiza resultados
- **API REST** con FastAPI, incluyendo streaming en tiempo real
- **Interfaz web** moderna con tema oscuro
- **Panel de configuración** para contexto de negocio de la base de datos

---

## Estructura del Proyecto

```
agente_ats/
├── README.md                   # Este archivo
├── ROADMAP.md                  # Plan de desarrollo por fases
├── CHANGELOG.md                # Historial de cambios
├── requirements.txt            # Dependencias Python
├── .env.example                # Plantilla de variables de entorno
├── .gitignore                  # Archivos excluidos de git
│
├── docs/                       # Documentación técnica
│   └── arquitectura.md         # Arquitectura y decisiones técnicas
│
└── fase_0/                     # Fase 0: Fundamentos + Agente SQL
    ├── app.py                  # API FastAPI (servidor principal)
    ├── agente_sql.py           # Agente de consultas SQL con LLM
    ├── database.py             # Conexión y operaciones con BD
    ├── primer_llm.py           # Script: primer llamado a LLM
    ├── prompt_engineering.py   # Script: prompt engineering
    ├── streaming_costos.py     # Script: streaming y costos
    ├── index.html              # Interfaz principal del chat
    ├── bd_config.html          # Panel de configuración de BD
    └── bd_contexto.json        # Contexto de negocio para el agente SQL
```

---

## Requisitos Previos

- **Python 3.11+**
- **Cuenta en Groq** (gratuita) para API key: [console.groq.com](https://console.groq.com)
- **Base de datos** (opcional): SQL Server, MySQL, PostgreSQL o SQLite

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd agente_ats
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y agrega tu API key de Groq:

```env
GROQ_API_KEY=gsk_tu-key-aqui
```

Para habilitar el agente SQL, agrega también:

```env
DATABASE_URL=mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server
```

---

## Uso

### Iniciar el servidor

```bash
cd fase_0
uvicorn app:app --reload --port 8000
```

En Windows, también puedes iniciar con limpieza automática del puerto (cierra procesos previos que estén usando el puerto antes de arrancar):

```powershell
cd fase_0
.\start_server.ps1 -Port 8000
```

Si quieres auto-recarga durante desarrollo:

```powershell
.\start_server.ps1 -Port 8000 -Reload
```

### Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Interfaz web del chat |
| `POST` | `/chat` | Enviar mensaje (respuesta completa) |
| `POST` | `/chat/stream` | Enviar mensaje (respuesta en streaming) |
| `POST` | `/reset` | Reiniciar sesión de chat |
| `GET` | `/personalidades` | Listar personalidades disponibles |
| `GET` | `/bd/status` | Estado de conexión a la BD |
| `GET` | `/bd/esquema` | Esquema completo de la BD |
| `GET` | `/bd/base` | Ver nombre de BD actual (de `DATABASE_URL`) |
| `GET` | `/bd/bases` | Listar bases disponibles para el usuario actual |
| `POST` | `/bd/base` | Cambiar solo nombre de BD y reconectar agente |
| `GET` | `/bd/config` | Panel de configuración de BD |
| `GET` | `/bd/contexto` | Obtener contexto de negocio |
| `POST` | `/bd/contexto` | Guardar contexto de negocio |

### Documentación interactiva de la API

Una vez iniciado el servidor:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Scripts de aprendizaje

```bash
cd fase_0

# Primer llamado a un LLM
python primer_llm.py

# Prompt engineering aplicado
python prompt_engineering.py

# Streaming y métricas de uso
python streaming_costos.py
```

---

## Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|-----------|-----------|
| LLM | Groq (Llama 3.3 70B) | Motor de IA principal (tier gratuito) |
| LLM Selector | Groq (Llama 3.1 8B) | Selección rápida de tablas |
| Backend | FastAPI | API REST + streaming |
| ORM | SQLAlchemy | Conexión multi-BD |
| Frontend | HTML/CSS/JS vanilla | Interfaz de chat |
| Config | python-dotenv | Variables de entorno |

---

## Configuración del Agente SQL

El agente SQL puede conectarse a cualquier base de datos soportada por SQLAlchemy. Para mejorar la precisión de las consultas:

1. Inicia el servidor y navega a `/bd/config`
2. Describe las tablas principales de tu BD
3. Agrega ejemplos de consultas SQL frecuentes
4. Define reglas de negocio (convenciones de estados, formatos, etc.)

Esta configuración se guarda en `fase_0/bd_contexto.json` y se inyecta automáticamente en el prompt del agente.

---

## Roadmap

Consulta [ROADMAP.md](ROADMAP.md) para el plan completo de desarrollo. Resumen de fases:

| Fase | Descripción | Estado |
|------|------------|--------|
| **Fase 0** | Fundamentos IA + Agente SQL | Completada |
| Fase 1 | Agente Conversacional Avanzado | Pendiente |
| Fase 2 | Integración WhatsApp/Telegram | Pendiente |
| Fase 3 | LangChain/LangGraph + RAG | Pendiente |
| Fase 4 | Docker + VPS + CI/CD | Pendiente |
| Fase 5 | Multi-agente + n8n + Celery | Pendiente |
| Fase 6 | SaaS Integrador + Monetización | Pendiente |

---

## Licencia

Este proyecto está bajo la Licencia MIT.
