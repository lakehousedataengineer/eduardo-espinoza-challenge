# Data Engineering Challenge — Eduardo Espinoza

## 🧩 Descripción General

Este proyecto implementa la **solución completa del reto técnico de ingeniería de datos**, cumpliendo con todos los requisitos de la **Sección 1 (API)** y **Sección 2 (SQL)**, además del **Bonus Track** de **Testing** y **Containerización**.

La aplicación está desarrollada con **FastAPI (Python 3.8+)**, permite **migrar datos desde archivos CSV hacia una base de datos PostgreSQL**, y expone endpoints para **consultar métricas solicitadas mediante SQL**.

Incluye:
- Recepción y carga de CSV con validaciones.
- Inserción por lotes (hasta 1000 filas por request).
- Endpoints para métricas SQL solicitadas.
- Pruebas automáticas con `pytest`.
- Despliegue en **Render.com** mediante contenedor Docker.

---

## ⚙️ Estructura del Proyecto

```
eduardo-espinoza-challenge/
│
├── src/
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── config/
│   │   └── database.py          # Configuración SQLAlchemy (PostgreSQL)
│   ├── models/                  # Definición de tablas ORM
│   ├── api/
│   │   └── ingest.py            # Endpoints de departamentos, jobs y empleados
│   ├── services/                # Lógica de validación y carga de CSV
│   └── tests/                   # Pruebas unitarias
│
├── Dockerfile                   # Imagen para despliegue en Render
├── requirements.txt             # Dependencias de Python
├── render.yaml                  # Configuración de servicio Render.com
├── .env.example                 # Variables de entorno base
└── README.md                    # Este archivo
```

---

## 🧠 Constantes y Validaciones

El sistema usa una constante para controlar la **carga masiva máxima de registros**:

```python
MAX_BATCH_SIZE = 1000
```

### Validaciones realizadas:
- Estructura de columnas exacta según tipo de entidad (`departments`, `jobs`, `employees`).
- Detección de columnas faltantes o con nombres no válidos.
- Validación de tipos (`int`, `string`, `datetime` ISO 8601).
- Rechazo de lotes con filas inválidas.
- Prevención de duplicados por `id`.

---

## 🧩 Endpoints Principales

### 1️⃣ **Carga de Datos desde CSV**

| Método | Endpoint | Descripción |
|--------|-----------|-------------|
| `POST` | `/upload/departments/` | Carga CSV con datos de departamentos. |
| `POST` | `/upload/jobs/` | Carga CSV con datos de puestos. |
| `POST` | `/upload/employees/` | Carga CSV de empleados contratados. Admite hasta 1000 registros. |

**Ejemplos de uso (cURL):**

📂 **1. Cargar departamentos**
```bash
curl -X POST "http://localhost:8000/upload/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "type=departments" \
  -F "file=@departments.csv;type=text/csv"

📂 **2. Cargar puestos (jobs)
```bash
curl -X POST "http://localhost:8000/upload/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "type=jobs" \
  -F "file=@jobs.csv;type=text/csv"

📂 **3. Cargar empleados contratados
```bash
curl -X POST "http://localhost:8000/upload/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "type=hired_employees" \
  -F "file=@hired_employees.csv;type=text/csv"

---

### 2️⃣ **Consultas SQL Solicitadas (Sección 2 del Challenge)**

#### a. Empleados contratados por trimestre (2021)
**Endpoint:**
```
GET /analytics/hired_per_quarter/
```
**Descripción:**
Devuelve el número de empleados contratados por cada **departamento** y **puesto**, separados por trimestre de 2021.

**Salida esperada:**
| department | job | Q1 | Q2 | Q3 | Q4 |
|-------------|-----|----|----|----|----|
| Staff | Recruiter | 3 | 0 | 7 | 11 |

---

#### b. Departamentos que contrataron por encima del promedio (2021)
**Endpoint:**
```
GET /analytics/departments_above_mean/
```
**Descripción:**
Lista los departamentos que contrataron **más empleados que el promedio global** de 2021, ordenados de forma descendente.

**Salida esperada:**
| id | department | hired |
|----|-------------|--------|
| 7 | Staff | 45 |
| 9 | Supply Chain | 12 |

---


## 🧪 Pruebas Automáticas

Las pruebas se ubican en el directorio `src/tests/` y se dividen en **tres módulos** principales:

| Archivo | Descripción |
|----------|-------------|
| `test_upload_departments.py` | Valida la carga correcta de `departments.csv` y el rechazo de archivos con estructura inválida. |
| `test_upload_jobs.py` | Verifica la carga del CSV `jobs.csv`, estructura, tipos de datos y control de duplicados. |
| `test_upload_employees.py` | Evalúa el endpoint de carga masiva de `hired_employees.csv`, incluyendo límites y validaciones de formato. |
| `test_analytics_quarter.py` | Prueba el endpoint `/analytics/hired_per_quarter/`, verificando los resultados trimestrales por departamento y puesto. |
| `test_analytics_above_mean.py` | Valida el endpoint `/analytics/departments_above_mean/` y la correcta comparación con el promedio global. |

---

### 📋 Detalle de las pruebas

#### 1️⃣ **Pruebas de carga de archivos CSV**

**Archivo:** `test_upload_departments.py`
- ✅ Carga exitosa de `departments.csv` con columnas correctas (`id`, `department`).
- ❌ Error por columnas faltantes.
- ❌ Error por archivo vacío.
- ✅ Inserción sin duplicados por `id`.

**Archivo:** `test_upload_jobs.py`
- ✅ Inserta correctamente `jobs.csv` con columnas (`id`, `job`).
- ❌ Rechaza CSV con tipo de dato incorrecto (por ejemplo, `id` no numérico).
- ✅ Confirma respuesta HTTP 200 y conteo correcto de filas insertadas.

**Archivo:** `test_upload_employees.py`
- ✅ Inserta registros válidos de `hired_employees.csv` (hasta `MAX_BATCH_SIZE` = 1000).
- ❌ Rechaza CSV con formato incorrecto de fecha o `department_id` inexistente.
- ✅ Detecta límite de inserción: si supera 1000 filas, retorna error `400 Bad Request`.
- ✅ Verifica transacciones por lotes y rollback si ocurre error parcial.

---

#### 2️⃣ **Pruebas de endpoints analíticos**

**Archivo:** `test_analytics_quarter.py`
- ✅ Consulta `/analytics/hired_per_quarter/` y valida:
  - Que los campos `Q1`, `Q2`, `Q3`, `Q4` existan.
  - Que los resultados estén ordenados alfabéticamente por `department` y `job`.
  - Que la suma total de contrataciones trimestrales coincida con los datos base.

**Archivo:** `test_analytics_above_mean.py`
- ✅ Ejecuta `/analytics/departments_above_mean/` y comprueba:
  - Que solo aparezcan departamentos con contrataciones > promedio 2021.
  - Que el resultado esté ordenado de mayor a menor por número de contrataciones.
  - Que el formato de respuesta contenga `id`, `department` y `hired`.

---

### 🧩 Datos de prueba utilizados

Durante las pruebas se usan versiones reducidas de los CSV oficiales del challenge:

- `tests/data/departments_sample.csv`
- `tests/data/jobs_sample.csv`
- `tests/data/hired_employees_sample.csv`

Cada uno contiene entre **5 y 20 registros** de ejemplo con datos consistentes entre tablas.

---

### 🧪 Ejecución de pruebas

Para ejecutar **todas las pruebas** (unitarias + integradas):

```bash
pytest -v --disable-warnings
```

Para ejecutar solo un grupo específico:

```bash
pytest src/tests/test_upload_employees.py -v
pytest src/tests/test_analytics_quarter.py -v
```

---

### 🧾 Ejemplo de salida esperada
```
====================== test session starts ======================
collected 25 items

src/tests/test_upload_departments.py .....           [ 20%]
src/tests/test_upload_jobs.py ......                 [ 40%]
src/tests/test_upload_employees.py ..........        [ 80%]
src/tests/test_analytics_quarter.py ....             [ 92%]
src/tests/test_analytics_above_mean.py ..            [100%]

================= 25 passed in 4.31s =============================
```



## 🚀 Ejecución local del servidor FastAPI

Si deseas ejecutar la aplicación **localmente sin Docker**, sigue los pasos:

### 1️⃣ Crear entorno virtual e instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Configurar variables de entorno
Copia el archivo `.env.example` a `.env` y actualiza las credenciales de base de datos.

### 3️⃣ Iniciar el servidor FastAPI
```bash
uvicorn src.main:app --reload
```

### 4️⃣ Acceder a la documentación
Abre tu navegador en:
```
http://localhost:8000/docs
```


## 🐳 Despliegue con Docker (Local)

A continuación se detallan los comandos necesarios para compilar, ejecutar, inspeccionar y limpiar el entorno Docker del proyecto **eduardo-espinoza-challenge**.

### 1️⃣ Construir la imagen
Compila la imagen Docker localmente:
```bash
docker build -t eduardo-espinoza-challenge .
```

### 2️⃣ Ejecutar el contenedor
Ejecuta el contenedor en segundo plano mapeando el puerto 8000:
```bash
docker run -d -p 8000:8000 --env-file .env eduardo-espinoza-challenge
```

### 3️⃣ Verificar el estado de las imágenes y contenedores
Listar todas las imágenes disponibles:
```bash
docker images
```
Listar todos los contenedores activos:
```bash
docker ps
```
Listar todos los contenedores (incluidos detenidos):
```bash
docker ps -a
```

### 4️⃣ Eliminar imágenes y contenedores (limpieza total)
Eliminar todos los contenedores detenidos:
```bash
docker container prune -f
```
Eliminar todas las imágenes locales:
```bash
docker rmi -f $(docker images -q)
```
Eliminar todos los volúmenes no utilizados:
```bash
docker volume prune -f
```

### 5️⃣ Compilar y ejecutar todo con un solo comando
Este comando limpia, compila y lanza la aplicación en un solo paso:
```bash
docker system prune -af && docker build -t eduardo-espinoza-challenge . && docker run -d -p 8000:8000 --env-file .env eduardo-espinoza-challenge
```

### 6️⃣ Acceder a la API
Una vez iniciado el contenedor, abre en tu navegador:
```
http://localhost:8000/docs
```
### 7️⃣ Detener todos los contenedores en ejecución
```bash
docker stop $(docker ps -aq)
```


### 8️⃣ Limpiar completamente el entorno Docker (sin errores si está vacío)
```bash
# Elimina contenedores detenidos
docker container prune -f

# Elimina imágenes no usadas
docker image prune -af

# Elimina volúmenes no usados
docker volume prune -f

# Limpieza total (contenedores, imágenes, redes y volúmenes)
docker system prune -af --volumes
```


### 9️⃣ Limpiar todo y reconstruir desde cero
```bash
docker system prune -af && docker build -t eduardo-espinoza-challenge . && docker run -d -p 8000:8000 --env-file .env eduardo-espinoza-challenge
```

### 🔎 Verificar estado del servicio
```bash
curl http://localhost:8000/docs
```



---

## 🧹 Limpieza total de Docker

En caso necesites **borrar absolutamente todas las imágenes, contenedores, volúmenes y redes** (por ejemplo, para reiniciar desde cero tu entorno Docker), sigue los pasos a continuación.

> ⚠️ **Advertencia:** Esto eliminará *todo* lo que tengas en Docker, incluyendo contenedores, imágenes y bases de datos.  
> Úsalo solo si deseas hacer una limpieza total del sistema Docker.

### 1️⃣ Detener todos los contenedores
```bash
docker stop $(docker ps -aq) 2>/dev/null
```

### 2️⃣ Eliminar todos los contenedores
```bash
docker rm -f $(docker ps -aq) 2>/dev/null
```

### 3️⃣ Eliminar todas las imágenes
```bash
docker rmi -f $(docker images -q) 2>/dev/null
```

### 4️⃣ Eliminar todos los volúmenes (incluye bases de datos)
```bash
docker volume rm $(docker volume ls -q) 2>/dev/null
```

### 5️⃣ Eliminar todas las redes no usadas
```bash
docker network prune -f
```

### 6️⃣ Limpieza general (todo lo anterior junto)
Puedes hacer todo con un solo comando:
```bash
docker system prune -af --volumes
```

### 7️⃣ Verificar que está limpio
```bash
docker ps -a
docker images
docker volume ls
```

Si todos los comandos devuelven vacío, tu sistema Docker quedó completamente limpio ✅



---

## 🧱 Construir y Reiniciar con Docker Compose

Si utilizas **Docker Compose** para desplegar tu entorno (FastAPI + PostgreSQL), puedes usar los siguientes comandos:

### 🏗️ Construir todo nuevamente
Compila y lanza los contenedores desde cero:
```bash
docker compose up -d --build
```

### 🔁 Reiniciar todos los servicios
Detiene y vuelve a levantar todo el entorno sin reconstruir imágenes:
```bash
docker compose down
docker compose up -d
```

Estos comandos garantizan que tanto **FastAPI** como **PostgreSQL** se actualicen correctamente y permanezcan sincronizados.


## ☁️ Despliegue en Render.com

El proyecto fue configurado para **Render.com** usando los siguientes archivos:

| Archivo | Descripción |
|----------|-------------|
| `Dockerfile` | Define la imagen base, instala dependencias y expone el puerto 8000. |
| `requirements.txt` | Lista de librerías Python requeridas (FastAPI, SQLAlchemy, psycopg2, pytest). |
| `render.yaml` | Indica el servicio web, runtime Docker y comando de inicio. |

### Ejemplo de `render.yaml`
```yaml
services:
  - type: web
    name: fastapi-app
    env: docker
    plan: free
    region: oregon  # Puedes usar frankfurt o virginia si prefieres
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: PG_HOST
        value: your-db-host.railway.app
      - key: PG_PORT
        value: 5432
      - key: PG_USER
        value: kalito
      - key: PG_PASSWORD
        value: AllMyLoving2025$$
      - key: PG_DB
        value: landing
```

---

## 🧾 Ejemplo de `.env`

```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/landing
MAX_BATCH_SIZE=1000
```

---

## 🧱 Tecnologías Utilizadas

| Componente | Tecnología |
|-------------|-------------|
| Lenguaje | Python 3.8 |
| Framework API | FastAPI |
| ORM | SQLAlchemy |
| Base de Datos | PostgreSQL |
| Testing | pytest |
| Contenedores | Docker |
| Cloud Hosting | Render.com |

---

## 👨‍💻 Autor

**Eduardo Espinoza**  
Data Engineering Technical Lead  
[GitHub: lakehousedataengineer](https://github.com/lakehousedataengineer)

---