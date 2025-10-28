from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import Base

# 🏢 Tabla: departments
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(String(100), nullable=False)

    # Relación hacia empleados
    employees = relationship("HiredEmployee", back_populates="department")


# 💼 Tabla: jobs
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job = Column(String(100), nullable=False)

    # Relación hacia empleados
    employees = relationship("HiredEmployee", back_populates="job")


# 👤 Tabla: hired_employees
class HiredEmployee(Base):
    __tablename__ = "hired_employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    datetime = Column(DateTime, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))

    # Relaciones inversas
    department = relationship("Department", back_populates="employees")
    job = relationship("Job", back_populates="employees")

    def __repr__(self):
        return f"<HiredEmployee(id={self.id}, name='{self.name}')>"
