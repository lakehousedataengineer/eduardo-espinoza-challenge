import os
import pandas as pd
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from src.models import models
from src.utils.logger import get_logger

logger = get_logger(__name__)
MAX_BATCH_SIZE = 2000

# Columnas esperadas por tabla
EXPECTED_COLUMNS = {
    "departments": ["id", "department"],
    "jobs": ["id", "job"],
    "hired_employees": ["id", "name", "datetime", "department_id", "job_id"],
}

# ============================================================
#  CARGA Y VALIDACIÓN DEL CSV
# ============================================================

def load_csv_strict(file_path: str, table: str):
    """Carga un CSV y valida formato, tipos y valores nulos."""
    if table not in EXPECTED_COLUMNS:
        raise ValueError(f"Tabla no soportada: {table}")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        msg = str(e).lower()
        if "no columns" in msg or "empty" in msg:
            raise ValueError("El archivo CSV está vacío o no contiene datos válidos.")
        raise ValueError(f"Error al leer CSV: {e}")

    # Validar encabezados exactos
    if list(df.columns) != EXPECTED_COLUMNS[table]:
        raise ValueError(
            f"Estructura inválida: faltan columnas esperadas para {table}. "
            f"Cabeceras recibidas: {list(df.columns)}"
        )

    df = df.dropna(how="all")
    invalid_rows = []

    if table == "hired_employees":
        for _, row in df.iterrows():
            try:
                if pd.isna(row["id"]) or pd.isna(row["name"]) or pd.isna(row["datetime"]) \
                   or pd.isna(row["department_id"]) or pd.isna(row["job_id"]):
                    raise ValueError("Campos obligatorios nulos")
                pd.to_datetime(row["datetime"], errors="raise", utc=True)
            except Exception as e:
                invalid_rows.append({**row.to_dict(), "error": str(e)})

        if invalid_rows:
            os.makedirs("logs", exist_ok=True)
            pd.DataFrame(invalid_rows).to_csv("logs/invalid_hired_employees.csv", index=False)
            logger.warning(
                f"{len(invalid_rows)} registros inválidos guardados en logs/invalid_hired_employees.csv"
            )

        df = df.dropna(subset=["id", "name", "datetime", "department_id", "job_id"])
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True)
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df["department_id"] = pd.to_numeric(df["department_id"], errors="coerce")
        df["job_id"] = pd.to_numeric(df["job_id"], errors="coerce")
        df = df.dropna(subset=["id", "datetime", "department_id", "job_id"])
        df = df.where(pd.notnull(df), None)

    else:
        field = EXPECTED_COLUMNS[table][1]
        for _, row in df.iterrows():
            try:
                if pd.isna(row["id"]) or pd.isna(row[field]):
                    raise ValueError("Campos obligatorios nulos")
            except Exception as e:
                invalid_rows.append({**row.to_dict(), "error": str(e)})

        if invalid_rows:
            os.makedirs("logs", exist_ok=True)
            pd.DataFrame(invalid_rows).to_csv(f"logs/invalid_{table}.csv", index=False)
            logger.warning(
                f"{len(invalid_rows)} registros inválidos guardados en logs/invalid_{table}.csv"
            )

        df = df.dropna(subset=["id", field])
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"])
        df = df.where(pd.notnull(df), None)
        df["id"] = df["id"].astype(int)

    return df, len(invalid_rows)

# ============================================================
#  INSERCIÓN POR LOTES CON DETECCIÓN DE DUPLICADOS Y FK
# ============================================================

def insert_batch(db, file_or_df, table: str):
    """Inserta registros válidos por lotes con detección de duplicados y errores FK."""
    try:
        # Cargar DataFrame
        if isinstance(file_or_df, (str, bytes)):
            df, invalid_count = load_csv_strict(file_or_df, table)
        elif isinstance(file_or_df, pd.DataFrame):
            df, invalid_count = file_or_df, 0
        else:
            raise ValueError("Entrada inválida (debe ser path o DataFrame)")

        # 🚨 Validación: tamaño del batch
        record_count = len(df)
        if record_count == 0:
            raise HTTPException(
                status_code=400,
                detail="El archivo CSV está vacío. Debe contener al menos 1 registro."
            )
        if record_count > MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"El archivo CSV contiene {record_count} registros. "
                    f"El límite máximo permitido por request es de {MAX_BATCH_SIZE} registros."
                ),
            )

        # Selección de modelo
        if table == "hired_employees":
            model = models.HiredEmployee
        elif table == "departments":
            model = models.Department
        elif table == "jobs":
            model = models.Job
        else:
            raise ValueError(f"Tabla desconocida: {table}")

        # Detectar duplicados existentes
        existing_ids = {r[0] for r in db.query(model.id).filter(model.id.in_(df["id"].tolist()))}
        duplicates_detected = len(existing_ids)
        if duplicates_detected:
            duplicates = df[df["id"].isin(existing_ids)]
            os.makedirs("logs", exist_ok=True)
            duplicates.to_csv(f"logs/duplicates_{table}.csv", index=False)
            df = df[~df["id"].isin(existing_ids)]
            logger.warning(f"{duplicates_detected} duplicados detectados en {table} → logs/duplicates_{table}.csv")

        # Duplicados dentro del CSV
        duplicate_ids_in_csv = df["id"].duplicated(keep=False)
        if duplicate_ids_in_csv.any():
            duplicates_csv = df[duplicate_ids_in_csv]
            os.makedirs("logs", exist_ok=True)
            duplicates_csv.to_csv(f"logs/duplicates_infile_{table}.csv", index=False)
            df = df.drop_duplicates(subset=["id"], keep="first")
            duplicates_detected += len(duplicates_csv)
            logger.warning(f"{len(duplicates_csv)} duplicados dentro del CSV detectados en {table}")

        # Conversión ORM
        valid_objects, fk_errors = [], []
        for _, row in df.iterrows():
            try:
                if table == "departments":
                    valid_objects.append(models.Department(**row))
                elif table == "jobs":
                    valid_objects.append(models.Job(**row))
                else:
                    dt = datetime.fromisoformat(str(row["datetime"]).replace("Z", "+00:00"))
                    valid_objects.append(models.HiredEmployee(
                        id=int(row["id"]),
                        name=row["name"],
                        datetime=dt,
                        department_id=int(row["department_id"]),
                        job_id=int(row["job_id"])
                    ))
            except Exception as e:
                fk_errors.append({**row.to_dict(), "error": str(e)})

        inserted, rejected_fk = 0, []

        # Inserción fila por fila para capturar errores FK sin abortar
        for obj in valid_objects:
            try:
                db.add(obj)
                db.commit()
                inserted += 1
            except IntegrityError as e:
                db.rollback()
                err_msg = str(e.orig).lower()
                if "foreign key" in err_msg:
                    rejected_fk.append({
                        "id": getattr(obj, "id", None),
                        "error": err_msg
                    })
                else:
                    raise
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"❌ Error SQL inesperado: {e}")

        if rejected_fk:
            os.makedirs("logs", exist_ok=True)
            pd.DataFrame(rejected_fk).to_csv("logs/foreign_key_errors_hired_employees.csv", index=False)
            logger.warning(
                f"{len(rejected_fk)} errores de clave foránea detectados → logs/foreign_key_errors_hired_employees.csv"
            )

        summary = {
            "total": len(df),
            "inserted": inserted,
            "rejected_fk": len(rejected_fk),
            "duplicates": duplicates_detected,
            "invalid_rows": invalid_count,
            "rejected_rows": rejected_fk,
        }

        return {
            "inserted": inserted,
            "invalid_rows": invalid_count,
            "duplicates": duplicates_detected,
            "summary": summary,
            "message": (
                f"Insertadas {inserted}, "
                f"{invalid_count} inválidas, "
                f"{duplicates_detected} duplicadas, "
                f"{len(rejected_fk)} rechazadas por FK en {table}"
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado en batch {table}: {e}", exc_info=True)
        raise
