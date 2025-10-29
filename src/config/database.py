from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

# 🔹 Cargar variables de entorno desde .env (si existe)
load_dotenv()

# 🔹 Variables de conexión PostgreSQL
PG_USER = os.getenv("PG_USER", "kalito")
PG_PASSWORD = os.getenv("PG_PASSWORD", "kalito123")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "landing")

# 🔹 Bandera para pipelines o entornos sin base real
SKIP_DB = os.getenv("SQLALCHEMY_SKIP_DB", "false").lower() == "true"

# ==============================
# ✅ Cambiar driver: psycopg (no psycopg2)
# ==============================
if PG_PASSWORD:
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )
else:
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg://{PG_USER}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )

# ==============================
# 🔧 Crear motor y sesión
# ==============================
if not SKIP_DB:
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, future=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
    except Exception as e:
        print(f"⚠️ [SQLAlchemy] Error al conectar a PostgreSQL: {e}", file=sys.stderr)
        engine = None
        SessionLocal = None
        Base = declarative_base()
else:
    print("⚙️ [SQLAlchemy] Conexión a base de datos deshabilitada (modo CI o skip).")
    engine = None
    SessionLocal = None
    Base = declarative_base()


def get_db():
    """Crea una sesión de base de datos y la cierra al finalizar"""
    if SessionLocal is None:
        raise RuntimeError("Base de datos no inicializada o deshabilitada.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
