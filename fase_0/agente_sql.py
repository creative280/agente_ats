"""
Agente SQL: convierte preguntas en español a consultas SQL,
las ejecuta contra la BD y analiza los resultados.

Flujo de dos pasos para no exceder el límite de tokens de Groq (12k TPM):
  1. Un modelo rápido (8b) recibe solo nombres de tablas y elige las relevantes
  2. El modelo principal recibe esquema detallado solo de esas tablas (~5)
"""

import os
import re
import json
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from database import (
    crear_engine, listar_tablas, obtener_esquema,
    ejecutar_consulta, test_conexion,
)

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path, override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODELO = "llama-3.3-70b-versatile"
MODELO_SELECTOR = "llama-3.1-8b-instant"

MAX_TABLAS_DETALLE = 5
MAX_FILAS_RESULTADO = 20
MAX_HISTORIAL = 6

_CONTEXTO_PATH = Path(__file__).resolve().parent / "bd_contexto.json"


def _cargar_contexto() -> dict:
    if _CONTEXTO_PATH.exists():
        try:
            return json.loads(_CONTEXTO_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _contexto_para_selector(ctx: dict, tablas: list[str]) -> str:
    """Genera lista de tablas enriquecida con descripciones del contexto."""
    desc_tablas = ctx.get("tablas", {})
    partes = []
    for t in tablas:
        desc = desc_tablas.get(t, {}).get("descripcion", "")
        partes.append(f"{t}: {desc}" if desc else t)
    return ", ".join(partes)


def _contexto_para_sql(ctx: dict) -> str:
    """Genera el bloque de contexto de negocio + ejemplos SQL para el prompt."""
    bloques = []

    desc = ctx.get("descripcion_bd", "")
    if desc:
        bloques.append(f"BD: {desc}")

    reglas = ctx.get("reglas_negocio", [])
    if reglas:
        bloques.append("REGLAS: " + " | ".join(reglas))

    ejemplos = ctx.get("ejemplos_sql", [])
    if ejemplos:
        ej_texto = []
        for ej in ejemplos[:5]:
            ej_texto.append(f"P: {ej['pregunta']}\nSQL: {ej['sql']}")
        bloques.append("EJEMPLOS:\n" + "\n".join(ej_texto))

    return "\n".join(bloques)


def _prompt_selector(tablas_desc: str, tipo_bd: str) -> str:
    return (
        f"BD {tipo_bd}. Tablas: {tablas_desc}\n"
        f"Responde SOLO nombres (máx {MAX_TABLAS_DETALLE}) separados por coma.\n"
        f"Si es pregunta general sobre la BD: __GENERAL__"
    )


def _prompt_sql(esquema_bd: str, tipo_bd: str, contexto_negocio: str) -> str:
    base = (
        f"Analista de datos. BD {tipo_bd}. Responde en español.\n"
        f"ESQUEMA:\n{esquema_bd}\n"
        f"SQL en ```sql...```. Solo SELECT/WITH. LIMIT 100."
    )
    if contexto_negocio:
        base = f"{contexto_negocio}\n\n{base}"
    return base


def _extraer_sql(texto: str) -> str | None:
    match = re.search(r"```sql\s*(.*?)\s*```", texto, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def _seleccionar_tablas(pregunta: str, todas: list[str], tipo_bd: str, ctx: dict) -> list[str] | None:
    """Paso 1: modelo rápido elige tablas relevantes. Retorna None si es pregunta general."""
    if len(todas) <= MAX_TABLAS_DETALLE:
        return todas

    tablas_desc = _contexto_para_selector(ctx, todas)
    resp = client.chat.completions.create(
        model=MODELO_SELECTOR,
        messages=[
            {"role": "system", "content": _prompt_selector(tablas_desc, tipo_bd)},
            {"role": "user", "content": pregunta},
        ],
        temperature=0,
        max_tokens=200,
    )
    texto = resp.choices[0].message.content.strip()

    if "__GENERAL__" in texto or "__TODAS__" in texto:
        return None

    candidatas = [t.strip().strip("`'\"") for t in texto.split(",")]
    validas = [t for t in candidatas if t in todas]
    return validas[:MAX_TABLAS_DETALLE] if validas else todas[:MAX_TABLAS_DETALLE]


def _respuesta_general(tablas: list[str], tipo_bd: str, pregunta: str) -> str:
    """Responde preguntas generales sobre la BD sin cargar esquemas pesados."""
    lista = "\n".join(f"- {t}" for t in tablas)
    resp = client.chat.completions.create(
        model=MODELO_SELECTOR,
        messages=[
            {"role": "system", "content": f"Analista de datos. BD {tipo_bd} con {len(tablas)} tablas. Responde en español."},
            {"role": "user", "content": f"Tablas disponibles:\n{lista}\n\nPregunta: {pregunta}"},
        ],
        temperature=0.5,
        max_tokens=1000,
    )
    return resp.choices[0].message.content


class AgenteBD:
    """Agente que conecta lenguaje natural con la base de datos."""

    def __init__(self):
        self.engine = crear_engine()
        info = test_conexion(self.engine)
        if info["status"] != "conectado":
            raise ConnectionError(f"No se pudo conectar a la BD: {info.get('detalle')}")

        self.tipo_bd = info["tipo_bd"]
        self.tablas = listar_tablas(self.engine)
        self.ctx = _cargar_contexto()
        self.historial: list[dict] = []

        print(f"[AgenteBD] Conectado a {self.tipo_bd} | {len(self.tablas)} tablas")
        if self.ctx.get("tablas"):
            print(f"[AgenteBD] Contexto cargado: {len(self.ctx['tablas'])} tablas descritas, "
                  f"{len(self.ctx.get('ejemplos_sql', []))} ejemplos SQL")

    def recargar_contexto(self):
        """Recarga bd_contexto.json sin reiniciar el servidor."""
        self.ctx = _cargar_contexto()

    def _esquema_para(self, pregunta: str) -> tuple[str | None, bool]:
        tablas_sel = _seleccionar_tablas(pregunta, self.tablas, self.tipo_bd, self.ctx)
        if tablas_sel is None:
            return None, True
        print(f"[AgenteBD] Tablas seleccionadas: {tablas_sel}")
        return obtener_esquema(self.engine, solo_tablas=tablas_sel), False

    def _system_msg(self, esquema: str) -> dict:
        ctx_negocio = _contexto_para_sql(self.ctx)
        return {"role": "system", "content": _prompt_sql(esquema, self.tipo_bd, ctx_negocio)}

    def _ejecutar_con_retry(self, sql: str, system_msg: dict) -> tuple[dict, str]:
        resultado = ejecutar_consulta(self.engine, sql)
        if not resultado.get("error"):
            return resultado, sql

        mensajes = [
            system_msg,
            {"role": "user", "content": f"Error al ejecutar: {resultado['error']}\nCorrige la SQL para {self.tipo_bd}."},
        ]
        resp = client.chat.completions.create(
            model=MODELO, messages=mensajes, temperature=0.3, max_tokens=1500,
        )
        sql_retry = _extraer_sql(resp.choices[0].message.content)
        if sql_retry:
            resultado = ejecutar_consulta(self.engine, sql_retry)
            return resultado, sql_retry
        return resultado, sql

    def consultar(self, pregunta: str) -> str:
        esquema, es_general = self._esquema_para(pregunta)
        if es_general:
            return _respuesta_general(self.tablas, self.tipo_bd, pregunta)

        system_msg = self._system_msg(esquema)
        self.historial.append({"role": "user", "content": pregunta})
        mensajes = [system_msg] + self.historial[-MAX_HISTORIAL:]

        resp = client.chat.completions.create(
            model=MODELO, messages=mensajes, temperature=0.3, max_tokens=1500,
        )
        texto_ia = resp.choices[0].message.content
        self.historial.append({"role": "assistant", "content": texto_ia})

        sql = _extraer_sql(texto_ia)
        if not sql:
            return texto_ia

        print(f"[SQL] {sql}")
        resultado, sql_final = self._ejecutar_con_retry(sql, system_msg)

        if resultado.get("error"):
            return f"No pude ejecutar la consulta.\n\nError: {resultado['error']}\n\n```sql\n{sql_final}\n```"

        datos_str = json.dumps(resultado["filas"][:MAX_FILAS_RESULTADO], default=str, ensure_ascii=False, indent=2)
        contexto = (
            f"Resultados ({resultado['total']} filas):\n"
            f"Columnas: {resultado.get('columnas', [])}\n{datos_str}"
        )

        mensajes_analisis = [
            system_msg,
            {"role": "user", "content": f"{pregunta}\n\n{contexto}\n\nAnaliza brevemente en español."},
        ]
        resp_a = client.chat.completions.create(
            model=MODELO, messages=mensajes_analisis, temperature=0.5, max_tokens=1500,
        )
        analisis = resp_a.choices[0].message.content
        self.historial.append({"role": "assistant", "content": analisis})
        return analisis

    def consultar_stream(self, pregunta: str):
        yield "**Identificando tablas relevantes...**\n\n"

        esquema, es_general = self._esquema_para(pregunta)
        if es_general:
            resp = _respuesta_general(self.tablas, self.tipo_bd, pregunta)
            yield resp
            return

        system_msg = self._system_msg(esquema)
        self.historial.append({"role": "user", "content": pregunta})
        mensajes = [system_msg] + self.historial[-MAX_HISTORIAL:]

        resp = client.chat.completions.create(
            model=MODELO, messages=mensajes, temperature=0.3, max_tokens=1500,
        )
        texto_ia = resp.choices[0].message.content
        self.historial.append({"role": "assistant", "content": texto_ia})

        sql = _extraer_sql(texto_ia)
        if not sql:
            yield from texto_ia
            return

        yield f"**Consultando base de datos...**\n\n```sql\n{sql}\n```\n\n"
        resultado, sql_final = self._ejecutar_con_retry(sql, system_msg)

        if resultado.get("error"):
            yield f"No pude completar la consulta: {resultado['error']}"
            return

        yield f"**{resultado['total']} filas encontradas.** Analizando...\n\n"

        datos_str = json.dumps(resultado["filas"][:MAX_FILAS_RESULTADO], default=str, ensure_ascii=False, indent=2)
        contexto = (
            f"Resultados ({resultado['total']} filas):\n"
            f"Columnas: {resultado.get('columnas', [])}\n{datos_str}"
        )

        mensajes_analisis = [
            system_msg,
            {"role": "user", "content": f"{pregunta}\n\n{contexto}\n\nAnaliza brevemente en español."},
        ]
        stream = client.chat.completions.create(
            model=MODELO, messages=mensajes_analisis,
            temperature=0.5, max_tokens=1500, stream=True,
        )

        texto_completo = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                texto_completo += delta
                yield delta

        self.historial.append({"role": "assistant", "content": texto_completo})

    def reset(self):
        self.historial = []


if __name__ == "__main__":
    agente = AgenteBD()
    print("\nChat con tu base de datos (escribe 'salir' para terminar)\n")
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() == "salir":
            break
        print(f"\nAgente: {agente.consultar(pregunta)}\n")
