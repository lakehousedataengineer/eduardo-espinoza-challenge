import io
import tempfile
import textwrap
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.config.database import Base, engine
from src.tests.utils_csv_generator import (
    generate_hired_csv,
    generate_departments_csv,
    generate_jobs_csv
)

client = TestClient(app)
pytestmark = pytest.mark.tdd


@pytest.fixture(scope="module")
def setup_csv_files(tmp_path_factory):
    """Prepara CSVs temporales para los tests."""
    base_dir = tmp_path_factory.mktemp("data")
    hired_path = base_dir / "hired_employees.csv"
    departments_path = base_dir / "departments.csv"
    jobs_path = base_dir / "jobs.csv"

    generate_departments_csv(departments_path, rows=5)
    generate_jobs_csv(jobs_path, rows=5)
    generate_hired_csv(hired_path, rows=1000, valid=True)

    return {
        "hired": hired_path,
        "departments": departments_path,
        "jobs": jobs_path
    }


# ============================================================
# ✅ TESTS DE INGESTA EXITOSA
# ============================================================

def test_upload_departments(setup_csv_files):
    """✅ Test: subida exitosa de departments.csv"""
    with open(setup_csv_files["departments"], "rb") as f:
        response = client.post(
            "/api/ingest/upload/",
            data={"type": "departments"},
            files={"file": ("departments.csv", f, "text/csv")}
        )

    data = response.json()
    assert response.status_code == 200
    assert "departments" in data["table"]
    assert data["inserted"] > 0
    assert any(word in data["message"].lower() for word in [
        "procesamiento", "insertadas", "válidas"
    ])


def test_upload_jobs(setup_csv_files):
    """✅ Test: subida exitosa de jobs.csv"""
    with open(setup_csv_files["jobs"], "rb") as f:
        response = client.post(
            "/api/ingest/upload/",
            data={"type": "jobs"},
            files={"file": ("jobs.csv", f, "text/csv")}
        )

    data = response.json()
    assert response.status_code == 200
    assert "jobs" in data["table"]
    assert data["inserted"] > 0
    assert any(word in data["message"].lower() for word in [
        "procesamiento", "insertadas", "válidas"
    ])


def test_upload_hired_employees_batch(setup_csv_files, seed_base_data):
    """✅ Test: subida exitosa de hired_employees.csv con batches de 1000"""
    with open(setup_csv_files["hired"], "rb") as f:
        response = client.post(
            "/api/ingest/upload/",
            data={"type": "hired_employees"},
            files={"file": ("hired_employees.csv", f, "text/csv")}
        )

    data = response.json()
    assert response.status_code == 200
    assert "hired_employees" in data["table"]
    assert data["inserted"] > 0
    assert "procesadas" in data["message"].lower() or "insertadas" in data["message"].lower()
    assert data["invalid_rows"] >= 0
    assert data["duplicates"] >= 0


# ============================================================
# ❌ TESTS DE VALIDACIÓN DE ERRORES
# ============================================================

def test_upload_invalid_file_type():
    """❌ Test: archivo no CSV"""
    fake_file = io.BytesIO(b"some text data")
    response = client.post(
        "/api/ingest/upload/",
        data={"type": "departments"},
        files={"file": ("departments.txt", fake_file, "text/plain")}
    )
    assert response.status_code == 400
    assert "Solo se permiten archivos CSV" in response.json()["detail"]


def test_upload_invalid_table_type():
    """❌ Test: tipo de tabla inválido"""
    fake_file = io.BytesIO(b"id,name\n1,Test")
    response = client.post(
        "/api/ingest/upload/",
        data={"type": "invalid_table"},
        files={"file": ("random_file.csv", fake_file, "text/csv")}
    )
    assert response.status_code == 400
    assert "Tipo inválido" in response.json()["detail"]


# ============================================================
# 🧪 TESTS DE DUPLICADOS
# ============================================================

def test_upload_hired_employees_with_duplicates(tmp_path):
    """✅ Test: inserta CSV con duplicados y verifica detección."""
    from src.tests.utils_csv_generator import generate_hired_csv

    path = tmp_path / "hired_employees_duplicates.csv"
    generate_hired_csv(path, rows=50, valid=True, duplicate=True)

    with open(path, "rb") as f:
        response = client.post(
            "/api/ingest/upload/",
            data={"type": "hired_employees"},
            files={"file": ("hired_employees.csv", f, "text/csv")}
        )

    data = response.json()
    assert response.status_code == 200
    assert data["duplicates"] > 0
    assert "duplicadas" in data["message"] or "duplicados" in data["message"]


# ============================================================
# 🧩 NUEVO TEST: CLAVES FORÁNEAS INVÁLIDAS
# ============================================================

def test_upload_hired_employees_with_invalid_fk():
    """
    ✅ Test: hired_employees con claves foráneas inválidas.
    Debe generar registros rechazados por FK y devolver un resumen detallado.
    """
    # Crear CSV con department_id y job_id inexistentes
    csv_content = textwrap.dedent("""\
        id,name,datetime,department_id,job_id
        1,John Doe,2024-01-10T10:00:00Z,999,999
        2,Jane Smith,2024-02-05T09:00:00Z,123,888
        3,Mark Test,2024-03-01T12:00:00Z,1000,1000
    """)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as tmp:
        tmp.write(csv_content)
        tmp_path = tmp.name

    # Subir CSV
    with open(tmp_path, "rb") as f:
        response = client.post(
            "/api/ingest/upload/",
            data={"type": "hired_employees"},
            files={"file": ("hired_employees_invalid_fk.csv", f, "text/csv")}
        )

    data = response.json()

    # Validar respuesta general
    assert response.status_code == 200
    assert "table" in data and data["table"] == "hired_employees"
    assert "inserted" in data
    assert "message" in data

    # Validar que summary exista y tenga rechazados FK
    summary = data.get("summary", {})
    assert isinstance(summary, dict)
    assert summary.get("rejected_fk", 0) > 0, "Debe detectar errores FK"
    assert len(summary.get("rejected_rows", [])) == summary.get("rejected_fk")

    # Validar contenido del resumen
    for row in summary.get("rejected_rows", []):
        assert "error" in row
        assert "foreign key" in row["error"].lower()

    # Validar mensaje coherente
    assert "rechazadas por fk" in data["message"].lower()
