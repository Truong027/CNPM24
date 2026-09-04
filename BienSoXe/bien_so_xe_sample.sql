-- ==============================================================================
-- CƠ SỞ DỮ LIỆU TỔNG HỢP: NHẬN DIỆN BIỂN SỐ XE AI & QUẢN LÝ BÃI ĐỖ XE
-- PHIÊN BẢN FINAL: TÍCH HỢP AUTHENTICATION, OTP & RÀNG BUỘC KHÓA NGOẠI HOÀN CHỈNH
-- ==============================================================================

DROP DATABASE IF EXISTS HTTT_QuanLyBaiXe_AI;
CREATE DATABASE HTTT_QuanLyBaiXe_AI 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE HTTT_QuanLyBaiXe_AI;

-- =======================================================
-- PHẦN 1: QUẢN LÝ HỆ THỐNG, TÀI KHOẢN & BẢO MẬT (AUTH)
-- =======================================================

-- 1. BẢNG NHÂN VIÊN (Dùng cho Admin/Bảo vệ đăng nhập Web/Phần mềm)
CREATE TABLE NHAN_VIEN (
    MaNV VARCHAR(20) PRIMARY KEY,
    HoTen NVARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL COMMENT 'Dùng để lấy lại mật khẩu',
    TaiKhoan VARCHAR(50) UNIQUE NOT NULL,
    MatKhau VARCHAR(255) NOT NULL COMMENT 'Mã hóa Hash (Bcrypt/MD5)',
    VaiTro ENUM('Admin', 'QuanLy', 'BaoVe') DEFAULT 'BaoVe',
    TrangThai ENUM('HoatDong', 'NghiViec') DEFAULT 'HoatDong',
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. BẢNG CƯ DÂN (Dùng cho Khách hàng đăng ký App Mobile)
CREATE TABLE CU_DAN (
    MaCuDan VARCHAR(20) PRIMARY KEY,
    HoTen NVARCHAR(100) NOT NULL,
    CCCD VARCHAR(15) UNIQUE NOT NULL,
    SoDienThoai VARCHAR(15) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL COMMENT 'Dùng để lấy lại mật khẩu App',
    MaCanHo VARCHAR(20) NOT NULL,
    TaiKhoan VARCHAR(50) UNIQUE NULL COMMENT 'Tài khoản đăng nhập App',
    MatKhau VARCHAR(255) NULL COMMENT 'Mật khẩu đăng nhập App',
    NgayDangKy DATETIME DEFAULT CURRENT_TIMESTAMP,
    TrangThai ENUM('HoatDong', 'TamKhoa') DEFAULT 'HoatDong'
) ENGINE=InnoDB;

-- 3. BẢNG LỊCH SỬ ĐĂNG NHẬP / ĐĂNG XUẤT (Audit Log)
CREATE TABLE LICH_SU_DANG_NHAP (
    MaPhien INT PRIMARY KEY AUTO_INCREMENT,
    MaNV VARCHAR(20) NOT NULL,
    ThoiGianDangNhap DATETIME DEFAULT CURRENT_TIMESTAMP,
    ThoiGianDangXuat DATETIME NULL,
    DiaChiIP VARCHAR(50) COMMENT 'Lưu IP máy tính/điện thoại',
    TrangThai ENUM('ThanhCong', 'SaiMatKhau', 'BiKhoa') DEFAULT 'ThanhCong',
    
    CONSTRAINT FK_DangNhap_NhanVien FOREIGN KEY (MaNV) 
        REFERENCES NHAN_VIEN(MaNV) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 4. BẢNG QUẢN LÝ QUÊN MẬT KHẨU / XÁC THỰC OTP
CREATE TABLE QUAN_LY_OTP_TOKEN (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Email_Nhan VARCHAR(100) NOT NULL,
    LoaiTaiKhoan ENUM('NhanVien', 'CuDan') NOT NULL,
    MaOTP VARCHAR(6) NOT NULL COMMENT 'Mã số 6 chữ số gửi qua mail',
    ThoiGianTao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ThoiGianHetHan DATETIME NOT NULL COMMENT 'Thời gian hết hạn (VD: 5 phút)',
    TrangThai ENUM('ChuaSuDung', 'DaSuDung', 'DaHuy') DEFAULT 'ChuaSuDung',
    
    INDEX idx_Email (Email_Nhan),
    INDEX idx_OTP (MaOTP)
) ENGINE=InnoDB;

-- =======================================================
-- PHẦN 2: DỮ LIỆU DANH MỤC & NHẬN DIỆN CỦA AI
-- =======================================================

CREATE TABLE provinces (
    code VARCHAR(10) PRIMARY KEY COMMENT 'Mã tỉnh (51, 29, 33...)',
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    region VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE vehicle_types (
    type_name VARCHAR(50) PRIMARY KEY COMMENT 'Ô tô con, Xe máy...',
    description VARCHAR(255),
    seats INT,
    max_weight DECIMAL(10,2)
) ENGINE=InnoDB;

CREATE TABLE plates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    plate_text VARCHAR(20) NOT NULL UNIQUE, -- Khóa ngoại kết nối với Bãi xe
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
) ENGINE=InnoDB;

CREATE TABLE detections (
    id INT PRIMARY KEY AUTO_INCREMENT, -- Mã ảnh Camera AI quét được
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
) ENGINE=InnoDB;

CREATE TABLE statistics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date_stat DATE NOT NULL UNIQUE,
    total_plates INT DEFAULT 0,
    total_detections INT DEFAULT 0,
    avg_confidence FLOAT DEFAULT 0,
    top_plate VARCHAR(20)
) ENGINE=InnoDB;

-- =======================================================
-- PHẦN 3: NGHIỆP VỤ QUẢN LÝ BÃI ĐỖ XE
-- =======================================================

CREATE TABLE BANG_GIA (
    MaGia VARCHAR(20) PRIMARY KEY,
    LoaiXe ENUM('Oto', 'XeMay') NOT NULL,
    LoaiChuXe ENUM('CuDan', 'VangLai') NOT NULL,
    HinhThuc ENUM('TheoLuot', 'TheoThang') NOT NULL,
    DonGia DECIMAL(10,2) NOT NULL,
    MoTa NVARCHAR(255),
    NgayApDung DATETIME DEFAULT CURRENT_TIMESTAMP,
    TrangThai ENUM('DangApDung', 'NgungApDung') DEFAULT 'DangApDung'
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

-- =======================================================
-- BẢNG GIAO THOA (THE BRIDGE): LỊCH SỬ RA VÀO
-- Nơi AI và Nghiệp vụ Bãi Xe bắt tay nhau
-- =======================================================
CREATE TABLE LICH_SU_RA_VAO (
    MaGiaoDich VARCHAR(30) PRIMARY KEY,
    BienSoXe VARCHAR(20) NOT NULL, 
    MaTheRFID VARCHAR(50) NOT NULL,
    LoaiKhach ENUM('CuDan', 'VangLai') NOT NULL,
    
    -- Liên kết sự kiện AI quét camera
    DetectionID_Vao INT NOT NULL COMMENT 'ID ảnh AI chụp lúc vào',
    DetectionID_Ra INT NULL COMMENT 'ID ảnh AI chụp lúc ra',

    ThoiGianVao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    AnhVao VARCHAR(255) NOT NULL, 
    MaNV_XacNhanVao VARCHAR(20), 

    ThoiGianRa DATETIME NULL,
    AnhRa VARCHAR(255) NULL,
    MaNV_XacNhanRa VARCHAR(20) NULL,
    
    TrangThai ENUM('DangTrongBai', 'DaRa') DEFAULT 'DangTrongBai',
    
    -- Khóa ngoại nối với bảng Biển số của AI
    CONSTRAINT FK_LSRV_AI_Plates FOREIGN KEY (BienSoXe) 
        REFERENCES plates(plate_text) ON UPDATE CASCADE ON DELETE RESTRICT,
        
    -- Khóa ngoại nối với ID Camera AI lúc vào/ra
    CONSTRAINT FK_LSRV_AI_DetectVao FOREIGN KEY (DetectionID_Vao) 
        REFERENCES detections(id) ON DELETE RESTRICT,
    CONSTRAINT FK_LSRV_AI_DetectRa FOREIGN KEY (DetectionID_Ra) 
        REFERENCES detections(id) ON DELETE RESTRICT,

    -- Khóa ngoại nối với Nhân viên quản lý
    CONSTRAINT FK_LICH_SU_NV_VAO FOREIGN KEY (MaNV_XacNhanVao) 
        REFERENCES NHAN_VIEN(MaNV) ON DELETE SET NULL,
    CONSTRAINT FK_LICH_SU_NV_RA FOREIGN KEY (MaNV_XacNhanRa) 
        REFERENCES NHAN_VIEN(MaNV) ON DELETE SET NULL
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

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
        SET MESSAGE_TEXT = 'Lỗi Toàn Vẹn: Không thể xóa Cư dân vì xe của họ đang nằm trong bãi!';
    END IF;
END$$
DELIMITER ;