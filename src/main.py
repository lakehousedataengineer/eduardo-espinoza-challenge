from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import ingest, queries
from src.utils.logger import get_logger
from src.config.database import Base, engine

logger = get_logger(__name__)

# 🚀 Crear app FastAPI
app = FastAPI(
    title="Globant Challenge API",
    description="Ingesta y procesamiento de CSVs (departments, jobs, hired_employees) + Consultas SQL",
    version="1.0.0"
)

# 🌐 Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ En producción: reemplazar por el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Registrar routers
app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingest"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])

# 🔹 Evento de inicio de la aplicación
@app.on_event("startup")
def init_database():
    """
    Crea las tablas en la base de datos si no existen.
    Este evento se ejecuta automáticamente al iniciar la app.
    """
    logger.info("🗄️ Creando tablas en la base de datos si no existen...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas listas en la base de datos.")
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        raise e

# 🔹 Endpoint de salud
@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica el estado general de la API."""
    logger.info("✅ Health check OK")
    return {"status": "ok", "message": "API is running"}

# 🔹 Mensaje de inicio
@app.on_event("startup")
def log_startup():
    logger.info("🚀 FastAPI app iniciada correctamente.")
