-- ============================================================================
-- STEP 1: ENSURE WE ARE USING THE CORRECT DATABASE
-- ============================================================================
USE ESSL;
GO

-- ============================================================================
-- STEP 2: CREATE DeviceLogs TABLES (if they don't already exist)
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.DeviceLogs_3_2026') AND type = 'U')
BEGIN
    CREATE TABLE dbo.DeviceLogs_3_2026 (
        Id                INT IDENTITY(1,1) PRIMARY KEY,
        DownloadDate      DATETIME,
        DeviceId          INT,
        UserId            VARCHAR(20),
        LogDate           DATETIME,
        Direction         VARCHAR(10),
        AttDirection      VARCHAR(10),
        WorkCode          VARCHAR(20),
        UpdateFlag        INT,
        Longitude         VARCHAR(20),
        Latitude          VARCHAR(20),
        IsApproved        INT,
        CreatedDate       DATETIME,
        LastModifiedDate  DATETIME,
        LocationAddress   VARCHAR(100),
        BodyTemperature   DECIMAL(5,2),
        IsMaskOn          INT
    );
    PRINT 'Created table: dbo.DeviceLogs_3_2026';
END
ELSE
    PRINT 'Table already exists: dbo.DeviceLogs_3_2026';
GO

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.DeviceLogs_4_2026') AND type = 'U')
BEGIN
    CREATE TABLE dbo.DeviceLogs_4_2026 (
        Id                INT IDENTITY(1,1) PRIMARY KEY,
        DownloadDate      DATETIME,
        DeviceId          INT,
        UserId            VARCHAR(20),
        LogDate           DATETIME,
        Direction         VARCHAR(10),
        AttDirection      VARCHAR(10),
        WorkCode          VARCHAR(20),
        UpdateFlag        INT,
        Longitude         VARCHAR(20),
        Latitude          VARCHAR(20),
        IsApproved        INT,
        CreatedDate       DATETIME,
        LastModifiedDate  DATETIME,
        LocationAddress   VARCHAR(100),
        BodyTemperature   DECIMAL(5,2),
        IsMaskOn          INT
    );
    PRINT 'Created table: dbo.DeviceLogs_4_2026';
END
ELSE
    PRINT 'Table already exists: dbo.DeviceLogs_4_2026';
GO

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.DeviceLogs_5_2026') AND type = 'U')
BEGIN
    CREATE TABLE dbo.DeviceLogs_5_2026 (
        Id                INT IDENTITY(1,1) PRIMARY KEY,
        DownloadDate      DATETIME,
        DeviceId          INT,
        UserId            VARCHAR(20),
        LogDate           DATETIME,
        Direction         VARCHAR(10),
        AttDirection      VARCHAR(10),
        WorkCode          VARCHAR(20),
        UpdateFlag        INT,
        Longitude         VARCHAR(20),
        Latitude          VARCHAR(20),
        IsApproved        INT,
        CreatedDate       DATETIME,
        LastModifiedDate  DATETIME,
        LocationAddress   VARCHAR(100),
        BodyTemperature   DECIMAL(5,2),
        IsMaskOn          INT
    );
    PRINT 'Created table: dbo.DeviceLogs_5_2026';
END
ELSE
    PRINT 'Table already exists: dbo.DeviceLogs_5_2026';
GO

-- ============================================================================
-- STEP 3: INSERT 60 ROWS INTO DeviceLogs_3_2026
-- ============================================================================
DECLARE @i INT = 1;
DECLARE @emp VARCHAR(20);
DECLARE @baseDate DATETIME;

WHILE @i <= 60
BEGIN
    SET @emp = 'PTSPL000' + CAST(((@i - 1) % 5) + 1 AS VARCHAR(1));
    SET @baseDate = DATEADD(MINUTE, @i * 30, '2026-03-01 08:00:00');

    INSERT INTO dbo.DeviceLogs_3_2026
    (
        DownloadDate, DeviceId, UserId, LogDate,
        Direction, AttDirection, WorkCode, UpdateFlag,
        Longitude, Latitude, IsApproved,
        CreatedDate, LastModifiedDate,
        LocationAddress, BodyTemperature, IsMaskOn
    )
    VALUES
    (
        DATEADD(SECOND, 5, @baseDate),
        31 + (@i % 3),
        @emp,
        @baseDate,
        CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
        CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
        'SHIFT-A',
        0,
        '72.877655',
        '19.076090',
        -1,
        DATEADD(SECOND, 5, @baseDate),
        DATEADD(SECOND, 5, @baseDate),
        'Mumbai Office',
        36.5,
        1
    );

    SET @i = @i + 1;
END

PRINT 'Inserted 60 rows into dbo.DeviceLogs_3_2026';
GO

-- ============================================================================
-- STEP 4: INSERT 60 ROWS INTO DeviceLogs_4_2026
-- ============================================================================
DECLARE @i INT = 1;
DECLARE @emp VARCHAR(20);
DECLARE @baseDate DATETIME;

WHILE @i <= 60
BEGIN
    SET @emp = 'PTSPL000' + CAST(((@i - 1) % 5) + 1 AS VARCHAR(1));
    SET @baseDate = DATEADD(MINUTE, @i * 30, '2026-04-01 08:00:00');

    INSERT INTO dbo.DeviceLogs_4_2026
    (
        DownloadDate, DeviceId, UserId, LogDate,
        Direction, AttDirection, WorkCode, UpdateFlag,
        Longitude, Latitude, IsApproved,
        CreatedDate, LastModifiedDate,
        LocationAddress, BodyTemperature, IsMaskOn
    )
    VALUES
    (
        DATEADD(SECOND, 5, @baseDate),
        31 + (@i % 3),
        @emp,
        @baseDate,
        CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
        CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
        'SHIFT-A',
        0,
        '72.877655',
        '19.076090',
        -1,
        DATEADD(SECOND, 5, @baseDate),
        DATEADD(SECOND, 5, @baseDate),
        'Mumbai Office',
        36.5,
        1
    );

    SET @i = @i + 1;
END

PRINT 'Inserted 60 rows into dbo.DeviceLogs_4_2026';
GO

-- ============================================================================
-- STEP 5: INSERT 60 ROWS INTO DeviceLogs_5_2026
-- ============================================================================
DECLARE @i INT = 1;
DECLARE @emp VARCHAR(20);
DECLARE @baseDate DATETIME;

WHILE @i <= 60
BEGIN
    SET @emp = 'PTSPL000' + CAST(((@i - 1) % 5) + 1 AS VARCHAR(1));
    SET @baseDate = DATEADD(MINUTE, @i * 30, '2026-05-01 08:00:00');

    INSERT INTO dbo.DeviceLogs_5_2026
    (
        DownloadDate, DeviceId, UserId, LogDate,
        Direction, AttDirection, WorkCode, UpdateFlag,
        Longitude, Latitude, IsApproved,
        CreatedDate, LastModifiedDate,
        LocationAddress, BodyTemperature, IsMaskOn
    )
    VALUES
    (
        DATEADD(SECOND, 5, @baseDate),
        31 + (@i % 3),
        @emp,
        @baseDate,
        CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
        CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
        'SHIFT-A',
        0,
        '72.877655',
        '19.076090',
        -1,
        DATEADD(SECOND, 5, @baseDate),
        DATEADD(SECOND, 5, @baseDate),
        'Mumbai Office',
        36.5,
        1
    );

    SET @i = @i + 1;
END

PRINT 'Inserted 60 rows into dbo.DeviceLogs_5_2026';
GO

-- ============================================================================
-- STEP 6: VERIFY ROW COUNTS
-- ============================================================================
SELECT 'DeviceLogs_3_2026' AS TableName, COUNT(*) AS TotalRows FROM dbo.DeviceLogs_3_2026
UNION ALL
SELECT 'DeviceLogs_4_2026', COUNT(*) FROM dbo.DeviceLogs_4_2026
UNION ALL
SELECT 'DeviceLogs_5_2026', COUNT(*) FROM dbo.DeviceLogs_5_2026;
GO