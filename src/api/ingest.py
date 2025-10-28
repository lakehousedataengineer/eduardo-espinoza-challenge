from fastapi import APIRouter, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.services.batch_insert_service import insert_batch
from src.config.database import get_db
from src.utils.logger import get_logger
import tempfile
import os

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload/")
async def upload_csv(
    type: str = Form(...),
    file: UploadFile = Form(...),
    db: Session = Depends(get_db)
):
    """
    📤 Endpoint para cargar archivos CSV.
    - Valida tipo de archivo y estructura.
    - Inserta por lotes (máx. 1000 filas por batch).
    - Maneja errores, duplicados y registros inválidos.
    - Muestra resumen si hay registros rechazados por FK.
    """
    try:
        # 1️⃣ Validar tipo de archivo
        filename = file.filename.lower()
        if not filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV (.csv).")

        # 2️⃣ Validar tipo de tabla
        valid_types = ["departments", "jobs", "hired_employees"]
        if type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo inválido: '{type}'. Debe ser uno de: {valid_types}"
            )

        # 3️⃣ Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        logger.info(f"📦 Archivo recibido: {filename} → {tmp_path}")

        # 4️⃣ Procesar el CSV e insertar los datos
        result = insert_batch(db, tmp_path, type)

        # 5️⃣ Eliminar archivo temporal (si es posible)
        try:
            os.remove(tmp_path)
        except Exception as e:
            logger.warning(f"No se pudo eliminar el archivo temporal: {tmp_path} ({e})")

        # 6️⃣ Construir respuesta retrocompatible
        response = {
            "table": type,
            "inserted": result.get("inserted", 0),
            "invalid_rows": result.get("invalid_rows", 0),
            "duplicates": result.get("duplicates", 0),
            "message": result.get("message", "Procesamiento completado correctamente"),
        }

        # 7️⃣ Agregar resumen solo si existe
        summary = result.get("summary")
        if summary and (summary.get("rejected_fk") or summary.get("invalid_rows") or summary.get("duplicates")):
            response["summary"] = summary

        return response

    # ⚙️ Errores controlados explícitos
    except HTTPException as e:
        raise e

    # ⚠️ Errores de validación de datos
    except ValueError as e:
        logger.error(f"⚠️ Error de validación: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # ❌ Errores SQL o de integridad
    except SQLAlchemyError as e:
        logger.error(f"❌ Error SQLAlchemy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error de base de datos")

    # 🧯 Errores inesperados
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
