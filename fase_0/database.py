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
from sqlalchemy.engine import Engine, make_url

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


def cambiar_nombre_bd_en_url(database_url: str, nombre_bd: str) -> str:
    """
    Retorna un DATABASE_URL nuevo cambiando solo el nombre de la base de datos.
    Mantiene usuario, password, host, puerto y query params.
    """
    if not database_url:
        raise ValueError("DATABASE_URL vacía.")
    if not nombre_bd or not nombre_bd.strip():
        raise ValueError("El nombre de la base de datos no puede estar vacío.")

    nombre_bd = nombre_bd.strip()
    if not re.fullmatch(r"[a-zA-Z0-9_\-\.]+", nombre_bd):
        raise ValueError("Nombre de base de datos inválido. Usa letras, números, guion, guion bajo o punto.")

    try:
        url = make_url(database_url)
        nueva_url = url.set(database=nombre_bd)
        return nueva_url.render_as_string(hide_password=False)
    except Exception as e:
        raise ValueError(f"No se pudo construir la nueva URL de conexión: {e}") from e


def listar_bases_disponibles(database_url: str) -> list[str]:
    """
    Lista las bases disponibles para el usuario actual en la instancia.
    Intenta conectarse con el mismo usuario/host pero en una BD de sistema
    según el motor para consultar el catálogo.
    """
    if not database_url:
        raise ValueError("DATABASE_URL vacía.")

    url = make_url(database_url)
    driver = (url.drivername or "").lower()
    backend = driver.split("+", 1)[0]

    if backend == "sqlite":
        return [url.database] if url.database else []

    # En MySQL administrado, abrir sesión sin DB puede fallar aunque la DB actual sí sea accesible.
    # Por eso se intenta primero con la URL original y luego con DBs de catálogo.
    candidatos_url = [url]
    if backend in {"postgresql", "postgres"}:
        candidatos_url.append(url.set(database="postgres"))
    elif backend in {"mssql"}:
        candidatos_url.append(url.set(database="master"))

    if backend in {"mysql", "mariadb"}:
        consultas = [
            "SELECT DISTINCT table_schema FROM information_schema.tables ORDER BY table_schema",
            "SHOW DATABASES",
            "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name",
            "SELECT DATABASE()",
        ]
    elif backend in {"postgresql", "postgres"}:
        consultas = [
            "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname",
            "SELECT current_database()",
        ]
    elif backend == "mssql":
        consultas = [
            "SELECT name FROM sys.databases ORDER BY name",
            "SELECT DB_NAME()",
        ]
    else:
        consultas = [
            "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name",
        ]

    bases: set[str] = set()
    ultimo_error = None
    for url_candidato in candidatos_url:
        engine_catalogo = create_engine(
            url_candidato.render_as_string(hide_password=False),
            pool_pre_ping=True,
            pool_size=2,
        )
        try:
            with engine_catalogo.connect() as conn:
                for q in consultas:
                    try:
                        filas = conn.execute(text(q)).fetchall()
                        for row in filas:
                            valor = row[0] if row else None
                            if valor:
                                bases.add(str(valor))
                        if bases:
                            break
                    except Exception as e:
                        ultimo_error = e
                if bases:
                    break
        except Exception as e:
            ultimo_error = e
        finally:
            engine_catalogo.dispose()

    if url.database:
        bases.add(url.database)

    if not bases and ultimo_error is not None:
        raise ultimo_error

    return sorted(b for b in bases if b)


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
