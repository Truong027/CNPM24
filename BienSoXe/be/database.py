import mysql.connector
from mysql.connector import Error
import os
import time
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

PROVINCE_METADATA = {
    '29': {'name': 'Thành phố Hải Phòng', 'name_en': 'Hai Phong', 'region': 'Bắc'},
    '30': {'name': 'Thành phố Hà Nội', 'name_en': 'Hanoi', 'region': 'Bắc'},
    '43': {'name': 'Thành phố Đà Nẵng', 'name_en': 'Da Nang', 'region': 'Trung'},
    '46': {'name': 'Thành phố Đà Nẵng', 'name_en': 'Da Nang', 'region': 'Trung'},
    '51': {'name': 'Thành phố Hồ Chí Minh', 'name_en': 'Ho Chi Minh City', 'region': 'Nam Bộ'},
    '59': {'name': 'Thành phố Hồ Chí Minh', 'name_en': 'Ho Chi Minh City', 'region': 'Nam Bộ'},
    '92': {'name': 'Tỉnh Quảng Nam', 'name_en': 'Quang Nam', 'region': 'Trung'},
}

# ==================== CẤU HÌNH MYSQL AN TOÀN ====================
def _load_env():
    """Tự động nạp cấu hình từ .env nếu có (không lộ thông tin nhạy cảm lên Git)"""
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(cur_dir, '.env'),
        os.path.join(cur_dir, '..', '.env'),
        os.path.join(os.getcwd(), '.env')
    ]
    for env_path in candidates:
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            k, v = line.split('=', 1)
                            k, v = k.strip(), v.strip().strip("'\"")
                            if k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass
            break

_load_env()

MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'HTTT_QuanLyBaiXe_AI'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'autocommit': True
}

def get_db_connection():
    """Lấy kết nối đến MySQL database."""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Error as e:
        print(f"❌ Lỗi kết nối MySQL: {e}")
        return None

def init_db():
    """Khởi tạo bảng cơ sở dữ liệu với ràng buộc khóa ngoại."""
    conn = None
    
    try:
        # Kết nối để tạo database
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            port=MYSQL_CONFIG['port']
        )
        c = conn.cursor()
        
        # Tạo database
        c.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
        print(f"✅ Database '{MYSQL_CONFIG['database']}' đã được tạo/kiểm tra.")
        conn.close()
        
        # Kết nối đến database cụ thể
        conn = get_db_connection()
        if not conn:
            print("❌ Không thể kết nối đến database.")
            return
            
        c = conn.cursor()
        
        # ====== BẢNG 1: PROVINCES (Tạo Trước) ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS provinces (
            id INT PRIMARY KEY AUTO_INCREMENT,
            code VARCHAR(10) NOT NULL UNIQUE COMMENT 'Mã tỉnh (51, 29, 33...)',
            name VARCHAR(100) NOT NULL COMMENT 'Tên tỉnh thành',
            name_en VARCHAR(100) COMMENT 'Tên tiếng Anh',
            region VARCHAR(50) COMMENT 'Vùng (Bắc, Trung, Nam)',
            INDEX idx_code (code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'provinces' đã được tạo.")
        
        # ====== BẢNG 2: VEHICLE_TYPES (Tạo Trước) ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_types (
            id INT PRIMARY KEY AUTO_INCREMENT,
            type_name VARCHAR(50) NOT NULL UNIQUE COMMENT 'Ô tô, Xe máy, Xe tải...',
            description VARCHAR(255),
            seats INT COMMENT 'Số chỗ ngồi (nếu là ô tô)',
            max_weight DECIMAL(10,2) COMMENT 'Trọng tải tối đa (tấn)'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'vehicle_types' đã được tạo.")
        
        # ====== BẢNG 3: PLATES (Tạo Sau Khi provinces & vehicle_types) ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS plates (
            id INT PRIMARY KEY AUTO_INCREMENT,
            plate_text VARCHAR(20) NOT NULL UNIQUE COMMENT 'Biển số (51G-12345)',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời gian phát hiện',
            detection_count INT DEFAULT 1 COMMENT 'Số lần phát hiện',
            confidence FLOAT DEFAULT 0.95 COMMENT 'Độ tin cậy nhận diện (0-1)',
            province_code VARCHAR(10) COMMENT 'Mã tỉnh (51=TP.HCM)',
            vehicle_type VARCHAR(50) COMMENT 'Loại xe (Ô tô, Xe máy...)',
            
            INDEX idx_timestamp (timestamp DESC),
            INDEX idx_plate_text (plate_text),
            INDEX idx_province (province_code),
            INDEX idx_vehicle_type (vehicle_type),
            
            CONSTRAINT fk_plates_province 
                FOREIGN KEY (province_code) REFERENCES provinces(code) 
                ON UPDATE CASCADE ON DELETE SET NULL,
            
            CONSTRAINT fk_plates_vehicle_type 
                FOREIGN KEY (vehicle_type) REFERENCES vehicle_types(type_name) 
                ON UPDATE CASCADE ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'plates' đã được tạo.")

        # Seed các tỉnh phổ biến để UI luôn hiển thị tên đầy đủ.
        seed_default_provinces(c)

        # ====== BẢNG 4: VEHICLES ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            plate_text VARCHAR(20) PRIMARY KEY COMMENT 'Biển số xe',
            owner_name VARCHAR(100) COMMENT 'Tên chủ xe',
            vehicle_type VARCHAR(50) COMMENT 'Loại xe',
            color VARCHAR(50) COMMENT 'Màu xe',
            registration_date DATE COMMENT 'Ngày đăng ký',
            status VARCHAR(30) DEFAULT 'Hoạt động' COMMENT 'Trạng thái',
            province_code VARCHAR(10) COMMENT 'Mã tỉnh',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            INDEX idx_vehicle_type (vehicle_type),
            INDEX idx_vehicle_status (status),
            INDEX idx_vehicle_province (province_code),

            CONSTRAINT fk_vehicles_province
                FOREIGN KEY (province_code) REFERENCES provinces(code)
                ON UPDATE CASCADE ON DELETE SET NULL,

            CONSTRAINT fk_vehicles_type
                FOREIGN KEY (vehicle_type) REFERENCES vehicle_types(type_name)
                ON UPDATE CASCADE ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'vehicles' đã được tạo.")

        seed_default_vehicles(c)
        
        # ====== BẢNG 5: DETECTIONS ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INT PRIMARY KEY AUTO_INCREMENT,
            plate_id INT NOT NULL,
            plate_text VARCHAR(20) NOT NULL,
            detected_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời gian phát hiện',
            confidence FLOAT DEFAULT 0.95,
            camera_source VARCHAR(100) COMMENT 'Nguồn camera (webcam/ipcam)',
            frame_number INT COMMENT 'Số khung hình',
            raw_text VARCHAR(50) COMMENT 'Text gốc trước chuẩn hóa',
            
            INDEX idx_detected_at (detected_at DESC),
            INDEX idx_plate_text (plate_text),
            INDEX idx_camera (camera_source),
            
            CONSTRAINT fk_detections_plate
                FOREIGN KEY (plate_id) REFERENCES plates(id) 
                ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'detections' đã được tạo.")
        
        # ====== BẢNG 6: STATISTICS ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INT PRIMARY KEY AUTO_INCREMENT,
            date_stat DATE NOT NULL COMMENT 'Ngày thống kê',
            total_plates INT DEFAULT 0 COMMENT 'Tổng biển số độc lập',
            total_detections INT DEFAULT 0 COMMENT 'Tổng số lần phát hiện',
            avg_confidence FLOAT DEFAULT 0 COMMENT 'Độ tin cậy trung bình',
            top_plate VARCHAR(20) COMMENT 'Biển số phát hiện nhiều nhất',
            UNIQUE KEY unique_date (date_stat),
            INDEX idx_date (date_stat DESC)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'statistics' đã được tạo.")

        # ====== BẢNG 7: APP_USERS ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS app_users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            role VARCHAR(30) DEFAULT 'Admin',
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_username (username)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'app_users' đã được tạo.")

        # ====== THAY ĐỔI CẤU TRÚC BẢNG VEHICLES (TỰ ĐỘNG NÂNG CẤP) ======
        try:
            c.execute("SHOW COLUMNS FROM vehicles LIKE 'group_type'")
            if not c.fetchone():
                c.execute("ALTER TABLE vehicles ADD COLUMN group_type VARCHAR(20) DEFAULT 'Normal' COMMENT 'Normal, Whitelist, Blacklist'")
                print("✅ Đã thêm cột group_type vào bảng vehicles.")
        except Error as e:
            print(f"⚠️ Lỗi nâng cấp cột group_type: {e}")

        try:
            c.execute("SHOW COLUMNS FROM vehicles LIKE 'monthly_ticket_expiry'")
            if not c.fetchone():
                c.execute("ALTER TABLE vehicles ADD COLUMN monthly_ticket_expiry DATE DEFAULT NULL COMMENT 'Hạn vé tháng'")
                print("✅ Đã thêm cột monthly_ticket_expiry vào bảng vehicles.")
        except Error as e:
            print(f"⚠️ Lỗi nâng cấp cột monthly_ticket_expiry: {e}")

        # ====== BẢNG 8: PARKING_SESSIONS ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS parking_sessions (
            id INT PRIMARY KEY AUTO_INCREMENT,
            plate_text VARCHAR(20) NOT NULL,
            check_in_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            check_out_time DATETIME DEFAULT NULL,
            duration_minutes INT DEFAULT NULL,
            fee DECIMAL(10,2) DEFAULT 0.00,
            status VARCHAR(20) DEFAULT 'Parked' COMMENT 'Parked, Completed',
            camera_in VARCHAR(100) DEFAULT NULL,
            camera_out VARCHAR(100) DEFAULT NULL,
            
            INDEX idx_plate_text (plate_text),
            INDEX idx_status (status),
            INDEX idx_check_in (check_in_time DESC),
            
            CONSTRAINT fk_sessions_plate FOREIGN KEY (plate_text) REFERENCES plates(plate_text)
                ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'parking_sessions' đã được tạo.")

        # ====== BẢNG 9: NHAN_VIEN (BẢO VỆ / NHÂN VIÊN TRỰC) ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS nhan_vien (
            MaNV VARCHAR(50) PRIMARY KEY,
            HoTen VARCHAR(100) NOT NULL,
            SoDienThoai VARCHAR(20),
            Email VARCHAR(100),
            CaTruc VARCHAR(50) DEFAULT 'Ca Sáng (06:00 - 14:00)',
            TaiKhoan VARCHAR(50) UNIQUE NOT NULL,
            MatKhau VARCHAR(255),
            VaiTro VARCHAR(30) DEFAULT 'Bảo vệ',
            TrangThai VARCHAR(30) DEFAULT 'HoatDong' COMMENT 'HoatDong, TamKhoa',
            NgayVaoLam DATE DEFAULT (CURRENT_DATE),
            INDEX idx_taikhoan (TaiKhoan)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'nhan_vien' đã được tạo/kiểm tra.")

        # Tự động nâng cấp cột cho bảng nhan_vien nếu bảng đã tồn tại từ trước
        try:
            c.execute("SHOW COLUMNS FROM nhan_vien")
            nv_existing = [r[0] for r in c.fetchall()]
            nv_needed = [
                ('CaTruc', "VARCHAR(50) DEFAULT 'Ca Sáng (06:00 - 14:00)'"),
                ('TaiKhoan', "VARCHAR(50) DEFAULT NULL"),
                ('MatKhau', "VARCHAR(255) DEFAULT NULL"),
                ('VaiTro', "VARCHAR(50) DEFAULT 'Bảo vệ'"),
                ('TrangThai', "VARCHAR(30) DEFAULT 'HoatDong'"),
                ('SoDienThoai', "VARCHAR(20) DEFAULT NULL"),
                ('Email', "VARCHAR(100) DEFAULT NULL"),
                ('NgayVaoLam', "DATE DEFAULT (CURRENT_DATE)")
            ]
            for col_name, col_def in nv_needed:
                if col_name not in nv_existing and (col_name != 'SoDienThoai' or 'SDT' not in nv_existing):
                    c.execute(f"ALTER TABLE nhan_vien ADD COLUMN {col_name} {col_def}")
                    print(f"✅ Đã nâng cấp thêm cột {col_name} vào bảng nhan_vien.")
                elif col_name in ['VaiTro', 'TrangThai', 'CaTruc']:
                    try:
                        c.execute(f"ALTER TABLE nhan_vien MODIFY COLUMN {col_name} {col_def}")
                    except Error:
                        pass
        except Error as e:
            print(f"⚠️ Lỗi nâng cấp cột nhan_vien: {e}")

        # ====== BẢNG 10: CU_DAN ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS cu_dan (
            MaCuDan VARCHAR(50) PRIMARY KEY,
            HoTen VARCHAR(100) NOT NULL,
            CCCD VARCHAR(20),
            SDT VARCHAR(20),
            SoDienThoai VARCHAR(20),
            Email VARCHAR(100),
            MaCanHo VARCHAR(50),
            TaiKhoan VARCHAR(50) UNIQUE,
            MatKhau VARCHAR(255),
            TrangThai VARCHAR(30) DEFAULT 'HoatDong',
            INDEX idx_taikhoan (TaiKhoan),
            INDEX idx_canho (MaCanHo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'cu_dan' đã được tạo/kiểm tra.")

        # Tự động nâng cấp cột cho bảng cu_dan nếu bảng đã tồn tại từ trước
        try:
            c.execute("SHOW COLUMNS FROM cu_dan")
            cd_existing = [r[0] for r in c.fetchall()]
            cd_needed = [
                ('TaiKhoan', "VARCHAR(50) DEFAULT NULL"),
                ('MatKhau', "VARCHAR(255) DEFAULT NULL"),
                ('TrangThai', "VARCHAR(30) DEFAULT 'HoatDong'"),
                ('MaCanHo', "VARCHAR(50) DEFAULT NULL"),
                ('CCCD', "VARCHAR(20) DEFAULT NULL"),
                ('SoDienThoai', "VARCHAR(20) DEFAULT NULL"),
                ('Email', "VARCHAR(100) DEFAULT NULL")
            ]
            for col_name, col_def in cd_needed:
                if col_name not in cd_existing and (col_name != 'SoDienThoai' or 'SDT' not in cd_existing):
                    c.execute(f"ALTER TABLE cu_dan ADD COLUMN {col_name} {col_def}")
                    print(f"✅ Đã nâng cấp thêm cột {col_name} vào bảng cu_dan.")
        except Error as e:
            print(f"⚠️ Lỗi nâng cấp cột cu_dan: {e}")

        # ====== BẢNG 11: CHUYEN_NHUONG_XE (ĐƠN CHUYỂN NHƯỢNG XE CƯ DÂN) ======
        c.execute('''
        CREATE TABLE IF NOT EXISTS chuyen_nhuong_xe (
            id INT PRIMARY KEY AUTO_INCREMENT,
            MaDon VARCHAR(50) UNIQUE NOT NULL,
            BienSoXe VARCHAR(20) NOT NULL,
            MaCuDanChuyen VARCHAR(50) NOT NULL,
            TenCuDanChuyen VARCHAR(100),
            CanHoChuyen VARCHAR(50),
            MaCuDanNhan VARCHAR(50) NOT NULL,
            TenCuDanNhan VARCHAR(100),
            CanHoNhan VARCHAR(50),
            NgayYeuCau DATETIME DEFAULT CURRENT_TIMESTAMP,
            NgayDuyet DATETIME DEFAULT NULL,
            NguoiDuyet VARCHAR(50) DEFAULT NULL,
            TrangThai VARCHAR(30) DEFAULT 'Pending' COMMENT 'Pending, Approved, Rejected',
            GhiChu TEXT,
            INDEX idx_bien_so (BienSoXe),
            INDEX idx_status (TrangThai),
            INDEX idx_chuyen (MaCuDanChuyen),
            INDEX idx_nhan (MaCuDanNhan)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bảng 'chuyen_nhuong_xe' đã được tạo.")

        # ====== CHUẨN HÓA TOÀN BỘ LOẠI XE: CHỈ DUY NHẤT "Ô TÔ CON" ======
        try:
            # Mở rộng cột LoaiXe và vehicle_type sang VARCHAR(50) để chứa tiếng Việt
            try:
                c.execute("ALTER TABLE phuong_tien MODIFY COLUMN LoaiXe VARCHAR(50) DEFAULT 'Ô tô con'")
            except Error:
                pass

            try:
                c.execute("ALTER TABLE vehicles MODIFY COLUMN vehicle_type VARCHAR(50) DEFAULT 'Ô tô con'")
            except Error:
                pass

            try:
                c.execute("ALTER TABLE plates MODIFY COLUMN vehicle_type VARCHAR(50) DEFAULT 'Ô tô con'")
            except Error:
                pass

            # Cập nhật bảng vehicle_types
            c.execute("""
                INSERT INTO vehicle_types (type_name, description, seats, max_weight)
                VALUES ('Ô tô con', 'Xe ô tô du lịch 4-7 chỗ', 5, 2.5)
                ON DUPLICATE KEY UPDATE description = VALUES(description)
            """)

            c.execute("UPDATE vehicles SET vehicle_type = 'Ô tô con' WHERE vehicle_type IS NULL OR vehicle_type != 'Ô tô con'")
            c.execute("UPDATE plates SET vehicle_type = 'Ô tô con' WHERE vehicle_type IS NULL OR vehicle_type != 'Ô tô con'")
            
            try:
                c.execute("UPDATE phuong_tien SET LoaiXe = 'Ô tô con' WHERE LoaiXe IS NULL OR LoaiXe != 'Ô tô con'")
            except Error:
                try:
                    c.execute("UPDATE phuong_tien SET LoaiXe = 'OTo' WHERE LoaiXe IS NULL OR LoaiXe != 'OTo'")
                except Error:
                    pass

            c.execute("DELETE FROM vehicle_types WHERE type_name != 'Ô tô con'")
            print("✅ Đã chuẩn hóa toàn bộ loại xe: Chỉ duy nhất 'Ô tô con'.")
        except Error as e:
            print(f"⚠️ Chuẩn hóa loại xe: {e}")

        seed_default_users(c)
        
        conn.commit()
        print(f"\n✅ Tất cả bảng đã được khởi tạo thành công với ràng buộc khóa ngoại!")
    
    except Error as e:
        print(f"❌ Lỗi khi khởi tạo CSDL: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

def seed_default_vehicles(cursor):
    """Chèn dữ liệu xe mẫu để giao diện Quản lý Xe có dữ liệu đồng bộ (chỉ ô tô con)."""
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    count = cursor.fetchone()[0]
    if count > 0:
        return

    sample_vehicles = [
        ('30A-12345', 'Nguyễn Văn A', 'Ô tô con', 'Đen', '2024-01-15', 'Hoạt động', '30'),
        ('51B-67890', 'Trần Thị B', 'Ô tô con', 'Trắng', '2024-02-20', 'Hoạt động', '51'),
        ('29C-54321', 'Lê Văn C', 'Ô tô con', 'Đỏ', '2024-03-10', 'Hoạt động', '29'),
        ('92D-98765', 'Phạm Thị D', 'Ô tô con', 'Xanh', '2024-01-25', 'Không hoạt động', '92'),
        ('43E-11223', 'Hoàng Văn E', 'Ô tô con', 'Vàng', '2024-04-05', 'Hoạt động', '43'),
    ]

    for plate_text, owner_name, vehicle_type, color, registration_date, status, province_code in sample_vehicles:
        cursor.execute("""
            INSERT INTO vehicles (plate_text, owner_name, vehicle_type, color, registration_date, status, province_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                owner_name = VALUES(owner_name),
                vehicle_type = VALUES(vehicle_type),
                color = VALUES(color),
                registration_date = VALUES(registration_date),
                status = VALUES(status),
                province_code = VALUES(province_code)
        """, (plate_text, owner_name, vehicle_type, color, registration_date, status, province_code))

def seed_default_provinces(cursor):
    """Chèn sẵn các tỉnh/thành phổ biến với tên đầy đủ."""
    for code, meta in PROVINCE_METADATA.items():
        cursor.execute("""
            INSERT INTO provinces (code, name, name_en, region)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                name_en = VALUES(name_en),
                region = VALUES(region)
        """, (code, meta['name'], meta.get('name_en'), meta.get('region')))

def seed_default_users(cursor):
    """Chèn tài khoản mặc định cho Admin, Bảo vệ và Cư dân nếu chưa có."""
    default_accounts = [
        ('admin', 'admin123', 'Admin User', 'admin@system.com', 'Admin'),
        ('baove1', 'baove123', 'Nguyễn Văn An', 'an.nguyen@security.com', 'Operator'),
        ('baove2', 'baove123', 'Trần Văn Bình', 'binh.tran@security.com', 'Operator'),
        ('cudan1', 'cudan123', 'Lê Văn Cư Dân', 'cudan1@resident.com', 'Resident')
    ]

    for username, raw_pass, full_name, email, role in default_accounts:
        try:
            cursor.execute("SELECT COUNT(*) FROM app_users WHERE username = %s", (username,))
            if cursor.fetchone()[0] == 0:
                pw_hash = generate_password_hash(raw_pass)
                cursor.execute("""
                    INSERT INTO app_users (username, password_hash, full_name, email, role, is_active)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                """, (username, pw_hash, full_name, email, role))
        except Error as e:
            print(f"⚠️ app_users seed warning: {e}")

        # Đồng bộ bảo vệ vào nhan_vien (chèn động theo các cột hiện có)
        if role == 'Operator':
            try:
                cursor.execute("SHOW COLUMNS FROM nhan_vien")
                nv_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
                
                if 'TaiKhoan' in nv_cols:
                    cursor.execute("SELECT COUNT(*) FROM nhan_vien WHERE TaiKhoan = %s", (username,))
                    if cursor.fetchone()[0] > 0:
                        continue

                ma_nv = "NV_" + username.upper()
                shift = 'Ca Sáng (06:00 - 14:00)' if '1' in username else 'Ca Chiều (14:00 - 22:00)'
                phone = '0912345678' if '1' in username else '0923456789'
                
                insert_data = {'MaNV': ma_nv, 'HoTen': full_name}
                if 'SoDienThoai' in nv_cols: insert_data['SoDienThoai'] = phone
                elif 'SDT' in nv_cols: insert_data['SDT'] = phone
                if 'Email' in nv_cols: insert_data['Email'] = email
                if 'CaTruc' in nv_cols: insert_data['CaTruc'] = shift
                if 'TaiKhoan' in nv_cols: insert_data['TaiKhoan'] = username
                if 'MatKhau' in nv_cols: insert_data['MatKhau'] = generate_password_hash(raw_pass)
                if 'VaiTro' in nv_cols: insert_data['VaiTro'] = 'Bảo vệ'
                if 'TrangThai' in nv_cols: insert_data['TrangThai'] = 'HoatDong'

                try:
                    cols_str = ", ".join(insert_data.keys())
                    placeholders = ", ".join(["%s"] * len(insert_data))
                    cursor.execute(f"INSERT INTO nhan_vien ({cols_str}) VALUES ({placeholders})", tuple(insert_data.values()))
                except Error as e_ins:
                    # Fallback nếu cột VaiTro là ENUM ('BaoVe' hoặc 'NhanVien')
                    if 'VaiTro' in insert_data:
                        try:
                            insert_data['VaiTro'] = 'BaoVe'
                            cols_str = ", ".join(insert_data.keys())
                            placeholders = ", ".join(["%s"] * len(insert_data))
                            cursor.execute(f"INSERT INTO nhan_vien ({cols_str}) VALUES ({placeholders})", tuple(insert_data.values()))
                        except Error:
                            del insert_data['VaiTro']
                            cols_str = ", ".join(insert_data.keys())
                            placeholders = ", ".join(["%s"] * len(insert_data))
                            cursor.execute(f"INSERT INTO nhan_vien ({cols_str}) VALUES ({placeholders})", tuple(insert_data.values()))
                    else:
                        print(f"⚠️ nhan_vien seed warning: {e_ins}")
            except Error as e:
                print(f"⚠️ nhan_vien seed warning: {e}")

        # Đồng bộ cư dân vào cu_dan (chèn động theo các cột hiện có)
        if role == 'Resident':
            try:
                cursor.execute("SHOW COLUMNS FROM cu_dan")
                cd_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
                
                if 'TaiKhoan' in cd_cols:
                    cursor.execute("SELECT COUNT(*) FROM cu_dan WHERE TaiKhoan = %s", (username,))
                    if cursor.fetchone()[0] > 0:
                        continue

                insert_data = {'MaCuDan': 'CD_1001', 'HoTen': full_name}
                if 'CCCD' in cd_cols: insert_data['CCCD'] = '001234567890'
                if 'SoDienThoai' in cd_cols: insert_data['SoDienThoai'] = '0934567890'
                elif 'SDT' in cd_cols: insert_data['SDT'] = '0934567890'
                if 'Email' in cd_cols: insert_data['Email'] = email
                if 'MaCanHo' in cd_cols: insert_data['MaCanHo'] = 'A-1205'
                if 'TaiKhoan' in cd_cols: insert_data['TaiKhoan'] = username
                if 'MatKhau' in cd_cols: insert_data['MatKhau'] = generate_password_hash(raw_pass)
                if 'TrangThai' in cd_cols: insert_data['TrangThai'] = 'HoatDong'

                cols_str = ", ".join(insert_data.keys())
                placeholders = ", ".join(["%s"] * len(insert_data))
                cursor.execute(f"INSERT INTO cu_dan ({cols_str}) VALUES ({placeholders})", tuple(insert_data.values()))
            except Error as e:
                print(f"⚠️ cu_dan seed warning: {e}")

def check_province_exists(province_code):
    """Kiểm tra tỉnh có tồn tại không."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM provinces WHERE code = %s", (province_code,))
        result = cursor.fetchone()
        return result is not None
    except Error as e:
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def check_vehicle_type_exists(vehicle_type):
    """Kiểm tra loại xe có tồn tại không."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM vehicle_types WHERE type_name = %s", (vehicle_type,))
        result = cursor.fetchone()
        return result is not None
    except Error as e:
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_or_update_province(code, name, name_en=None, region=None):
    """Thêm hoặc cập nhật tỉnh thành."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO provinces (code, name, name_en, region) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name), region = VALUES(region)
        """, (code, name, name_en, region))
        
        conn.commit()
        return True
    except Error as e:
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_or_update_vehicle_type(type_name, description=None, seats=None, max_weight=None):
    """Thêm hoặc cập nhật loại xe."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO vehicle_types (type_name, description, seats, max_weight) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE description = VALUES(description)
        """, (type_name, description, seats, max_weight))
        
        conn.commit()
        return True
    except Error as e:
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def upsert_vehicle(plate_text, owner_name=None, vehicle_type='Ô tô con', color=None,
                   registration_date=None, status='Hoạt động', province_code=None,
                   group_type='Normal', monthly_ticket_expiry=None, update_if_exists=True,
                   ma_cu_dan=None):
    """Thêm hoặc cập nhật xe trong bảng vehicles và đồng bộ bảng phuong_tien."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor(dictionary=True)
        
        args = (
            plate_text,
            owner_name or 'Chưa gán',
            vehicle_type,
            color or 'Chưa xác định',
            registration_date,
            status,
            province_code,
            group_type,
            monthly_ticket_expiry
        )
        
        if update_if_exists:
            cursor.execute("""
                INSERT INTO vehicles (
                    plate_text, owner_name, vehicle_type, color,
                    registration_date, status, province_code,
                    group_type, monthly_ticket_expiry
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    owner_name = VALUES(owner_name),
                    vehicle_type = VALUES(vehicle_type),
                    color = VALUES(color),
                    registration_date = VALUES(registration_date),
                    province_code = VALUES(province_code),
                    status = VALUES(status),
                    group_type = VALUES(group_type),
                    monthly_ticket_expiry = VALUES(monthly_ticket_expiry),
                    updated_at = CURRENT_TIMESTAMP
            """, args)
        else:
            cursor.execute("""
                INSERT IGNORE INTO vehicles (
                    plate_text, owner_name, vehicle_type, color,
                    registration_date, status, province_code,
                    group_type, monthly_ticket_expiry
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, args)
            
        # Đồng bộ sang bảng tiếng Việt: phuong_tien và cu_dan
        try:
            loai_xe_id = 'Oto' if 'tô' in (vehicle_type or '').lower() else 'XeMay'
            target_ma_cd = ma_cu_dan
            
            if not target_ma_cd:
                # 1. Kiểm tra xem phuong_tien đã có MaCuDan thực tế chưa
                cursor.execute("SELECT MaCuDan FROM phuong_tien WHERE BienSoXe = %s", (plate_text,))
                existing_pt = cursor.fetchone()
                if existing_pt and existing_pt["MaCuDan"]:
                    target_ma_cd = existing_pt["MaCuDan"]
                elif owner_name and owner_name != 'Chưa gán':
                    # 2. Tìm cư dân theo tên chủ xe
                    cursor.execute("SELECT MaCuDan FROM cu_dan WHERE HoTen = %s OR TaiKhoan = %s LIMIT 1", (owner_name, owner_name))
                    matching_cd = cursor.fetchone()
                    if matching_cd:
                        target_ma_cd = matching_cd["MaCuDan"]
                        
            if not target_ma_cd:
                target_ma_cd = "CD_" + plate_text.replace("-", "").replace(".", "")
                cursor.execute("""
                    INSERT IGNORE INTO cu_dan (MaCuDan, HoTen, CCCD, SoDienThoai, Email, MaCanHo, TrangThai)
                    VALUES (%s, %s, %s, '000', %s, 'Khach', 'HoatDong')
                """, (target_ma_cd, owner_name or 'Khách', target_ma_cd, f"{target_ma_cd}@guest.com"))
            
            cursor.execute("""
                INSERT INTO phuong_tien (BienSoXe, LoaiXe, MaCuDan, MauXe, NgayHetHan, TrangThaiHopLe)
                VALUES (%s, %s, %s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE 
                    MaCuDan = IF(VALUES(MaCuDan) IS NOT NULL, VALUES(MaCuDan), MaCuDan),
                    LoaiXe = VALUES(LoaiXe),
                    MauXe = VALUES(MauXe),
                    NgayHetHan = COALESCE(VALUES(NgayHetHan), NgayHetHan)
            """, (plate_text, loai_xe_id, target_ma_cd, color or 'Chưa xác định', monthly_ticket_expiry or '2099-12-31'))
        except Exception as e:
            print(f"Lỗi đồng bộ phuong_tien: {e}")

        conn.commit()
        return True
    except Error as e:
        print(f"Lỗi upsert_vehicle: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_vehicle(plate_text):
    """Xóa xe theo biển số."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vehicles WHERE plate_text = %s", (plate_text,))
        conn.commit()
        return True
    except Error:
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_province_name(province_code):
    """Lấy tên tỉnh từ mã tỉnh."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return PROVINCE_METADATA.get(province_code, {}).get('name')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM provinces WHERE code = %s", (province_code,))
        result = cursor.fetchone()
        if result and result[0]:
            return result[0]
        return PROVINCE_METADATA.get(province_code, {}).get('name')
    except Error as e:
        return PROVINCE_METADATA.get(province_code, {}).get('name')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_vehicle_type_info(vehicle_type):
    """Lấy thông tin loại xe."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicle_types WHERE type_name = %s", (vehicle_type,))
        result = cursor.fetchone()
        return result
    except Error as e:
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_plates_with_details():
    """Lấy tất cả biển số với chi tiết tỉnh, loại xe, nhóm xe và giao dịch đỗ xe gần nhất."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                p.id, p.plate_text, p.timestamp, p.detection_count, 
                p.confidence, p.province_code, p.vehicle_type,
                pr.name as province_name, vt.type_name, vt.seats, vt.max_weight,
                v.group_type, v.monthly_ticket_expiry, v.owner_name,
                s.status AS session_status, s.fee AS session_fee, s.check_in_time, 
                s.check_out_time, s.duration_minutes
            FROM plates p
            LEFT JOIN provinces pr ON p.province_code = pr.code
            LEFT JOIN vehicle_types vt ON p.vehicle_type = vt.type_name
            LEFT JOIN vehicles v ON p.plate_text = v.plate_text
            LEFT JOIN parking_sessions s ON s.id = (
                SELECT id FROM parking_sessions 
                WHERE plate_text = p.plate_text 
                ORDER BY check_in_time DESC LIMIT 1
            )
            ORDER BY p.timestamp DESC
        """)
        results = cursor.fetchall()
        return results
    except Error as e:
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_vehicles():
    """Lấy danh sách xe để hiển thị trên màn Quản Lý Xe."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                v.plate_text, v.owner_name, v.vehicle_type, v.color,
                v.registration_date, v.status, v.province_code,
                v.group_type, v.monthly_ticket_expiry,
                pr.name as province_name
            FROM vehicles v
            LEFT JOIN provinces pr ON v.province_code = pr.code
            ORDER BY v.updated_at DESC, v.registration_date DESC
        """)
        return cursor.fetchall()
    except Error:
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def authenticate_user(username, password):
    """Xác thực người dùng bằng password hash."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, password_hash, full_name, email, role, is_active
            FROM app_users
            WHERE username = %s
            LIMIT 1
        """, (username,))
        user = cursor.fetchone()
        if not user:
            return None
        if not user.get('is_active'):
            return None
        if user and check_password_hash(user['password_hash'], password):
            # Đồng bộ lịch sử đăng nhập vào bảng tiếng Việt: lich_su_dang_nhap
            try:
                # Tìm MaNV từ bảng nhan_vien bằng TaiKhoan (username)
                cursor.execute("SELECT MaNV FROM nhan_vien WHERE TaiKhoan = %s", (username,))
                nv = cursor.fetchone()
                if nv:
                    cursor.execute("""
                        INSERT INTO lich_su_dang_nhap (MaNV, DiaChiIP, TrangThai)
                        VALUES (%s, '127.0.0.1', 'ThanhCong')
                    """, (nv['MaNV'],))
                    conn.commit()
            except Exception as e:
                print(f"Lỗi đồng bộ lich_su_dang_nhap: {e}")
                
            user.pop('password_hash', None)
            return user
        return None
    except Error:
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def log_detection(plate_text, confidence=0.95, camera_source='webcam', frame_number=None, raw_text=None):
    """Lưu nhật ký phát hiện vào bảng detections."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM plates WHERE plate_text = %s LIMIT 1", (plate_text,))
        plate_row = cursor.fetchone()
        if not plate_row:
            return False

        plate_id = plate_row[0]
        cursor.execute("""
            INSERT INTO detections (plate_id, plate_text, confidence, camera_source, frame_number, raw_text)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (plate_id, plate_text, confidence, camera_source, frame_number, raw_text))
        conn.commit()
        return True
    except Error:
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_plate_detections(plate_text):
    """Lấy lịch sử chi tiết của một biển số."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM detections 
            WHERE plate_text = %s 
            ORDER BY detected_at DESC
        """, (plate_text,))
        results = cursor.fetchall()
        return results
    except Error as e:
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_statistics(date_stat):
    """Cập nhật thống kê cho ngày cụ thể."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # Tính toán thống kê
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT p.id) as total_plates,
                COUNT(d.id) as total_detections,
                AVG(p.confidence) as avg_confidence,
                (SELECT plate_text FROM plates WHERE DATE(timestamp) = %s ORDER BY detection_count DESC LIMIT 1) as top_plate
            FROM plates p
            LEFT JOIN detections d ON p.id = d.plate_id AND DATE(d.detected_at) = %s
            WHERE DATE(p.timestamp) = %s
        """, (date_stat, date_stat, date_stat))
        
        result = cursor.fetchone()
        total_plates, total_detections, avg_confidence, top_plate = result
        
        # Cập nhật hoặc thêm mới
        cursor.execute("""
            INSERT INTO statistics (date_stat, total_plates, total_detections, avg_confidence, top_plate)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                total_plates = VALUES(total_plates),
                total_detections = VALUES(total_detections),
                avg_confidence = VALUES(avg_confidence),
                top_plate = VALUES(top_plate)
        """, (date_stat, total_plates or 0, total_detections or 0, avg_confidence or 0, top_plate))
        
        conn.commit()
        return True
    except Error as e:
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def register_user(username, password, full_name, email='', role='User'):
    """Đăng ký tài khoản người dùng mới."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None, "Không thể kết nối cơ sở dữ liệu"

        cursor = conn.cursor(dictionary=True)

        # Kiểm tra username đã tồn tại chưa
        cursor.execute("SELECT id FROM app_users WHERE username = %s", (username,))
        if cursor.fetchone():
            return None, "Tên tài khoản đã tồn tại"

        # Kiểm tra email đã tồn tại chưa (nếu có)
        if email:
            cursor.execute("SELECT id FROM app_users WHERE email = %s", (email,))
            if cursor.fetchone():
                return None, "Email đã được sử dụng"

        password_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO app_users (username, password_hash, full_name, email, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password_hash, full_name, email, role))
        
        import time
        if role == 'Resident':
            # Đồng bộ sang bảng tiếng Việt: cu_dan
            ma_cu_dan = "CD_" + str(int(time.time() * 100))
            try:
                cursor.execute("""
                    INSERT INTO cu_dan (MaCuDan, HoTen, CCCD, SoDienThoai, Email, MaCanHo, TaiKhoan, MatKhau, TrangThai)
                    VALUES (%s, %s, %s, '000', %s, 'Chưa có', %s, %s, 'HoatDong')
                """, (ma_cu_dan, full_name, ma_cu_dan, email or f"{username}@resident.com", username, password_hash))
            except Exception as e:
                print(f"Lỗi đồng bộ cu_dan: {e}")
        else:
            # Đồng bộ sang bảng tiếng Việt: nhan_vien
            ma_nv = "NV_" + str(int(time.time() * 100))
            vai_tro = 'QuanLy' if role == 'Admin' else 'BaoVe'
            try:
                cursor.execute("""
                    INSERT INTO nhan_vien (MaNV, HoTen, Email, TaiKhoan, MatKhau, VaiTro, TrangThai)
                    VALUES (%s, %s, %s, %s, %s, %s, 'HoatDong')
                """, (ma_nv, full_name, email or f"{username}@system.com", username, password_hash, vai_tro))
            except Exception as e:
                print(f"Lỗi đồng bộ nhan_vien: {e}")

        conn.commit()

        cursor.execute("""
            SELECT id, username, full_name, email, role
            FROM app_users WHERE username = %s
        """, (username,))
        new_user = cursor.fetchone()
        return new_user, None
    except Error as e:
        return None, f"Lỗi cơ sở dữ liệu: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

import random
from datetime import datetime, timedelta

def generate_otp(email):
    """Tạo mã OTP 6 số và lưu vào quan_ly_otp_token."""
    conn = get_db_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
    try:
        cursor = conn.cursor(dictionary=True)
        # Xác định loại tài khoản (NhanVien hay CuDan)
        cursor.execute("SELECT MaNV FROM nhan_vien WHERE Email = %s", (email,))
        is_nhan_vien = cursor.fetchone()
        
        cursor.execute("SELECT MaCuDan FROM cu_dan WHERE Email = %s", (email,))
        is_cu_dan = cursor.fetchone()
        
        if not is_nhan_vien and not is_cu_dan:
            # Kiểm tra thử app_users dự phòng
            cursor.execute("SELECT role FROM app_users WHERE email = %s", (email,))
            app_user = cursor.fetchone()
            if not app_user:
                return False, "Email không tồn tại trong hệ thống."
            loai_tk = 'CuDan' if app_user['role'] == 'Resident' else 'NhanVien'
        else:
            loai_tk = 'NhanVien' if is_nhan_vien else 'CuDan'

        otp_code = str(random.randint(100000, 999999))
        expire_time = datetime.now() + timedelta(minutes=5)

        cursor.execute("""
            INSERT INTO quan_ly_otp_token (Email_Nhan, LoaiTaiKhoan, MaOTP, ThoiGianHetHan, TrangThai)
            VALUES (%s, %s, %s, %s, 'ChuaSuDung')
        """, (email, loai_tk, otp_code, expire_time.strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        return True, otp_code
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        conn.close()

def verify_and_reset_password(email, otp, new_password):
    """Xác minh OTP và cập nhật mật khẩu mới."""
    conn = get_db_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
    try:
        cursor = conn.cursor(dictionary=True)
        # Tìm OTP hợp lệ (ChuaSuDung, chưa hết hạn, đúng mã, đúng email)
        cursor.execute("""
            SELECT ID, LoaiTaiKhoan, ThoiGianHetHan 
            FROM quan_ly_otp_token 
            WHERE Email_Nhan = %s AND MaOTP = %s AND TrangThai = 'ChuaSuDung'
            ORDER BY ThoiGianTao DESC LIMIT 1
        """, (email, otp))
        token = cursor.fetchone()
        
        if not token:
            return False, "Mã OTP không đúng hoặc không tồn tại."
            
        if token['ThoiGianHetHan'] < datetime.now():
            return False, "Mã OTP đã hết hạn."
            
        # Hợp lệ -> Đổi pass
        password_hash = generate_password_hash(new_password)
        
        # Cập nhật app_users
        cursor.execute("UPDATE app_users SET password_hash = %s WHERE email = %s", (password_hash, email))
        
        # Cập nhật bảng Tiếng Việt
        if token['LoaiTaiKhoan'] == 'NhanVien':
            cursor.execute("UPDATE nhan_vien SET MatKhau = %s WHERE Email = %s", (password_hash, email))
        else:
            cursor.execute("UPDATE cu_dan SET MatKhau = %s WHERE Email = %s", (password_hash, email))
            
        # Đánh dấu OTP đã sử dụng
        cursor.execute("UPDATE quan_ly_otp_token SET TrangThai = 'DaSuDung' WHERE ID = %s", (token['ID'],))
        
        conn.commit()
        return True, "Cập nhật mật khẩu thành công."
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        conn.close()

def calculate_parking_fee(vehicle_type, duration_minutes, group_type, is_ticket_active):
    """Tính phí gửi xe dựa trên loại xe, thời lượng đỗ và phân nhóm xe."""
    if group_type == 'Whitelist' or is_ticket_active:
        return 0.0
    
    # Làm tròn lên theo giờ (tối thiểu 1 giờ)
    hours = max(1, int((duration_minutes + 59) / 60))
    
    # Biểu phí theo loại xe
    rates = {
        'Ô tô con': 15000.0,
        'Xe máy': 3000.0,
        'Ô tô tải': 30000.0,
    }
    rate = rates.get(vehicle_type, 10000.0)
    return rate * hours

def process_parking_transaction(plate_text, gate_type, camera_source):
    """Xử lý nghiệp vụ Check-In/Check-Out khi phát hiện biển số."""
    conn = None
    from datetime import datetime, date
    import time
    try:
        conn = get_db_connection()
        if not conn:
            return {"status": "error", "message": "Không thể kết nối CSDL"}
        cursor = conn.cursor(dictionary=True)
        
        # 1. Kiểm tra thông tin xe và nhóm xe
        cursor.execute("""
            SELECT group_type, vehicle_type, monthly_ticket_expiry, status 
            FROM vehicles WHERE plate_text = %s
        """, (plate_text,))
        vehicle_row = cursor.fetchone()
        
        group_type = 'Normal'
        vehicle_type = 'Ô tô con'
        is_ticket_active = False
        
        if vehicle_row:
            group_type = vehicle_row['group_type'] or 'Normal'
            vehicle_type = vehicle_row['vehicle_type'] or 'Ô tô con'
            expiry = vehicle_row['monthly_ticket_expiry']
            if expiry:
                if expiry >= date.today():
                    is_ticket_active = True
            if vehicle_row.get('status') == 'Không hoạt động':
                return {
                    "status": "error",
                    "message": "Xe đã bị vô hiệu hóa (Không hoạt động)",
                    "group_type": group_type,
                    "is_ticket_active": is_ticket_active
                }

        # 2. Xử lý Check-In
        if gate_type == 'in':
            if group_type == 'Blacklist':
                return {
                    "status": "error",
                    "message": "Xe nằm trong danh sách đen (Blacklist). TỪ CHỐI CHECK-IN.",
                    "group_type": group_type,
                    "is_ticket_active": is_ticket_active
                }

            # Kiểm tra xem có phiên nào đang đỗ (Parked) không
            cursor.execute("""
                SELECT id, check_in_time FROM parking_sessions 
                WHERE plate_text = %s AND status = 'Parked' 
                LIMIT 1
            """, (plate_text,))
            active_session = cursor.fetchone()
            
            if active_session:
                return {
                    "status": "already_in",
                    "session_id": active_session['id'],
                    "check_in_time": str(active_session['check_in_time']),
                    "group_type": group_type,
                    "is_ticket_active": is_ticket_active
                }
            
            # Tạo phiên đỗ mới trong parking_sessions
            cursor.execute("""
                INSERT INTO parking_sessions (plate_text, check_in_time, status, camera_in)
                VALUES (%s, NOW(), 'Parked', %s)
            """, (plate_text, camera_source))
            conn.commit()
            session_id = cursor.lastrowid
            
            # Đồng bộ dữ liệu sang bảng tiếng Việt: lich_su_ra_vao
            ma_giao_dich = "TXN_" + str(int(time.time() * 1000))
            loai_khach = 'CuDan' if group_type in ['Whitelist', 'Monthly'] else 'VangLai'
            try:
                # Lấy DetectionID mới nhất để thỏa mãn Foreign Key
                cursor.execute("SELECT id FROM detections WHERE plate_text = %s ORDER BY detected_at DESC LIMIT 1", (plate_text,))
                det_row = cursor.fetchone()
                det_id = det_row['id'] if det_row else 0
                
                cursor.execute("""
                    INSERT INTO lich_su_ra_vao 
                    (MaGiaoDich, BienSoXe, LoaiKhach, ThoiGianVao, TrangThai, AnhVao, DetectionID_Vao)
                    VALUES (%s, %s, %s, NOW(), 'DangTrongBai', %s, %s)
                """, (ma_giao_dich, plate_text, loai_khach, "", det_id))
                conn.commit()
            except Error as e:
                print(f"Lỗi đồng bộ lich_su_ra_vao (IN): {e}")
            
            return {
                "status": "check_in_success",
                "session_id": session_id,
                "check_in_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "group_type": group_type,
                "is_ticket_active": is_ticket_active
            }
            
        # 3. Xử lý Check-Out
        elif gate_type == 'out':
            # Tìm phiên đang đỗ
            cursor.execute("""
                SELECT id, check_in_time FROM parking_sessions 
                WHERE plate_text = %s AND status = 'Parked' 
                ORDER BY check_in_time DESC LIMIT 1
            """, (plate_text,))
            active_session = cursor.fetchone()
            
            if active_session:
                session_id = active_session['id']
                # Cập nhật thông tin check-out trong parking_sessions
                cursor.execute("""
                    UPDATE parking_sessions 
                    SET check_out_time = NOW(),
                        duration_minutes = TIMESTAMPDIFF(MINUTE, check_in_time, NOW()),
                        status = 'Completed',
                        camera_out = %s
                    WHERE id = %s
                """, (camera_source, session_id))
                
                # Đồng bộ cập nhật check-out sang bảng tiếng Việt: lich_su_ra_vao
                ma_giao_dich = None
                try:
                    # Lấy MaGiaoDich trước khi update
                    cursor.execute("""
                        SELECT MaGiaoDich FROM lich_su_ra_vao 
                        WHERE BienSoXe = %s AND TrangThai = 'DangTrongBai' 
                        ORDER BY ThoiGianVao DESC LIMIT 1
                    """, (plate_text,))
                    vn_session = cursor.fetchone()
                    
                    if vn_session:
                        ma_giao_dich = vn_session['MaGiaoDich']
                        cursor.execute("""
                            UPDATE lich_su_ra_vao
                            SET ThoiGianRa = NOW(),
                                TrangThai = 'DaRa',
                                AnhRa = %s
                            WHERE MaGiaoDich = %s
                        """, ("", ma_giao_dich))
                except Error as e:
                    print(f"Lỗi đồng bộ lich_su_ra_vao (OUT): {e}")
                    ma_giao_dich = None
                
                # Đọc lại duration_minutes để tính phí
                cursor.execute("""
                    SELECT duration_minutes, check_in_time, check_out_time 
                    FROM parking_sessions WHERE id = %s
                """, (session_id,))
                updated_session = cursor.fetchone()
                duration = updated_session['duration_minutes'] or 1
                
                fee = calculate_parking_fee(vehicle_type, duration, group_type, is_ticket_active)
                
                cursor.execute("""
                    UPDATE parking_sessions SET fee = %s WHERE id = %s
                """, (fee, session_id))
                
                # Tạo hóa đơn trong bảng tiếng Việt: hoa_don
                if ma_giao_dich:
                    try:
                        ma_hoa_don = "HD_" + str(int(time.time() * 1000))
                        phuong_thuc = 'VeThang' if is_ticket_active else 'TienMat'
                        # Chọn ngẫu nhiên một mã giá (Gia_VangLai_Oto_TheoLuot vv) - tạm hardcode 1 mã cho demo
                        ma_gia = "GIA_DEFAULT"
                        cursor.execute("""
                            INSERT INTO hoa_don 
                            (MaHoaDon, MaGiaoDich, MaGia, TongTien, PhuongThucThanhToan, TrangThai)
                            VALUES (%s, %s, %s, %s, %s, 'DaThanhToan')
                        """, (ma_hoa_don, ma_giao_dich, ma_gia, fee, phuong_thuc))
                    except Error as e:
                        print(f"Lỗi đồng bộ hoa_don (OUT): {e}")
                        
                conn.commit()
                
                return {
                    "status": "check_out_success",
                    "session_id": session_id,
                    "check_in_time": str(updated_session['check_in_time']),
                    "check_out_time": str(updated_session['check_out_time']),
                    "duration_minutes": duration,
                    "fee": float(fee),
                    "group_type": group_type,
                    "is_ticket_active": is_ticket_active
                }
            else:
                # Không tìm thấy check-in -> Tự động check-in cách đây 60 phút
                fee = calculate_parking_fee(vehicle_type, 60, group_type, is_ticket_active)
                cursor.execute("""
                    INSERT INTO parking_sessions 
                    (plate_text, check_in_time, check_out_time, duration_minutes, fee, status, camera_in, camera_out)
                    VALUES (%s, DATE_SUB(NOW(), INTERVAL 1 HOUR), NOW(), 60, %s, 'Completed', 'Auto-CheckIn', %s)
                """, (plate_text, fee, camera_source))
                conn.commit()
                session_id = cursor.lastrowid
                
                # Đồng bộ Auto-CheckOut sang bảng tiếng Việt: lich_su_ra_vao
                ma_giao_dich = "TXN_" + str(int(time.time() * 1000))
                loai_khach = 'CuDan' if group_type in ['Whitelist', 'Monthly'] else 'VangLai'
                try:
                    cursor.execute("SELECT id FROM detections WHERE plate_text = %s ORDER BY detected_at DESC LIMIT 1", (plate_text,))
                    det_row = cursor.fetchone()
                    det_id = det_row['id'] if det_row else 0

                    cursor.execute("""
                        INSERT INTO lich_su_ra_vao 
                        (MaGiaoDich, BienSoXe, LoaiKhach, ThoiGianVao, ThoiGianRa, TrangThai, AnhVao, AnhRa, DetectionID_Vao)
                        VALUES (%s, %s, %s, DATE_SUB(NOW(), INTERVAL 1 HOUR), NOW(), 'DaRa', '', '', %s)
                    """, (ma_giao_dich, plate_text, loai_khach, det_id))
                    
                    # Tạo hóa đơn cho luồng tự động
                    ma_hoa_don = "HD_" + str(int(time.time() * 1000))
                    phuong_thuc = 'VeThang' if is_ticket_active else 'TienMat'
                    cursor.execute("""
                        INSERT INTO hoa_don 
                        (MaHoaDon, MaGiaoDich, MaGia, TongTien, PhuongThucThanhToan, TrangThai)
                        VALUES (%s, %s, %s, %s, %s, 'DaThanhToan')
                    """, (ma_hoa_don, ma_giao_dich, "GIA_DEFAULT", fee, phuong_thuc))
                    
                    conn.commit()
                except Error as e:
                    print(f"Lỗi đồng bộ lich_su_ra_vao (AUTO_OUT): {e}")
                
                return {
                    "status": "auto_check_out_success",
                    "session_id": session_id,
                    "duration_minutes": 60,
                    "fee": float(fee),
                    "group_type": group_type,
                    "is_ticket_active": is_ticket_active,
                    "warning": "Không tìm thấy lượt vào, tự động Check-In trước 1 giờ."
                }
        
    except Error as e:
        print(f"Lỗi xử lý giao dịch đỗ xe: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_parking_sessions(status=None, date_from=None, date_to=None, search_term=None):
    """Lấy danh sách lượt đỗ xe kèm thông tin chi tiết xe."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT s.*, v.owner_name, v.vehicle_type, v.color, v.group_type
            FROM parking_sessions s
            LEFT JOIN vehicles v ON s.plate_text = v.plate_text
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND s.status = %s"
            params.append(status)
            
        if date_from:
            query += " AND DATE(s.check_in_time) >= %s"
            params.append(date_from)
            
        if date_to:
            query += " AND DATE(s.check_in_time) <= %s"
            params.append(date_to)
            
        if search_term:
            query += " AND (s.plate_text LIKE %s OR v.owner_name LIKE %s)"
            term = f"%{search_term}%"
            params.append(term)
            params.append(term)
            
        query += " ORDER BY s.check_in_time DESC LIMIT 500"
        
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Lỗi lấy danh sách phiên đỗ xe: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def checkout_session_manual(session_id):
    """Nút bấm Check-Out thủ công cho quản trị viên."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor(dictionary=True)
        
        # Lấy biển số và thông tin phiên
        cursor.execute("SELECT plate_text, status FROM parking_sessions WHERE id = %s", (session_id,))
        row = cursor.fetchone()
        if not row or row['status'] != 'Parked':
            return False
            
        plate_text = row['plate_text']
        
        # Thực hiện Check-Out bằng hàm xử lý chung
        res = process_parking_transaction(plate_text, 'out', 'Manual-Dashboard')
        return res.get('status') in ['check_out_success', 'auto_check_out_success']
    except Error as e:
        print(f"Lỗi Check-Out thủ công: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_revenue_stats(date_from=None, date_to=None):
    """Thống kê doanh thu theo ngày."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT DATE(check_out_time) AS date_revenue, SUM(fee) AS total_fee
            FROM parking_sessions
            WHERE status = 'Completed' AND check_out_time IS NOT NULL
        """
        params = []
        if date_from:
            query += " AND DATE(check_out_time) >= %s"
            params.append(date_from)
        if date_to:
            query += " AND DATE(check_out_time) <= %s"
            params.append(date_to)
            
        query += " GROUP BY DATE(check_out_time) ORDER BY date_revenue ASC LIMIT 60"
        
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Lỗi thống kê doanh thu: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_peak_hours_stats():
    """Thống kê lượng quét xe theo giờ trong ngày (0-23 giờ)."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT HOUR(detected_at) AS scan_hour, COUNT(*) AS scan_count
            FROM detections
            GROUP BY HOUR(detected_at)
            ORDER BY scan_hour ASC
        """)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Lỗi thống kê giờ cao điểm: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ================== QUẢN LÝ TÀI KHOẢN & BẢO VỆ (ADMIN) ==================

def get_all_users_list():
    """Lấy danh sách tất cả tài khoản người dùng, cư dân và bảo vệ."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SHOW COLUMNS FROM cu_dan")
        cd_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
        cd_phone = "c.SoDienThoai" if "SoDienThoai" in cd_cols else ("c.SDT" if "SDT" in cd_cols else "NULL")

        cursor.execute("SHOW COLUMNS FROM nhan_vien")
        nv_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
        nv_phone = "nv.SoDienThoai" if "SoDienThoai" in nv_cols else ("nv.SDT" if "SDT" in nv_cols else "NULL")

        cursor.execute(f"""
            SELECT u.id, u.username, u.full_name, u.email, u.role, u.is_active, u.created_at,
                   c.MaCanHo AS apartment, {cd_phone} AS resident_phone,
                   nv.CaTruc AS shift, {nv_phone} AS guard_phone, nv.VaiTro AS guard_role
            FROM app_users u
            LEFT JOIN cu_dan c ON u.username = c.TaiKhoan
            LEFT JOIN nhan_vien nv ON u.username = nv.TaiKhoan
            ORDER BY u.created_at DESC
        """)
        users = cursor.fetchall()
        for u in users:
            u["phone"] = u.get("guard_phone") or u.get("resident_phone") or "Chưa có"
            u["created_str"] = u["created_at"].strftime("%d/%m/%Y %H:%M") if u.get("created_at") else "---"
        return users
    except Error as e:
        print(f"Lỗi lấy danh sách tài khoản: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def admin_reset_user_password(username, new_password):
    """Cấp lại / đổi mật khẩu cho người dùng từ trang Admin."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Không thể kết nối CSDL"
        cursor = conn.cursor(dictionary=True)
        
        pw_hash = generate_password_hash(new_password)
        cursor.execute("UPDATE app_users SET password_hash = %s WHERE username = %s", (pw_hash, username))
        cursor.execute("UPDATE cu_dan SET MatKhau = %s WHERE TaiKhoan = %s", (pw_hash, username))
        cursor.execute("UPDATE nhan_vien SET MatKhau = %s WHERE TaiKhoan = %s", (pw_hash, username))
        conn.commit()
        return True, "Cấp lại mật khẩu thành công!"
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def admin_toggle_user_status(username):
    """Khóa hoặc Mở khóa tài khoản."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Không thể kết nối CSDL"
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT is_active, role FROM app_users WHERE username = %s", (username,))
        u = cursor.fetchone()
        if not u:
            return False, "Tài khoản không tồn tại"
        if u["role"] == "Admin":
            return False, "Không thể khóa tài khoản Quản trị viên (Admin)"
            
        new_status = not bool(u["is_active"])
        new_trang_thai = "HoatDong" if new_status else "TamKhoa"
        
        cursor.execute("UPDATE app_users SET is_active = %s WHERE username = %s", (new_status, username))
        cursor.execute("UPDATE cu_dan SET TrangThai = %s WHERE TaiKhoan = %s", (new_trang_thai, username))
        cursor.execute("UPDATE nhan_vien SET TrangThai = %s WHERE TaiKhoan = %s", (new_trang_thai, username))
        conn.commit()
        
        msg = "Đã mở khóa tài khoản" if new_status else "Đã tạm khóa tài khoản"
        return True, msg
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def admin_create_guard(username, full_name, password, phone, email, shift):
    """Tạo mới tài khoản bảo vệ / nhân viên trực cổng."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Không thể kết nối CSDL"
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id FROM app_users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "Tên đăng nhập này đã tồn tại trên hệ thống"
            
        pw_hash = generate_password_hash(password)
        ma_nv = "NV_" + username.upper()
        
        cursor.execute("""
            INSERT INTO app_users (username, password_hash, full_name, email, role, is_active)
            VALUES (%s, %s, %s, %s, 'Operator', TRUE)
        """, (username, pw_hash, full_name, email or f"{username}@security.com"))
        
        cursor.execute("SHOW COLUMNS FROM nhan_vien")
        nv_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
        phone_col = "SoDienThoai" if "SoDienThoai" in nv_cols else ("SDT" if "SDT" in nv_cols else None)

        if phone_col:
            cursor.execute(f"""
                INSERT INTO nhan_vien (MaNV, HoTen, {phone_col}, Email, CaTruc, TaiKhoan, MatKhau, VaiTro, TrangThai)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Bảo vệ', 'HoatDong')
            """, (ma_nv, full_name, phone or '0900000000', email or f"{username}@security.com", shift or 'Ca Sáng (06:00 - 14:00)', username, pw_hash))
        else:
            cursor.execute("""
                INSERT INTO nhan_vien (MaNV, HoTen, Email, CaTruc, TaiKhoan, MatKhau, VaiTro, TrangThai)
                VALUES (%s, %s, %s, %s, %s, %s, 'Bảo vệ', 'HoatDong')
            """, (ma_nv, full_name, email or f"{username}@security.com", shift or 'Ca Sáng (06:00 - 14:00)', username, pw_hash))
        
        conn.commit()
        return True, "Thêm tài khoản bảo vệ thành công!"
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def admin_update_guard(username, full_name, phone, email, shift):
    """Cập nhật thông tin bảo vệ."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Không thể kết nối CSDL"
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("UPDATE app_users SET full_name = %s, email = %s WHERE username = %s", (full_name, email, username))
        
        cursor.execute("SHOW COLUMNS FROM nhan_vien")
        nv_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
        phone_col = "SoDienThoai" if "SoDienThoai" in nv_cols else ("SDT" if "SDT" in nv_cols else None)

        if phone_col:
            cursor.execute(f"""
                UPDATE nhan_vien 
                SET HoTen = %s, {phone_col} = %s, Email = %s, CaTruc = %s 
                WHERE TaiKhoan = %s
            """, (full_name, phone, email, shift, username))
        else:
            cursor.execute("""
                UPDATE nhan_vien 
                SET HoTen = %s, Email = %s, CaTruc = %s 
                WHERE TaiKhoan = %s
            """, (full_name, email, shift, username))
            
        conn.commit()
        return True, "Cập nhật thông tin bảo vệ thành công!"
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def admin_delete_guard(username):
    """Xóa tài khoản bảo vệ."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Không thể kết nối CSDL"
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT role FROM app_users WHERE username = %s", (username,))
        u = cursor.fetchone()
        if not u or u["role"] not in ["Operator", "Security"]:
            return False, "Chỉ có thể xóa tài khoản vai trò Bảo vệ"
            
        cursor.execute("DELETE FROM nhan_vien WHERE TaiKhoan = %s", (username,))
        cursor.execute("DELETE FROM app_users WHERE username = %s", (username,))
        conn.commit()
        return True, "Đã xóa tài khoản bảo vệ"
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def admin_create_resident(username, full_name, password, phone='', email='', apartment_number='', cccd='', initial_plate=''):
    """Quản trị viên tạo tài khoản cho Cư dân (khi trang đăng ký bị lỗi hoặc cấp phát tại quầy)."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Không thể kết nối CSDL"
        cursor = conn.cursor(dictionary=True)
        
        # 1. Kiểm tra username đã tồn tại chưa
        cursor.execute("SELECT id FROM app_users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "Tên đăng nhập này đã tồn tại trên hệ thống"
            
        # 2. Kiểm tra email nếu có
        if email:
            cursor.execute("SELECT id FROM app_users WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "Email này đã được sử dụng bởi tài khoản khác"
                
        # 3. Tạo hash mật khẩu
        pw_hash = generate_password_hash(password)
        effective_email = email or f"{username}@resident.com"
        
        # 4. Thêm vào app_users với role 'Resident'
        cursor.execute("""
            INSERT INTO app_users (username, password_hash, full_name, email, role, is_active)
            VALUES (%s, %s, %s, %s, 'Resident', TRUE)
        """, (username, pw_hash, full_name, effective_email))
        
        # 5. Đồng bộ sang bảng cu_dan
        cursor.execute("SHOW COLUMNS FROM cu_dan")
        cd_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
        phone_col = "SoDienThoai" if "SoDienThoai" in cd_cols else ("SDT" if "SDT" in cd_cols else None)
        
        ma_cu_dan = "CD_" + str(int(time.time() * 100))
        cccd_val = cccd or ("CCCD_" + username.upper())
        phone_val = phone or "0900000000"
        apt_val = apartment_number or "Chưa cập nhật"
        
        insert_cols = ["MaCuDan", "HoTen", "TaiKhoan", "MatKhau", "TrangThai"]
        insert_vals = [ma_cu_dan, full_name, username, pw_hash, "HoatDong"]
        
        if phone_col:
            insert_cols.append(phone_col)
            insert_vals.append(phone_val)
        if "Email" in cd_cols:
            insert_cols.append("Email")
            insert_vals.append(effective_email)
        if "MaCanHo" in cd_cols:
            insert_cols.append("MaCanHo")
            insert_vals.append(apt_val)
        if "CCCD" in cd_cols:
            insert_cols.append("CCCD")
            insert_vals.append(cccd_val)
            
        cols_str = ", ".join(insert_cols)
        placeholders = ", ".join(["%s"] * len(insert_vals))
        cursor.execute(f"INSERT INTO cu_dan ({cols_str}) VALUES ({placeholders})", tuple(insert_vals))
        
        # 6. Nếu có biển số xe ban đầu, tự động gán xe cho cư dân
        if initial_plate:
            clean_plate = initial_plate.strip().upper()
            if clean_plate:
                try:
                    cursor.execute("""
                        INSERT INTO vehicles (plate_text, owner_name, vehicle_type, resident_id)
                        VALUES (%s, %s, 'Ô tô con', %s)
                        ON DUPLICATE KEY UPDATE owner_name = VALUES(owner_name), resident_id = VALUES(resident_id)
                    """, (clean_plate, full_name, username))
                except Exception as ex_v:
                    print(f"Warning: Tự động gán biển số {clean_plate} gặp lỗi: {ex_v}")
        
        conn.commit()
        return True, f"Tạo tài khoản cư dân '{username}' thành công!"
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ================== DUYỆT ĐƠN CHUYỂN NHƯỢNG XE ==================

def create_vehicle_transfer_request(plate_text, from_username, to_identifier, note=None):
    """Cư dân tạo đơn yêu cầu chuyển nhượng xe cho cư dân khác."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Không thể kết nối CSDL"
        cursor = conn.cursor(dictionary=True)
        
        # 1. Tìm thông tin cư dân chuyển
        cursor.execute("SELECT MaCuDan, HoTen, MaCanHo FROM cu_dan WHERE TaiKhoan = %s", (from_username,))
        sender = cursor.fetchone()
        if not sender:
            return False, "Không tìm thấy hồ sơ cư dân của bạn"
            
        # 2. Kiểm tra quyền sở hữu xe
        cursor.execute("""
            SELECT p.BienSoXe, p.MaCuDan, v.owner_name 
            FROM phuong_tien p 
            LEFT JOIN vehicles v ON p.BienSoXe = v.plate_text 
            WHERE p.BienSoXe = %s
        """, (plate_text,))
        veh = cursor.fetchone()
        if not veh:
            return False, "Không tìm thấy phương tiện này"
            
        if veh["MaCuDan"] != sender["MaCuDan"] and veh["owner_name"] != sender["HoTen"] and veh["owner_name"] != from_username:
            return False, "Bạn không phải là chủ sở hữu của phương tiện này"
            
        # 3. Tìm thông tin cư dân nhận
        cursor.execute("SHOW COLUMNS FROM cu_dan")
        cd_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
        phone_col = "SoDienThoai" if "SoDienThoai" in cd_cols else ("SDT" if "SDT" in cd_cols else None)

        if phone_col:
            cursor.execute(f"""
                SELECT MaCuDan, HoTen, MaCanHo, TaiKhoan 
                FROM cu_dan 
                WHERE (MaCanHo = %s OR TaiKhoan = %s OR {phone_col} = %s OR MaCuDan = %s)
                LIMIT 1
            """, (to_identifier, to_identifier, to_identifier, to_identifier))
        else:
            cursor.execute("""
                SELECT MaCuDan, HoTen, MaCanHo, TaiKhoan 
                FROM cu_dan 
                WHERE (MaCanHo = %s OR TaiKhoan = %s OR MaCuDan = %s)
                LIMIT 1
            """, (to_identifier, to_identifier, to_identifier))

        recipient = cursor.fetchone()
        if not recipient:
            return False, f"Không tìm thấy cư dân nhận phù hợp với '{to_identifier}'"
            
        if recipient["MaCuDan"] == sender["MaCuDan"]:
            return False, "Không thể tự chuyển nhượng xe cho chính mình"
            
        # 4. Kiểm tra xem đã có đơn Pending nào chưa
        cursor.execute("SELECT id FROM chuyen_nhuong_xe WHERE BienSoXe = %s AND TrangThai = 'Pending'", (plate_text,))
        if cursor.fetchone():
            return False, "Biển số xe này đang có một đơn chuyển nhượng chờ duyệt!"
            
        ma_don = "DON_" + str(int(time.time()))
        cursor.execute("""
            INSERT INTO chuyen_nhuong_xe (
                MaDon, BienSoXe, MaCuDanChuyen, TenCuDanChuyen, CanHoChuyen,
                MaCuDanNhan, TenCuDanNhan, CanHoNhan, TrangThai, GhiChu
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending', %s)
        """, (
            ma_don, plate_text,
            sender["MaCuDan"], sender["HoTen"], sender.get("MaCanHo") or "---",
            recipient["MaCuDan"], recipient["HoTen"], recipient.get("MaCanHo") or "---",
            note or "Cư dân yêu cầu chuyển nhượng xe trong chung cư"
        ))
        conn.commit()
        return True, f"Gửi đơn chuyển nhượng thành công (Mã đơn: {ma_don}). Vui lòng chờ Ban Quản Trị phê duyệt!"
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_transfer_requests(status_filter=None):
    """Lấy danh sách các đơn chuyển nhượng xe cho Admin duyệt."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM chuyen_nhuong_xe"
        params = []
        if status_filter:
            query += " WHERE TrangThai = %s"
            params.append(status_filter)
        query += " ORDER BY NgayYeuCau DESC LIMIT 200"
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        for r in rows:
            r["created_str"] = r["NgayYeuCau"].strftime("%d/%m/%Y %H:%M") if r.get("NgayYeuCau") else "---"
            r["approved_str"] = r["NgayDuyet"].strftime("%d/%m/%Y %H:%M") if r.get("NgayDuyet") else "---"
        return rows
    except Error as e:
        print(f"Lỗi lấy danh sách đơn chuyển nhượng: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_resident_transfer_requests(username):
    """Lấy danh sách đơn chuyển nhượng liên quan đến cư dân đang đăng nhập."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MaCuDan FROM cu_dan WHERE TaiKhoan = %s", (username,))
        cudan = cursor.fetchone()
        if not cudan:
            return []
        ma_cd = cudan["MaCuDan"]
        
        cursor.execute("""
            SELECT * FROM chuyen_nhuong_xe 
            WHERE MaCuDanChuyen = %s OR MaCuDanNhan = %s
            ORDER BY NgayYeuCau DESC LIMIT 50
        """, (ma_cd, ma_cd))
        rows = cursor.fetchall()
        for r in rows:
            r["created_str"] = r["NgayYeuCau"].strftime("%d/%m/%Y %H:%M") if r.get("NgayYeuCau") else "---"
            r["is_sender"] = (r["MaCuDanChuyen"] == ma_cd)
        return rows
    except Error as e:
        print(f"Lỗi lấy đơn chuyển nhượng cư dân: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def process_transfer_request_action(request_id, action, reviewer_username, note=None):
    """Ban Quản Trị duyệt hoặc từ chối đơn chuyển nhượng xe."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Không thể kết nối CSDL"
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM chuyen_nhuong_xe WHERE id = %s", (request_id,))
        req = cursor.fetchone()
        if not req:
            return False, "Không tìm thấy đơn chuyển nhượng này"
        if req["TrangThai"] != "Pending":
            return False, f"Đơn này đã được xử lý ({req['TrangThai']})"
            
        if action == "approve":
            # Chuyển quyền sở hữu xe
            plate = req["BienSoXe"]
            recipient_cd = req["MaCuDanNhan"]
            recipient_name = req["TenCuDanNhan"]
            
            cursor.execute("UPDATE phuong_tien SET MaCuDan = %s WHERE BienSoXe = %s", (recipient_cd, plate))
            cursor.execute("UPDATE vehicles SET owner_name = %s WHERE plate_text = %s", (recipient_name, plate))
            
            cursor.execute("""
                UPDATE chuyen_nhuong_xe 
                SET TrangThai = 'Approved', NgayDuyet = NOW(), NguoiDuyet = %s, GhiChu = COALESCE(%s, GhiChu)
                WHERE id = %s
            """, (reviewer_username, note or "Ban Quản Trị đã duyệt chuyển nhượng", request_id))
            conn.commit()
            return True, f"Đã phê duyệt thành công! Quyền sở hữu xe {plate} đã được chuyển cho cư dân {recipient_name}."
            
        elif action == "reject":
            cursor.execute("""
                UPDATE chuyen_nhuong_xe 
                SET TrangThai = 'Rejected', NgayDuyet = NOW(), NguoiDuyet = %s, GhiChu = COALESCE(%s, 'Ban Quản Trị từ chối yêu cầu')
                WHERE id = %s
            """, (reviewer_username, note or "Ban Quản Trị từ chối yêu cầu", request_id))
            conn.commit()
            return True, "Đã từ chối đơn chuyển nhượng."
        else:
            return False, "Hành động không hợp lệ"
    except Error as e:
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ================== CHỨC NĂNG BẢO VỆ / BÀN TRỰC OPERATOR ==================

def get_guard_verification_info(plate_text):
    """Lấy toàn bộ dữ liệu đối chiếu ảnh lúc vào, thông tin xe và tính phí trực tiếp."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        
        # 1. Tìm thông tin xe và chủ xe
        cursor.execute("SHOW COLUMNS FROM cu_dan")
        cd_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
        phone_col = "c.SoDienThoai" if "SoDienThoai" in cd_cols else ("c.SDT" if "SDT" in cd_cols else "NULL")

        cursor.execute(f"""
            SELECT v.*, p.MauXe, p.LoaiXe, p.NgayHetHan, c.HoTen AS resident_name, c.MaCanHo, {phone_col} AS phone
            FROM vehicles v
            LEFT JOIN phuong_tien p ON v.plate_text = p.BienSoXe
            LEFT JOIN cu_dan c ON p.MaCuDan = c.MaCuDan
            WHERE v.plate_text = %s
        """, (plate_text,))
        veh = cursor.fetchone()
        
        # 2. Tìm phiên đỗ xe hiện tại (nếu đang trong bãi)
        cursor.execute("""
            SELECT * FROM parking_sessions 
            WHERE plate_text = %s AND status = 'Parked' 
            ORDER BY check_in_time DESC LIMIT 1
        """, (plate_text,))
        session_curr = cursor.fetchone()
        
        # 3. Lấy ảnh snapshot lúc vào từ detections
        in_detection = None
        if session_curr:
            cursor.execute("""
                SELECT id, detected_at, camera_source, raw_text 
                FROM detections 
                WHERE plate_text = %s AND detected_at >= %s - INTERVAL 2 MINUTE AND detected_at <= %s + INTERVAL 2 MINUTE
                ORDER BY detected_at ASC LIMIT 1
            """, (plate_text, session_curr["check_in_time"], session_curr["check_in_time"]))
            in_detection = cursor.fetchone()

        now = datetime.now()
        is_monthly = False
        ticket_type = "Khách Vãng Lai"
        fee = 0
        duration_minutes = 0
        
        if veh:
            expiry = veh.get("monthly_ticket_expiry") or veh.get("NgayHetHan")
            if expiry:
                exp_date = expiry if isinstance(expiry, date) else datetime.strptime(str(expiry)[:10], "%Y-%m-%d").date()
                if exp_date >= date.today():
                    is_monthly = True
                    ticket_type = "Vé Tháng Cư Dân"
                    
        if session_curr and session_curr.get("check_in_time"):
            in_time = session_curr["check_in_time"]
            duration_minutes = max(1, int((now - in_time).total_seconds() / 60))
            if not is_monthly:
                # Bảng giá vé lượt: 15.000đ cho 2 giờ đầu, 10.000đ mỗi giờ tiếp theo
                hours = max(1, (duration_minutes + 59) // 60)
                if hours <= 2:
                    fee = 15000
                else:
                    fee = 15000 + (hours - 2) * 10000
            else:
                fee = 0

        return {
            "plate_text": plate_text,
            "vehicle_type": veh.get("vehicle_type") if veh else "Ô tô con",
            "color": veh.get("color") if veh else "Chưa xác định",
            "owner_name": (veh.get("resident_name") or veh.get("owner_name")) if veh else "Khách vãng lai",
            "apartment": veh.get("MaCanHo") if veh else "---",
            "phone": veh.get("SoDienThoai") if veh else "---",
            "is_monthly": is_monthly,
            "ticket_type": ticket_type,
            "has_active_session": session_curr is not None,
            "session_id": session_curr["id"] if session_curr else None,
            "check_in_time": session_curr["check_in_time"].strftime("%d/%m/%Y %H:%M:%S") if session_curr and session_curr.get("check_in_time") else None,
            "duration_minutes": duration_minutes,
            "duration_str": f"{duration_minutes // 60} giờ {duration_minutes % 60} phút" if duration_minutes >= 60 else f"{duration_minutes} phút",
            "fee": fee,
            "fee_formatted": f"{fee:,.0f} VNĐ",
            "in_camera": session_curr["camera_in"] if session_curr else "Cổng Vào #1"
        }
    except Error as e:
        print(f"Lỗi lấy thông tin đối chiếu: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    init_db()