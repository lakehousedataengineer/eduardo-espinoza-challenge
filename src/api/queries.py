from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.config.database import SessionLocal
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_db():
    """Dependencia de base de datos para endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/hired-by-quarter/", tags=["Queries"])
def employees_by_quarter(db: Session = Depends(get_db)):
    """
    📊 Endpoint 1:
    Devuelve el número de empleados contratados por job y department en 2021,
    dividido por trimestre (Q1, Q2, Q3, Q4).
    """
    try:
        query = text("""
            SELECT 
                d.department AS department,
                j.job AS job,
                COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.datetime) = 1) AS Q1,
                COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.datetime) = 2) AS Q2,
                COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.datetime) = 3) AS Q3,
                COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.datetime) = 4) AS Q4
            FROM hired_employees e
            JOIN departments d ON e.department_id = d.id
            JOIN jobs j ON e.job_id = j.id
            WHERE EXTRACT(YEAR FROM e.datetime) = 2021
            GROUP BY d.department, j.job
            ORDER BY d.department ASC, j.job ASC;
        """)

        result = db.execute(query).mappings().all()
        return {"rows": result, "total": len(result)}
    except Exception as e:
        logger.error(f"Error ejecutando query hired-by-quarter: {str(e)}")
        raise HTTPException(status_code=500, detail="Error ejecutando consulta SQL")


@router.get("/above-mean/", tags=["Queries"])
def departments_above_mean(db: Session = Depends(get_db)):
    """
    📈 Endpoint 2:
    Lista los departamentos que contrataron más empleados que el promedio general de 2021.
    """
    try:
        query = text("""
            SELECT 
                d.id AS id,
                d.department AS department,
                COUNT(e.id) AS hired
            FROM hired_employees e
            JOIN departments d ON e.department_id = d.id
            WHERE EXTRACT(YEAR FROM e.datetime) = 2021
            GROUP BY d.id, d.department
            HAVING COUNT(e.id) > (
                SELECT AVG(sub.hired)
                FROM (
                    SELECT COUNT(id) AS hired
                    FROM hired_employees
                    WHERE EXTRACT(YEAR FROM datetime) = 2021
                    GROUP BY department_id
                ) sub
            )
            ORDER BY hired DESC;
        """)
        result = db.execute(query).mappings().all()
        return {"rows": result, "total": len(result)}
    except Exception as e:
        logger.error(f"Error ejecutando query above-mean: {str(e)}")
        raise HTTPException(status_code=500, detail="Error ejecutando consulta SQL")
