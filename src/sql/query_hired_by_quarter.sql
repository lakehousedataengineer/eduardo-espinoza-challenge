/*
------------------------------------------------------------
 📊 Query 1: Empleados contratados por trimestre (2021)
------------------------------------------------------------
Objetivo:
    Obtener el número de empleados contratados en 2021
    por departamento y puesto, divididos por trimestre.
------------------------------------------------------------
*/

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
