-- ==============================================================================
-- CƠ SỞ DỮ LIỆU TỔNG HỢP: NHẬN DIỆN BIỂN SỐ XE AI & QUẢN LÝ BÃI ĐỖ XE
-- ==============================================================================

DROP DATABASE IF EXISTS HTTT_QuanLyBaiXe_AI;
CREATE DATABASE HTTT_QuanLyBaiXe_AI 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE HTTT_QuanLyBaiXe_AI;

-- =======================================================
-- PHẦN 1: QUẢN LÝ HỆ THỐNG & TÀI KHOẢN (Đã thêm Đăng Nhập/Đăng Xuất)
-- =======================================================

-- 1. BẢNG NHÂN VIÊN
CREATE TABLE NHAN_VIEN (
    MaNV VARCHAR(20) PRIMARY KEY,
    HoTen NVARCHAR(100) NOT NULL,
    TaiKhoan VARCHAR(50) UNIQUE NOT NULL,
    MatKhau VARCHAR(255) NOT NULL,
    VaiTro ENUM('Admin', 'QuanLy', 'BaoVe') DEFAULT 'BaoVe',
    TrangThai ENUM('HoatDong', 'NghiViec') DEFAULT 'HoatDong',
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. BẢNG LỊCH SỬ ĐĂNG NHẬP / ĐĂNG XUẤT (BẢNG MỚI THÊM)
CREATE TABLE LICH_SU_DANG_NHAP (
    MaPhien INT PRIMARY KEY AUTO_INCREMENT,
    MaNV VARCHAR(20) NOT NULL,
    ThoiGianDangNhap DATETIME DEFAULT CURRENT_TIMESTAMP,
    ThoiGianDangXuat DATETIME NULL,
    DiaChiIP VARCHAR(50) COMMENT 'Lưu IP máy tính/điện thoại đăng nhập',
    TrangThai ENUM('ThanhCong', 'SaiMatKhau', 'BiKhoa') DEFAULT 'ThanhCong',
    
    INDEX idx_MaNV (MaNV),
    INDEX idx_ThoiGian (ThoiGianDangNhap DESC),
    
    CONSTRAINT FK_DangNhap_NhanVien FOREIGN KEY (MaNV) 
        REFERENCES NHAN_VIEN(MaNV) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =======================================================
-- PHẦN 2: DỮ LIỆU DANH MỤC & NHẬN DIỆN CỦA AI
-- =======================================================

-- 3. BẢNG PROVINCES (Tỉnh/Thành Phố)
CREATE TABLE provinces (
    code VARCHAR(10) PRIMARY KEY COMMENT 'Mã tỉnh (51, 29, 33...)',
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    region VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. BẢNG VEHICLE_TYPES (Loại Xe AI nhận diện)
CREATE TABLE vehicle_types (
    type_name VARCHAR(50) PRIMARY KEY COMMENT 'Ô tô con, Xe máy, Xe tải...',
    description VARCHAR(255),
    seats INT,
    max_weight DECIMAL(10,2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. BẢNG PLATES (Danh sách Biển số AI từng quét được)
CREATE TABLE plates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    plate_text VARCHAR(20) NOT NULL UNIQUE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    detection_count INT DEFAULT 1,
    confidence FLOAT DEFAULT 0.95,
    province_code VARCHAR(10),
    vehicle_type VARCHAR(50),
    
    INDEX idx_plate_text (plate_text),
    
    CONSTRAINT fk_plates_province FOREIGN KEY (province_code) 
        REFERENCES provinces(code) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_plates_vehicle_type FOREIGN KEY (vehicle_type) 
        REFERENCES vehicle_types(type_name) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. BẢNG DETECTIONS (Nhật ký phát hiện thô từ Camera)
CREATE TABLE detections (
    id INT PRIMARY KEY AUTO_INCREMENT,
    plate_id INT NOT NULL,
    plate_text VARCHAR(20) NOT NULL,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT DEFAULT 0.95,
    camera_source VARCHAR(100),
    frame_number INT,
    raw_text VARCHAR(50),
    
    INDEX idx_detected_at (detected_at DESC),
    
    CONSTRAINT fk_detections_plate FOREIGN KEY (plate_id) 
        REFERENCES plates(id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. BẢNG STATISTICS (Thống Kê Nhận Diện AI)
CREATE TABLE statistics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date_stat DATE NOT NULL UNIQUE,
    total_plates INT DEFAULT 0,
    total_detections INT DEFAULT 0,
    avg_confidence FLOAT DEFAULT 0,
    top_plate VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =======================================================
-- PHẦN 3: NGHIỆP VỤ QUẢN LÝ BÃI ĐỖ XE
-- =======================================================

-- 8. BẢNG CƯ DÂN
CREATE TABLE CU_DAN (
    MaCuDan VARCHAR(20) PRIMARY KEY,
    HoTen NVARCHAR(100) NOT NULL,
    CCCD VARCHAR(15) UNIQUE NOT NULL,
    SoDienThoai VARCHAR(15) NOT NULL,
    MaCanHo VARCHAR(20) NOT NULL,
    NgayDangKy DATETIME DEFAULT CURRENT_TIMESTAMP,
    TrangThai ENUM('HoatDong', 'TamKhoa') DEFAULT 'HoatDong'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. BẢNG BẢNG GIÁ
CREATE TABLE BANG_GIA (
    MaGia VARCHAR(20) PRIMARY KEY,
    LoaiXe ENUM('Oto', 'XeMay') NOT NULL,
    LoaiChuXe ENUM('CuDan', 'VangLai') NOT NULL,
    HinhThuc ENUM('TheoLuot', 'TheoThang') NOT NULL,
    DonGia DECIMAL(10,2) NOT NULL,
    MoTa NVARCHAR(255),
    NgayApDung DATETIME DEFAULT CURRENT_TIMESTAMP,
    TrangThai ENUM('DangApDung', 'NgungApDung') DEFAULT 'DangApDung'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. BẢNG PHƯƠNG TIỆN (Gắn Biển Số Với Cư Dân)
CREATE TABLE PHUONG_TIEN (
    BienSoXe VARCHAR(20) PRIMARY KEY,
    MaCuDan VARCHAR(20) NOT NULL, 
    LoaiXe ENUM('Oto', 'XeMay') NOT NULL,
    MauXe NVARCHAR(50),
    MaTheRFID VARCHAR(50) UNIQUE NOT NULL,
    NgayHetHan DATETIME NOT NULL, 
    TrangThaiHopLe BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT FK_PHUONG_TIEN_CUDAN FOREIGN KEY (MaCuDan) 
        REFERENCES CU_DAN(MaCuDan) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. BẢNG LỊCH SỬ RA VÀO (Giao dịch ra vào bãi - Liên kết với AI)
CREATE TABLE LICH_SU_RA_VAO (
    MaGiaoDich VARCHAR(30) PRIMARY KEY,
    BienSoXe VARCHAR(20) NOT NULL COMMENT 'Có thể JOIN với bảng plates của AI', 
    MaTheRFID VARCHAR(50) NOT NULL,
    LoaiKhach ENUM('CuDan', 'VangLai') NOT NULL,
    
    ThoiGianVao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    AnhVao VARCHAR(255) NOT NULL COMMENT 'Đường dẫn ảnh Camera chụp', 
    MaNV_XacNhanVao VARCHAR(20), 

    ThoiGianRa DATETIME NULL,
    AnhRa VARCHAR(255) NULL,
    MaNV_XacNhanRa VARCHAR(20) NULL,
    
    TrangThai ENUM('DangTrongBai', 'DaRa') DEFAULT 'DangTrongBai',
    
    CONSTRAINT FK_LICH_SU_NV_VAO FOREIGN KEY (MaNV_XacNhanVao) 
        REFERENCES NHAN_VIEN(MaNV) ON DELETE SET NULL,
    CONSTRAINT FK_LICH_SU_NV_RA FOREIGN KEY (MaNV_XacNhanRa) 
        REFERENCES NHAN_VIEN(MaNV) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. BẢNG HÓA ĐƠN
CREATE TABLE HOA_DON (
    MaHoaDon VARCHAR(30) PRIMARY KEY,
    MaGiaoDich VARCHAR(30) NOT NULL, 
    MaGia VARCHAR(20) NOT NULL,
    MaNV_ThuTien VARCHAR(20),
    
    TongTien DECIMAL(10,2) NOT NULL,
    ThoiGianThanhToan DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PhuongThucThanhToan ENUM('TienMat', 'ChuyenKhoan', 'VeThang') DEFAULT 'TienMat',
    TrangThai ENUM('DaThanhToan', 'ChuaThanhToan', 'Huy') DEFAULT 'DaThanhToan',
    
    CONSTRAINT FK_HOADON_GIAODICH FOREIGN KEY (MaGiaoDich) 
        REFERENCES LICH_SU_RA_VAO(MaGiaoDich) ON DELETE RESTRICT,
    CONSTRAINT FK_HOADON_BANGGIA FOREIGN KEY (MaGia) 
        REFERENCES BANG_GIA(MaGia) ON DELETE RESTRICT,
    CONSTRAINT FK_HOADON_NHANVIEN FOREIGN KEY (MaNV_ThuTien) 
        REFERENCES NHAN_VIEN(MaNV) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =======================================================
-- PHẦN 4: TRIGGERS BẢO VỆ TOÀN VẸN DỮ LIỆU
-- =======================================================

DELIMITER $$
CREATE TRIGGER trg_KhongXoaCuDan_KhiXeTrongBai
BEFORE DELETE ON CU_DAN
FOR EACH ROW
BEGIN
    DECLARE xeTrongBai INT;
    
    SELECT COUNT(*) INTO xeTrongBai
    FROM PHUONG_TIEN pt
    JOIN LICH_SU_RA_VAO ls ON pt.BienSoXe = ls.BienSoXe
    WHERE pt.MaCuDan = OLD.MaCuDan AND ls.TrangThai = 'DangTrongBai';
    
    IF xeTrongBai > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Lỗi: Không thể xóa Cư dân vì xe của họ đang nằm trong bãi!';
    END IF;
END$$
DELIMITER ;

-- =======================================================
-- PHẦN 5: DỮ LIỆU MẪU (OPTIONAL)
-- =======================================================

-- Insert nhân viên mẫu
INSERT INTO NHAN_VIEN (MaNV, HoTen, TaiKhoan, MatKhau, VaiTro) VALUES
('NV001', 'Nguyễn Văn A', 'admin', 'admin123', 'Admin'),
('NV002', 'Trần Thị B', 'manager', 'manager123', 'QuanLy'),
('NV003', 'Lê Văn C', 'guard', 'guard123', 'BaoVe');

-- Insert tỉnh/thành phố
INSERT INTO provinces (code, name, name_en, region) VALUES
('29', 'Thành phố Hải Phòng', 'Hai Phong', 'Bắc'),
('30', 'Thành phố Hà Nội', 'Hanoi', 'Bắc'),
('51', 'Thành phố Hồ Chí Minh', 'Ho Chi Minh City', 'Nam Bộ'),
('46', 'Thành phố Đà Nẵng', 'Da Nang', 'Trung');

-- Insert loại xe
INSERT INTO vehicle_types (type_name, description, seats, max_weight) VALUES
('Ô tô con', 'Xe con đặc dụng', 4, 1.50),
('Ô tô khách', 'Xe chở khách từ 9 chỗ', 30, 10.00),
('Ô tô tải', 'Xe tải hàng hóa', 2, 25.00),
('Xe máy', 'Xe máy, xe scooter', 2, 0.20);

-- Insert bảng giá
INSERT INTO BANG_GIA (MaGia, LoaiXe, LoaiChuXe, HinhThuc, DonGia, MoTa) VALUES
('GIA001', 'Oto', 'CuDan', 'TheoThang', 500000, 'Giá dân cư - ô tô - theo tháng'),
('GIA002', 'Oto', 'VangLai', 'TheoLuot', 50000, 'Giá khách vãng lai - ô tô - theo lượt'),
('GIA003', 'XeMay', 'CuDan', 'TheoThang', 100000, 'Giá dân cư - xe máy - theo tháng'),
('GIA004', 'XeMay', 'VangLai', 'TheoLuot', 10000, 'Giá khách vãng lai - xe máy - theo lượt');

-- Insert cư dân mẫu
INSERT INTO CU_DAN (MaCuDan, HoTen, CCCD, SoDienThoai, MaCanHo) VALUES
('CD001', 'Phạm Tuấn Anh', '0123456789001', '0912345601', 'A101'),
('CD002', 'Nguyễn Hồng Hạnh', '0123456789002', '0912345602', 'A102'),
('CD003', 'Trương Văn Lâm', '0123456789003', '0912345603', 'B201');

-- Insert phương tiện mẫu
INSERT INTO PHUONG_TIEN (BienSoXe, MaCuDan, LoaiXe, MauXe, MaTheRFID, NgayHetHan, TrangThaiHopLe) VALUES
('51G-12345', 'CD001', 'Oto', 'Trắng', 'RFID001', '2026-12-31', TRUE),
('51H-67890', 'CD002', 'Oto', 'Đen', 'RFID002', '2026-12-31', TRUE),
('51K-99999', 'CD003', 'XeMay', 'Xanh', 'RFID003', '2026-12-31', TRUE);

-- Insert lịch sử ra vào mẫu
INSERT INTO LICH_SU_RA_VAO (MaGiaoDich, BienSoXe, MaTheRFID, LoaiKhach, AnhVao, MaNV_XacNhanVao, TrangThai) VALUES
('GD001', '51G-12345', 'RFID001', 'CuDan', '/images/in_51G12345_001.jpg', 'NV003', 'DangTrongBai'),
('GD002', '51H-67890', 'RFID002', 'CuDan', '/images/in_51H67890_001.jpg', 'NV003', 'DangTrongBai');
