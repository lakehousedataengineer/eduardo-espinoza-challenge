-- ============================================
-- 🚀 Seed Data for PostgreSQL
-- ============================================

-- Limpieza previa (opcional si ya existen)
TRUNCATE TABLE hired_employees RESTART IDENTITY CASCADE;
TRUNCATE TABLE jobs RESTART IDENTITY CASCADE;
TRUNCATE TABLE departments RESTART IDENTITY CASCADE;

-- ===============================
-- 🏢 Insert Departments
-- ===============================
INSERT INTO departments (department)
VALUES 
    ('Product Management'),
    ('Sales'),
    ('Research and Development'),
    ('Business Development'),
    ('Engineering'),
    ('Human Resources'),
    ('Services'),
    ('Support'),
    ('Marketing'),
    ('Training'),
    ('Legal'),
    ('Accounting');

-- ===============================
-- 💼 Insert Jobs
-- ===============================
INSERT INTO jobs (job)
VALUES
    ('Marketing Assistant'),
    ('VP Sales'),
    ('Biostatistician IV'),
    ('Account Representative II'),
    ('VP Marketing'),
    ('Environmental Specialist'),
    ('Software Consultant'),
    ('Office Assistant III'),
    ('Information Systems Manager'),
    ('Desktop Support Technician'),
    ('Financial Advisor'),
    ('Computer Systems Analyst I'),
    ('Automation Specialist IV'),
    ('Help Desk Technician'),
    ('Office Assistant II'),
    ('VP Quality Control'),
    ('Office Assistant IV'),
    ('Financial Analyst'),
    ('Electrical Engineer'),
    ('Chemical Engineer'),
    ('Social Worker'),
    ('VP Product Management'),
    ('Administrative Officer'),
    ('Paralegal'),
    ('Actuary'),
    ('Database Administrator I'),
    ('Nuclear Power Engineer'),
    ('Database Administrator II'),
    ('GIS Technical Architect'),
    ('Human Resources Assistant IV'),
    ('Marketing Manager'),
    ('Structural Engineer'),
    ('General Manager'),
    ('Chief Design Engineer'),
    ('Senior Quality Engineer'),
    ('Pharmacist'),
    ('Accounting Assistant IV'),
    ('Web Developer I'),
    ('Automation Specialist I'),
    ('Statistician IV');

-- ===============================
-- 👥 Insert Hired Employees
-- ===============================
INSERT INTO hired_employees (name, datetime, department_id, job_id)
VALUES
    ('Alice Johnson', '2021-01-15 09:30:00', 1, 2),
    ('Bob Smith', '2021-02-22 11:15:00', 2, 3),
    ('Carlos Díaz', '2021-03-10 10:45:00', 3, 5),
    ('Diana Prince', '2021-04-05 14:00:00', 4, 8),
    ('Evelyn Wright', '2021-05-12 09:00:00', 5, 10),
    ('Frank Castle', '2021-06-18 16:30:00', 6, 12),
    ('Grace Lee', '2021-07-23 13:15:00', 7, 14),
    ('Henry Ford', '2021-08-19 15:45:00', 8, 17),
    ('Irene Adler', '2021-09-25 08:30:00', 9, 19),
    ('John Wick', '2021-10-30 12:00:00', 10, 22);
