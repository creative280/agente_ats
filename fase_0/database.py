"""
Módulo de conexión a base de datos para el agente IA.

Soporta: SQL Server, MySQL, PostgreSQL, SQLite.
Funciones: descubrimiento automático de esquema, ejecución segura (solo lectura).
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path, override=True)


def crear_engine() -> Engine:
    """Crea la conexión a la BD usando la variable DATABASE_URL del .env."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL no configurada en .env\n"
            "Ejemplos:\n"
            "  SQL Server: mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server\n"
            "  MySQL:      mysql+pymysql://user:pass@server:3306/db\n"
            "  PostgreSQL: postgresql://user:pass@server:5432/db\n"
            "  SQLite:     sqlite:///ruta/archivo.db"
        )
    return create_engine(url, pool_pre_ping=True, pool_size=5)


def listar_tablas(engine: Engine, esquemas: list[str] | None = None) -> list[str]:
    """Retorna la lista de nombres de tablas de la BD."""
    inspector = inspect(engine)
    schema_list = esquemas or [None]
    todas = []
    for schema in schema_list:
        tablas = inspector.get_table_names(schema=schema)
        prefix = f"{schema}." if schema else ""
        todas.extend(f"{prefix}{t}" for t in tablas)
    return todas


def obtener_esquema(engine: Engine, esquemas: list[str] | None = None,
                    solo_tablas: list[str] | None = None) -> str:
    """
    Lee tablas, columnas y tipos de la BD.
    Si solo_tablas se proporciona, solo incluye esas tablas (mucho más rápido).
    """
    inspector = inspect(engine)
    schema_list = esquemas or [None]
    lineas = []

    for schema in schema_list:
        tablas = inspector.get_table_names(schema=schema)
        prefix = f"{schema}." if schema else ""

        for tabla in tablas:
            nombre_completo = f"{prefix}{tabla}"
            if solo_tablas and nombre_completo not in solo_tablas and tabla not in solo_tablas:
                continue

            columnas = inspector.get_columns(tabla, schema=schema)
            pk = inspector.get_pk_constraint(tabla, schema=schema)
            pk_cols = pk.get("constrained_columns", []) if pk else []

            cols_info = []
            for col in columnas:
                tipo = str(col["type"])
                nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
                is_pk = " PK" if col["name"] in pk_cols else ""
                cols_info.append(f"    {col['name']} {tipo} {nullable}{is_pk}")

            lineas.append(f"TABLA: {nombre_completo}")
            lineas.append("\n".join(cols_info))
            lineas.append("")

    return "\n".join(lineas)


def obtener_muestra(engine: Engine, tabla: str, limite: int = 3) -> list[dict]:
    """Obtiene una muestra de filas de una tabla (para dar contexto al agente)."""
    nombre_limpio = re.sub(r"[^a-zA-Z0-9_.\[\]]", "", tabla)
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT TOP {limite} * FROM {nombre_limpio}"))
        columnas = list(result.keys())
        return [dict(zip(columnas, row)) for row in result.fetchall()]


def ejecutar_consulta(engine: Engine, sql: str) -> dict:
    """
    Ejecuta una consulta SQL de solo lectura.
    Bloquea INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, EXEC.
    Retorna las filas como lista de diccionarios.
    """
    sql_upper = sql.strip().upper()

    operaciones_prohibidas = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
        "TRUNCATE", "EXEC", "EXECUTE", "CREATE", "GRANT", "REVOKE",
    ]
    for op in operaciones_prohibidas:
        if re.search(rf"\b{op}\b", sql_upper):
            return {
                "error": f"Operación '{op}' no permitida. Solo se permiten consultas de lectura (SELECT).",
                "filas": [],
                "total": 0,
            }

    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
        return {
            "error": "Solo se permiten consultas SELECT o WITH (CTEs).",
            "filas": [],
            "total": 0,
        }

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columnas = list(result.keys())
            filas = [dict(zip(columnas, row)) for row in result.fetchmany(500)]
            total = len(filas)

            return {
                "columnas": columnas,
                "filas": filas,
                "total": total,
                "nota": "Limitado a 500 filas" if total == 500 else None,
            }
    except Exception as e:
        return {"error": str(e), "filas": [], "total": 0}


def test_conexion(engine: Engine) -> dict:
    """Prueba la conexión y retorna info básica."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        return {
            "status": "conectado",
            "tipo_bd": engine.dialect.name,
            "total_tablas": len(tablas),
            "tablas": tablas[:20],
        }
    except Exception as e:
        return {"status": "error", "detalle": str(e)}


if __name__ == "__main__":
    engine = crear_engine()
    info = test_conexion(engine)
    print("=== Test de conexión ===")
    for k, v in info.items():
        print(f"  {k}: {v}")

    if info["status"] == "conectado":
        print("\n=== Esquema de la BD ===")
        print(obtener_esquema(engine))
