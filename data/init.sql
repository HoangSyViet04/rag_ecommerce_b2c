-- 1. Tạo Database
CREATE DATABASE RagB2C_Inventory;
GO

-- 2. Chuyển sang dùng Database vừa tạo
USE RagB2C_Inventory;
GO

-- 3. Tạo bảng Products (Đã fix chuẩn SQL Server)
CREATE TABLE products (
    product_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    description NVARCHAR(MAX),
    category NVARCHAR(100),
    price DECIMAL(10, 2),
    status NVARCHAR(50) DEFAULT 'active',
    updated_at DATETIME DEFAULT GETDATE()
);
GO

-- 4. Bơm dữ liệu mồi (Nhớ có chữ N phía trước để không bị lỗi font Tiếng Việt)
INSERT INTO products (name, description, category, price)
VALUES (
    N'Tai nghe Bluetooth Sony',
    N'Tai nghe chống ồn chủ động, pin 30h',
    N'dien_tu',
    3500000
),
(
    N'Balo chống nước',
    N'Balo laptop 15.6 inch, chất liệu vải dù',
    N'thoi_trang',
    450000
);
GO

-- 5. Tạo bảng Lịch sử Chat 
CREATE TABLE ChatHistory (
    MessageID INT IDENTITY(1,1) PRIMARY KEY,
    SessionID VARCHAR(50) NOT NULL,
    SenderRole VARCHAR(10) NOT NULL,
    Content NVARCHAR(MAX) NOT NULL,
    CreatedAt DATETIME DEFAULT GETDATE()
);
GO