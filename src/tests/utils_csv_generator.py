import pandas as pd
import random
import string
from datetime import datetime, timedelta
from pathlib import Path


random.seed(42)


def random_name() -> str:
    """Genera un nombre aleatorio para simular empleados."""
    return ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10)))


def random_datetime(year=2021):
    """Genera una fecha aleatoria dentro del año dado."""
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return (start + timedelta(seconds=random_seconds)).isoformat() + "Z"

def generate_hired_csv(path: str, rows: int = 1000, valid=True, duplicate=False) -> str:
    """
    Genera un CSV de empleados contratados con datos válidos o inválidos.
    Si duplicate=True, repetirá algunos IDs para probar duplicados.
    """
    data = []
    for i in range(1, rows + 1):
        row_id = i if not duplicate else (i if i % 10 != 0 else 1)  # cada 10 repite ID 1
        if valid:
            data.append({
                "id": row_id,
                "name": random_name(),
                "datetime": random_datetime(),
                "department_id": random.randint(1, 10),
                "job_id": random.randint(1, 10)
            })
        else:
            data.append({
                "id": row_id if i % 10 != 0 else None,
                "name": random_name() if i % 15 != 0 else "",
                "datetime": random_datetime() if i % 20 != 0 else "INVALID_DATE",
                "department_id": random.randint(1, 10),
                "job_id": random.randint(1, 10)
            })
    df = pd.DataFrame(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return str(path)



def generate_departments_csv(path: str, rows: int = 10):
    """Genera un CSV simple para la tabla departments."""
    data = [{"id": i, "department": f"Dept_{i}"} for i in range(1, rows + 1)]
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return str(path)


def generate_jobs_csv(path: str, rows: int = 10):
    """Genera un CSV simple para la tabla jobs."""
    data = [{"id": i, "job": f"Job_{i}"} for i in range(1, rows + 1)]
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return str(path)
