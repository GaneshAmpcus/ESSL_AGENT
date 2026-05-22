USE hrms;
GO

-- ============================================================================
-- CREATE dbo.Devices TABLE IF NOT EXISTS
-- ============================================================================

IF NOT EXISTS (
    SELECT 1
    FROM sys.objects
    WHERE object_id = OBJECT_ID(N'dbo.Devices')
      AND type = 'U'
)
BEGIN
    CREATE TABLE dbo.Devices
    (
        DeviceId                INT IDENTITY(1,1) PRIMARY KEY,
        DeviceFName             NVARCHAR(255),
        DevicesName             NVARCHAR(255),
        DeviceDirection         NVARCHAR(255),
        SerialNumber            NVARCHAR(255),
        ConnectionType          NVARCHAR(255),
        IpAddress               NVARCHAR(255),
        BaudRate                NVARCHAR(255),
        CommKey                 NVARCHAR(255),
        ComPort                 NVARCHAR(255),
        LastLogDownloadDate     DATETIME,
        C1                      NVARCHAR(255),
        C2                      NVARCHAR(255),
        C3                      NVARCHAR(255),
        C4                      NVARCHAR(255),
        C5                      NVARCHAR(255),
        C6                      NVARCHAR(255),
        C7                      NVARCHAR(255),
        TransactionStamp        NVARCHAR(50),
        LastPing                DATETIME,
        DeviceType              NVARCHAR(255),
        OpStamp                 NVARCHAR(255),
        DownLoadType            INT,
        Timezone                NVARCHAR(50),
        DeviceLocation          NVARCHAR(50),
        TimeOut                 NVARCHAR(50),
        FaceDeviceType          NVARCHAR(255),
        MasterId                INT,
        AttPhotoStamp           NVARCHAR(255),
        DeviceActivationCode    NVARCHAR(255)
    );

    PRINT 'Created dbo.Devices';
END
ELSE
BEGIN
    PRINT 'dbo.Devices already exists';
END
GO

-- ============================================================================
-- INSERT DEVICE 31
-- ============================================================================

IF NOT EXISTS (
    SELECT 1
    FROM dbo.Devices
    WHERE DeviceId = 31
)
BEGIN
    SET IDENTITY_INSERT dbo.Devices ON;

    INSERT INTO dbo.Devices
    (
        DeviceId,
        DeviceFName,
        DevicesName,
        DeviceDirection,
        SerialNumber,
        ConnectionType,
        IpAddress,
        BaudRate,
        CommKey,
        ComPort,
        LastLogDownloadDate,
        TransactionStamp,
        LastPing,
        DeviceType,
        DownLoadType,
        Timezone,
        DeviceLocation,
        TimeOut,
        FaceDeviceType,
        DeviceActivationCode
    )
    VALUES
    (
        31,
        'Mumbai HQ Gate 1',
        'HQ-GATE-1',
        'IN/OUT',
        'SN-00031',
        'TCP/IP',
        '192.168.1.31',
        '115200',
        '0',
        'COM1',
        GETDATE(),
        'TS-31',
        GETDATE(),
        'FACE',
        1,
        'IST',
        'Mumbai HQ - Gate 1',
        '30',
        'Face Recognition',
        'ACT-31'
    );

    SET IDENTITY_INSERT dbo.Devices OFF;

    PRINT 'Inserted DeviceId 31';
END
ELSE
BEGIN
    PRINT 'DeviceId 31 already exists';
END
GO

-- ============================================================================
-- INSERT DEVICE 32
-- ============================================================================

IF NOT EXISTS (
    SELECT 1
    FROM dbo.Devices
    WHERE DeviceId = 32
)
BEGIN
    SET IDENTITY_INSERT dbo.Devices ON;

    INSERT INTO dbo.Devices
    (
        DeviceId,
        DeviceFName,
        DevicesName,
        DeviceDirection,
        SerialNumber,
        ConnectionType,
        IpAddress,
        BaudRate,
        CommKey,
        ComPort,
        LastLogDownloadDate,
        TransactionStamp,
        LastPing,
        DeviceType,
        DownLoadType,
        Timezone,
        DeviceLocation,
        TimeOut,
        FaceDeviceType,
        DeviceActivationCode
    )
    VALUES
    (
        32,
        'Mumbai HQ Gate 2',
        'HQ-GATE-2',
        'IN/OUT',
        'SN-00032',
        'TCP/IP',
        '192.168.1.32',
        '115200',
        '0',
        'COM1',
        GETDATE(),
        'TS-32',
        GETDATE(),
        'FACE+FINGERPRINT',
        1,
        'IST',
        'Mumbai HQ - Gate 2',
        '30',
        'Hybrid',
        'ACT-32'
    );

    SET IDENTITY_INSERT dbo.Devices OFF;

    PRINT 'Inserted DeviceId 32';
END
ELSE
BEGIN
    PRINT 'DeviceId 32 already exists';
END
GO

-- ============================================================================
-- VERIFY
-- ============================================================================

SELECT
    DeviceId,
    DeviceFName,
    DevicesName,
    DeviceType,
    IpAddress,
    DeviceLocation,
    LastLogDownloadDate
FROM dbo.Devices
ORDER BY DeviceId;
GO