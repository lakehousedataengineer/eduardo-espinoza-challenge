import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.config.database import SessionLocal, Base, engine
from src.models.models import Department, Job, HiredEmployee
from datetime import datetime

client = TestClient(app)
pytestmark = pytest.mark.tdd


@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    """Crea tablas e inserta datos mínimos para las pruebas de queries."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Limpiar tablas
    db.query(HiredEmployee).delete()
    db.query(Job).delete()
    db.query(Department).delete()

    # Crear datos de prueba
    departments = [
        Department(id=1, department="Staff"),
        Department(id=2, department="Engineering"),
        Department(id=3, department="Support")
    ]
    jobs = [
        Job(id=1, job="Manager"),
        Job(id=2, job="Analyst"),
        Job(id=3, job="Recruiter")
    ]
    employees = [
        HiredEmployee(id=1, name="Alice", datetime=datetime(2021, 1, 5), department_id=1, job_id=3),
        HiredEmployee(id=2, name="Bob", datetime=datetime(2021, 4, 22), department_id=1, job_id=2),
        HiredEmployee(id=3, name="Charlie", datetime=datetime(2021, 7, 10), department_id=2, job_id=1),
        HiredEmployee(id=4, name="Diana", datetime=datetime(2021, 10, 18), department_id=3, job_id=1),
        HiredEmployee(id=5, name="Eve", datetime=datetime(2021, 2, 20), department_id=1, job_id=3),
    ]

    db.add_all(departments + jobs + employees)
    db.commit()
    db.close()
    yield
    # Teardown al finalizar tests
    Base.metadata.drop_all(bind=engine)


def test_query_hired_by_quarter():
    """✅ Test: Endpoint /api/queries/hired-by-quarter/"""
    response = client.get("/api/queries/hired-by-quarter/")
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert isinstance(data["rows"], list)
    if len(data["rows"]) > 0:
        sample = data["rows"][0]
        assert "department" in sample
        assert "job" in sample
        assert all(q in sample for q in ["Q1", "Q2", "Q3", "Q4"])


def test_query_departments_above_mean():
    """✅ Test: Endpoint /api/queries/above-mean/"""
    response = client.get("/api/queries/above-mean/")
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert isinstance(data["rows"], list)

    # Si hay resultados, validar campos
    if len(data["rows"]) > 0:
        sample = data["rows"][0]
        assert "id" in sample
        assert "department" in sample
        assert "hired" in sample
