import pytest
from sqlalchemy import text
from src.config.database import SessionLocal, Base, engine
from src.models.models import Department, Job, HiredEmployee


# ⚙️ Crear tablas automáticamente antes de los tests (solo si engine existe)
if engine is not None:
    Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    """
    🔥 Limpia las tablas antes de cada test (PostgreSQL).
    Se asegura de que las tablas existan antes de truncarlas.
    """
    if engine is None or SessionLocal is None:
        pytest.skip("⏭️ Base de datos no inicializada (modo CI skip).")

    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        # ✅ PostgreSQL requiere TRUNCATE CASCADE para limpiar FKs correctamente
        db.execute(text("TRUNCATE TABLE hired_employees RESTART IDENTITY CASCADE;"))
        db.execute(text("TRUNCATE TABLE jobs RESTART IDENTITY CASCADE;"))
        db.execute(text("TRUNCATE TABLE departments RESTART IDENTITY CASCADE;"))
        db.commit()
    finally:
        db.close()


@pytest.fixture
def seed_base_data():
    """
    🌱 Inserta datos base antes de hired_employees para respetar FK.
    """
    if engine is None or SessionLocal is None:
        pytest.skip("⏭️ Base de datos no inicializada (modo CI skip).")

    db = SessionLocal()
    try:
        departments = [Department(id=i, department=f"Dept {i}") for i in range(1, 11)]
        jobs = [Job(id=i, job=f"Job {i}") for i in range(1, 11)]
        db.bulk_save_objects(departments + jobs)
        db.commit()
    finally:
        db.close()
