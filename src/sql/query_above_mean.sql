/*
------------------------------------------------------------
 📈 Query 2: Departamentos que contrataron por encima del promedio (2021)
------------------------------------------------------------
Objetivo:
    Listar los departamentos que contrataron más empleados
    que el promedio total de contrataciones por departamento
    durante el año 2021.

Columnas:
    id          -> ID del departamento
    department  -> Nombre del departamento
    hired       -> Total de empleados contratados
------------------------------------------------------------
*/

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
    ) AS sub
)
ORDER BY hired DESC;
