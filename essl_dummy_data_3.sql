USE ESSL;
GO

-- ============================================================================
-- ADD 60 MORE ROWS TO DeviceLogs_3_2026 (continuing from row 61)
-- ============================================================================
DECLARE @i INT = 1;
DECLARE @emp VARCHAR(20);
DECLARE @baseDate DATETIME;

WHILE @i <= 60
BEGIN
    SET @emp = 'PTSPL000' + CAST(((@i - 1) % 5) + 1 AS VARCHAR(1));
    SET @baseDate = DATEADD(MINUTE, @i * 30, '2026-03-15 08:00:00');

    INSERT INTO dbo.DeviceLogs_3_2026
    (DownloadDate, DeviceId, UserId, LogDate, Direction, AttDirection,
     WorkCode, UpdateFlag, Longitude, Latitude, IsApproved,
     CreatedDate, LastModifiedDate, LocationAddress, BodyTemperature, IsMaskOn)
    VALUES
    (DATEADD(SECOND, 5, @baseDate), 31 + (@i % 3), @emp, @baseDate,
     CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
     CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
     'SHIFT-B', 0, '72.877655', '19.076090', -1,
     DATEADD(SECOND, 5, @baseDate), DATEADD(SECOND, 5, @baseDate),
     'Mumbai Office', 36.6, 1);

    SET @i = @i + 1;
END
GO

-- ============================================================================
-- ADD 60 MORE ROWS TO DeviceLogs_4_2026 (continuing from row 61)
-- ============================================================================
DECLARE @i INT = 1;
DECLARE @emp VARCHAR(20);
DECLARE @baseDate DATETIME;

WHILE @i <= 60
BEGIN
    SET @emp = 'PTSPL000' + CAST(((@i - 1) % 5) + 1 AS VARCHAR(1));
    SET @baseDate = DATEADD(MINUTE, @i * 30, '2026-04-15 08:00:00');

    INSERT INTO dbo.DeviceLogs_4_2026
    (DownloadDate, DeviceId, UserId, LogDate, Direction, AttDirection,
     WorkCode, UpdateFlag, Longitude, Latitude, IsApproved,
     CreatedDate, LastModifiedDate, LocationAddress, BodyTemperature, IsMaskOn)
    VALUES
    (DATEADD(SECOND, 5, @baseDate), 31 + (@i % 3), @emp, @baseDate,
     CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
     CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
     'SHIFT-B', 0, '72.877655', '19.076090', -1,
     DATEADD(SECOND, 5, @baseDate), DATEADD(SECOND, 5, @baseDate),
     'Mumbai Office', 36.6, 1);

    SET @i = @i + 1;
END
GO

-- ============================================================================
-- ADD 60 MORE ROWS TO DeviceLogs_5_2026 (continuing from row 61)
-- ============================================================================
DECLARE @i INT = 1;
DECLARE @emp VARCHAR(20);
DECLARE @baseDate DATETIME;

WHILE @i <= 60
BEGIN
    SET @emp = 'PTSPL000' + CAST(((@i - 1) % 5) + 1 AS VARCHAR(1));
    SET @baseDate = DATEADD(MINUTE, @i * 30, '2026-05-15 08:00:00');

    INSERT INTO dbo.DeviceLogs_5_2026
    (DownloadDate, DeviceId, UserId, LogDate, Direction, AttDirection,
     WorkCode, UpdateFlag, Longitude, Latitude, IsApproved,
     CreatedDate, LastModifiedDate, LocationAddress, BodyTemperature, IsMaskOn)
    VALUES
    (DATEADD(SECOND, 5, @baseDate), 31 + (@i % 3), @emp, @baseDate,
     CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
     CASE WHEN @i % 2 = 0 THEN 'in' ELSE 'out' END,
     'SHIFT-B', 0, '72.877655', '19.076090', -1,
     DATEADD(SECOND, 5, @baseDate), DATEADD(SECOND, 5, @baseDate),
     'Mumbai Office', 36.6, 1);

    SET @i = @i + 1;
END
GO

-- Verify
SELECT 'DeviceLogs_3_2026' AS TableName, COUNT(*) AS TotalRows FROM dbo.DeviceLogs_3_2026
UNION ALL
SELECT 'DeviceLogs_4_2026', COUNT(*) FROM dbo.DeviceLogs_4_2026
UNION ALL
SELECT 'DeviceLogs_5_2026', COUNT(*) FROM dbo.DeviceLogs_5_2026;
GO