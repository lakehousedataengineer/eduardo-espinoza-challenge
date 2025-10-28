import io
import os
import csv
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.tests.utils_csv_generator import generate_hired_csv
from src.config.database import Base, engine
from src.services.batch_insert_service import MAX_BATCH_SIZE


client = TestClient(app)
pytestmark = pytest.mark.tdd


@pytest.fixture(scope="module")
def invalid_csvs(tmp_path_factory):
    """Genera CSVs con diferentes errores simulados."""
    base_dir = tmp_path_factory.mktemp("invalid_data")
    csv_invalid_date = base_dir / "hired_employees_invalid_date.csv"
    csv_empty = base_dir / "hired_employees_empty.csv"
    csv_missing_columns = base_dir / "hired_employees_missing_cols.csv"

    # CSV con fechas inválidas
    generate_hired_csv(csv_invalid_date, rows=50, valid=False)

    # CSV vacío
    csv_empty.write_text("")

    # CSV con columnas faltantes
    csv_missing_columns.write_text("id,name\n1,Test User")

    return {
        "invalid_date": csv_invalid_date,
        "empty": csv_empty,
        "missing_cols": csv_missing_columns,
    }


# ============================================================
# 🧪 TESTS DE VALIDACIONES DE INGESTA
# ============================================================

def test_upload_invalid_date_csv(invalid_csvs):
    """
    ✅ Test: CSV con fechas inválidas debe procesarse parcialmente (status 200)
    y registrar las filas erróneas en logs/invalid_hired_employees.csv.
    """
    with open(invalid_csvs["invalid_date"], "rb") as f:
        response = client.post(
            "/api/ingest/upload/",
            data={"type": "hired_employees"},
            files={"file": ("hired_employees_invalid_date.csv", f, "text/csv")}
        )

    data = response.json()

    # ✅ Nuevo comportamiento: no lanza error HTTP
    assert response.status_code == 200

    # Validar que existan filas inválidas registradas
    assert data["invalid_rows"] > 0, "Debe detectar registros con fechas inválidas"
    assert "message" in data
    assert "invalid" in data["message"].lower() or "inválidas" in data["message"].lower()

    # Validar que el archivo de logs exista
    assert os.path.exists("logs/invalid_hired_employees.csv"), "Debe generarse el archivo de logs"


def test_upload_empty_csv(invalid_csvs):
    """❌ Test: archivo CSV vacío."""
    with open(invalid_csvs["empty"], "rb") as f:
        response = client.post(
            "/api/ingest/upload/",
            data={"type": "hired_employees"},
            files={"file": ("hired_employees.csv", f, "text/csv")}
        )

    assert response.status_code == 400
    assert "vacío" in response.json()["detail"].lower()


def test_upload_missing_columns_csv(invalid_csvs):
    """❌ Test: CSV con columnas incompletas."""
    with open(invalid_csvs["missing_cols"], "rb") as f:
        response = client.post(
            "/api/ingest/upload/",
            data={"type": "hired_employees"},
            files={"file": ("hired_employees.csv", f, "text/csv")}
        )

    assert response.status_code in (400, 500)
    assert "column" in response.json()["detail"].lower() or "estructura" in response.json()["detail"].lower()


# ============================================================
# 🧪 TESTS DEL LÍMITE DE 1000 REGISTROS POR REQUEST
# ============================================================

def test_upload_hired_employees_exceeds_batch_limit(tmp_path):
    """
    ❌ Test: CSV con más de MAX_BATCH_SIZE filas debe devolver error 400.
    """
    csv_path = tmp_path / "too_many_hired.csv"
    rows_exceeding = MAX_BATCH_SIZE + 501  # superamos el límite intencionalmente

    # Generar CSV con más filas que el límite
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "datetime", "department_id", "job_id"])
        for i in range(rows_exceeding):
            writer.writerow([i, f"Employee {i}", "2024-01-01T10:00:00Z", 1, 1])

    with open(csv_path, "rb") as f:
        response = client.post(
            "/api/ingest/upload/",
            data={"type": "hired_employees"},
            files={"file": ("too_many_hired.csv", f, "text/csv")}
        )

    # ✅ Esperado: error 400 con mensaje del límite
    assert response.status_code == 400, f"Debe devolver 400, obtuvo {response.status_code}"
    detail = response.json().get("detail", "").lower()
    assert str(MAX_BATCH_SIZE) in detail or "límite" in detail, f"Mensaje inesperado: {detail}"


