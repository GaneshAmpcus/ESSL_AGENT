

-- =========================================================
-- ESSL DUMMY DATA SETUP
-- Creates database and tables if they do not exist
-- Then inserts sample data
-- Safe to run multiple times
-- SQL Server
-- =========================================================

-- =========================================================
-- CREATE DATABASE
-- =========================================================
IF DB_ID('ESSL') IS NULL
BEGIN
    CREATE DATABASE ESSL;
END
GO

USE ESSL;
GO

-- =========================================================
-- CREATE DEPARTMENTS TABLE
-- =========================================================
IF OBJECT_ID('dbo.Departments', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Departments
    (
        DepartmentId INT IDENTITY(1,1) PRIMARY KEY,
        DepartmentName VARCHAR(100) NOT NULL,
        DepartmentCode VARCHAR(20) UNIQUE,
        CreatedDate DATETIME DEFAULT GETDATE()
    );
END
GO

-- =========================================================
-- CREATE EMPLOYEES TABLE
-- =========================================================
IF OBJECT_ID('dbo.Employees', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Employees
    (
        EmployeeId VARCHAR(20) PRIMARY KEY,
        EmployeeCode VARCHAR(20) UNIQUE,
        EmployeeName VARCHAR(150) NOT NULL,
        Gender VARCHAR(10),
        DepartmentId INT,
        Designation VARCHAR(100),
        Email VARCHAR(150),
        MobileNo VARCHAR(20),
        JoiningDate DATE,
        ShiftName VARCHAR(50),
        Salary DECIMAL(18,2),
        IsActive BIT DEFAULT 1,
        CreatedDate DATETIME DEFAULT GETDATE(),

        CONSTRAINT FK_Employees_Department
            FOREIGN KEY (DepartmentId)
            REFERENCES dbo.Departments(DepartmentId)
    );
END
GO

-- =========================================================
-- INSERT DEPARTMENTS (ONLY IF EMPTY)
-- =========================================================
IF NOT EXISTS (SELECT 1 FROM dbo.Departments)
BEGIN
    INSERT INTO dbo.Departments
    (
        DepartmentName,
        DepartmentCode
    )
    VALUES
    ('Human Resources','HR'),
    ('Engineering','ENG'),
    ('Finance','FIN'),
    ('Operations','OPS'),
    ('IT Infrastructure','IT');
END
GO

-- =========================================================
-- INSERT EMPLOYEES (ONLY IF NOT EXISTS)
-- =========================================================
IF NOT EXISTS (SELECT 1 FROM dbo.Employees WHERE EmployeeId = 'PTSPL0001')
BEGIN
    INSERT INTO dbo.Employees
    (
        EmployeeId,
        EmployeeCode,
        EmployeeName,
        Gender,
        DepartmentId,
        Designation,
        Email,
        MobileNo,
        JoiningDate,
        ShiftName,
        Salary
    )
    VALUES
    ('PTSPL0001','EMP001','Aarav Mehta','Male',2,'Software Engineer','aarav@ptspl.com','9876543201','2022-04-11','SHIFT-A',85000),
    ('PTSPL0002','EMP002','Priya Sharma','Female',1,'HR Executive','priya@ptspl.com','9876543202','2021-08-19','SHIFT-B',65000),
    ('PTSPL0003','EMP003','Rohan Verma','Male',4,'Warehouse Supervisor','rohan@ptspl.com','9876543203','2020-01-09','EARLYSHIFT',55000),
    ('PTSPL0004','EMP004','Neha Kulkarni','Female',3,'Finance Analyst','neha@ptspl.com','9876543204','2019-11-25','SHIFT-B',72000),
    ('PTSPL0005','EMP005','Vikram Nair','Male',5,'Data Center Engineer','vikram@ptspl.com','9876543205','2018-07-14','NIGHTSHIFT',98000);
END
GO

-- =========================================================
-- VERIFY DATA
-- =========================================================
SELECT COUNT(*) AS DepartmentCount FROM dbo.Departments;
SELECT COUNT(*) AS EmployeeCount FROM dbo.Employees;
GO




