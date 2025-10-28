import os
import pandas as pd
from src.tests.utils_csv_generator import (
    random_name,
    random_datetime,
    generate_hired_csv,
    generate_departments_csv,
    generate_jobs_csv
)


def test_random_name_generates_nonempty():
    """✅ random_name() debe generar nombres válidos."""
    name = random_name()
    assert isinstance(name, str)
    assert len(name) >= 5


def test_random_datetime_format():
    """✅ random_datetime() debe generar un string ISO válido."""
    dt = random_datetime()
    assert dt.endswith("Z")
    assert "T" in dt
    assert dt.startswith("2021-")


def test_generate_hired_csv_valid(tmp_path):
    """✅ generate_hired_csv() debe crear un archivo CSV con columnas correctas."""
    path = tmp_path / "hired_employees.csv"
    file_path = generate_hired_csv(path, rows=10, valid=True)

    assert os.path.exists(file_path)
    df = pd.read_csv(file_path)
    expected_cols = {"id", "name", "datetime", "department_id", "job_id"}
    assert expected_cols.issubset(df.columns)
    assert len(df) == 10


def test_generate_hired_csv_invalid(tmp_path):
    """✅ generate_hired_csv() con valid=False debe generar filas con errores intencionales."""
    path = tmp_path / "hired_employees_invalid.csv"
    file_path = generate_hired_csv(path, rows=20, valid=False)

    df = pd.read_csv(file_path)
    # Al menos una fila debería tener datos inválidos (fechas, ids o nombres vacíos)
    invalids = df[df["id"].isna() | (df["name"] == "") | (df["datetime"] == "INVALID_DATE")]
    assert len(invalids) > 0


def test_generate_departments_csv(tmp_path):
    """✅ generate_departments_csv() debe crear CSV con columnas id, department."""
    path = tmp_path / "departments.csv"
    file_path = generate_departments_csv(path, rows=5)

    df = pd.read_csv(file_path)
    assert {"id", "department"}.issubset(df.columns)
    assert len(df) == 5


def test_generate_jobs_csv(tmp_path):
    """✅ generate_jobs_csv() debe crear CSV con columnas id, job."""
    path = tmp_path / "jobs.csv"
    file_path = generate_jobs_csv(path, rows=5)

    df = pd.read_csv(file_path)
    assert {"id", "job"}.issubset(df.columns)
    assert len(df) == 5


def test_generate_hired_csv_with_duplicates(tmp_path):
    path = tmp_path / "dup.csv"
    generate_hired_csv(path, rows=20, valid=True, duplicate=True)
    df = pd.read_csv(path)
    assert df["id"].duplicated().any()
