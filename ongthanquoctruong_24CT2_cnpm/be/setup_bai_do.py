#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script khởi tạo bảng bai_do và seed dữ liệu bãi đỗ xe ô tô chung cư phong cách rạp chiếu phim
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import database

def setup_bai_do():
    conn = database.get_db_connection()
    if not conn:
        print("❌ Không thể kết nối CSDL")
        return False
        
    c = conn.cursor(dictionary=True)
    
    # 1. Tạo bảng bai_do
    c.execute("""
    CREATE TABLE IF NOT EXISTS bai_do (
        MaChoDo VARCHAR(20) PRIMARY KEY COMMENT 'Mã ô đỗ xe, ví dụ: B1-A01, B1-B05',
        TenChoDo VARCHAR(100) NOT NULL COMMENT 'Tên ô đỗ: Vị trí A-01 (Tầng B1)',
        KhuVuc VARCHAR(30) NOT NULL COMMENT 'Khu vực / Tầng hầm: Ham_B1, Ham_B2',
        Day VARCHAR(10) NOT NULL COMMENT 'Dãy ô đỗ: A, B, VIP, C, D, E',
        SoThuTu INT NOT NULL COMMENT 'Số thứ tự trong dãy: 1..10',
        LoaiChoDo VARCHAR(30) DEFAULT 'Ô tô con' COMMENT 'Loại chỗ: Ô tô con, VIP Ô tô',
        TrangThai VARCHAR(20) DEFAULT 'Trong' COMMENT 'Trong, DaDat, BaoTri',
        BienSoXe VARCHAR(20) DEFAULT NULL,
        MaCuDan VARCHAR(50) DEFAULT NULL,
        GhiChu VARCHAR(255) DEFAULT NULL,
        CapNhatLuc DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_khuvuc (KhuVuc),
        INDEX idx_trangthai (TrangThai),
        INDEX idx_bienso (BienSoXe),
        INDEX idx_cudan (MaCuDan)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    print("✅ Bảng 'bai_do' đã được tạo/kiểm tra.")
    
    # 2. Bổ sung cột ViTriDo vào phuong_tien
    c.execute("SHOW COLUMNS FROM phuong_tien LIKE 'ViTriDo'")
    if not c.fetchone():
        c.execute("ALTER TABLE phuong_tien ADD COLUMN ViTriDo VARCHAR(50) DEFAULT NULL COMMENT 'Vị trí bãi đỗ xe ô tô'")
        print("✅ Đã thêm cột 'ViTriDo' vào bảng phuong_tien.")
    else:
        print("ℹ️ Cột 'ViTriDo' đã có trong phuong_tien.")
        
    # 3. Bổ sung cột parking_slot vào vehicles
    c.execute("SHOW COLUMNS FROM vehicles LIKE 'parking_slot'")
    if not c.fetchone():
        c.execute("ALTER TABLE vehicles ADD COLUMN parking_slot VARCHAR(50) DEFAULT NULL COMMENT 'Vị trí bãi đỗ xe ô tô'")
        print("✅ Đã thêm cột 'parking_slot' vào bảng vehicles.")
    else:
        print("ℹ️ Cột 'parking_slot' đã có trong vehicles.")
        
    # 4. Tạo danh sách các ô đỗ chuẩn chỉ dành riêng cho xe ô tô (100 ô: 50 ô Hầm B1, 50 ô Hầm B2)
    slots = []
    
    # ================== TẦNG HẦM B1: 50 CHỖ Ô TÔ ==================
    # Dãy A (14 ô)
    for i in range(1, 15):
        slots.append({
            "MaChoDo": f"B1-A{i:02d}",
            "TenChoDo": f"Vị trí A-{i:02d} (Hầm B1)",
            "KhuVuc": "Ham_B1",
            "Day": "A",
            "SoThuTu": i,
            "LoaiChoDo": "Ô tô con",
            "TrangThai": "Trong"
        })
    # Dãy B (14 ô)
    for i in range(1, 15):
        slots.append({
            "MaChoDo": f"B1-B{i:02d}",
            "TenChoDo": f"Vị trí B-{i:02d} (Hầm B1)",
            "KhuVuc": "Ham_B1",
            "Day": "B",
            "SoThuTu": i,
            "LoaiChoDo": "Ô tô con",
            "TrangThai": "Trong"
        })
    # Dãy C (14 ô)
    for i in range(1, 15):
        slots.append({
            "MaChoDo": f"B1-C{i:02d}",
            "TenChoDo": f"Vị trí C-{i:02d} (Hầm B1)",
            "KhuVuc": "Ham_B1",
            "Day": "C",
            "SoThuTu": i,
            "LoaiChoDo": "Ô tô con",
            "TrangThai": "Trong"
        })
    # Dãy VIP Hầm B1 (8 ô - gần sảnh thang máy cư dân)
    for i in range(1, 9):
        slots.append({
            "MaChoDo": f"B1-VIP{i:02d}",
            "TenChoDo": f"Vị trí VIP-{i:02d} (Hầm B1)",
            "KhuVuc": "Ham_B1",
            "Day": "VIP",
            "SoThuTu": i,
            "LoaiChoDo": "VIP Ô tô",
            "TrangThai": "Trong"
        })
        
    # ================== TẦNG HẦM B2: 50 CHỖ Ô TÔ ==================
    # Dãy D (14 ô)
    for i in range(1, 15):
        slots.append({
            "MaChoDo": f"B2-D{i:02d}",
            "TenChoDo": f"Vị trí D-{i:02d} (Hầm B2)",
            "KhuVuc": "Ham_B2",
            "Day": "D",
            "SoThuTu": i,
            "LoaiChoDo": "Ô tô con",
            "TrangThai": "Trong"
        })
    # Dãy E (14 ô)
    for i in range(1, 15):
        slots.append({
            "MaChoDo": f"B2-E{i:02d}",
            "TenChoDo": f"Vị trí E-{i:02d} (Hầm B2)",
            "KhuVuc": "Ham_B2",
            "Day": "E",
            "SoThuTu": i,
            "LoaiChoDo": "Ô tô con",
            "TrangThai": "Trong"
        })
    # Dãy F (14 ô)
    for i in range(1, 15):
        slots.append({
            "MaChoDo": f"B2-F{i:02d}",
            "TenChoDo": f"Vị trí F-{i:02d} (Hầm B2)",
            "KhuVuc": "Ham_B2",
            "Day": "F",
            "SoThuTu": i,
            "LoaiChoDo": "Ô tô con",
            "TrangThai": "Trong"
        })
    # Dãy VIP Hầm B2 (8 ô - gần thang máy phụ)
    for i in range(1, 9):
        slots.append({
            "MaChoDo": f"B2-VIP{i:02d}",
            "TenChoDo": f"Vị trí VIP-{i:02d} (Hầm B2)",
            "KhuVuc": "Ham_B2",
            "Day": "VIP",
            "SoThuTu": i,
            "LoaiChoDo": "VIP Ô tô",
            "TrangThai": "Trong"
        })
        
    # Insert hoặc update các ô đỗ
    for s in slots:
        c.execute("""
            INSERT INTO bai_do (MaChoDo, TenChoDo, KhuVuc, Day, SoThuTu, LoaiChoDo, TrangThai)
            VALUES (%(MaChoDo)s, %(TenChoDo)s, %(KhuVuc)s, %(Day)s, %(SoThuTu)s, %(LoaiChoDo)s, %(TrangThai)s)
            ON DUPLICATE KEY UPDATE
                TenChoDo = VALUES(TenChoDo),
                KhuVuc = VALUES(KhuVuc),
                Day = VALUES(Day),
                SoThuTu = VALUES(SoThuTu),
                LoaiChoDo = VALUES(LoaiChoDo)
        """, s)

    # Dọn dẹp các mã ô đỗ cũ không còn trong danh mục 100 ô
    valid_codes = [s["MaChoDo"] for s in slots]
    format_strings = ','.join(['%s'] * len(valid_codes))
    c.execute(f"DELETE FROM bai_do WHERE MaChoDo NOT IN ({format_strings})", tuple(valid_codes))
        
    conn.commit()
    print(f"✅ Đã cấu hình thành công {len(slots)} ô đỗ ô tô trong bảng 'bai_do'.")
    
    # 5. Gán tự động một số ô đỗ cho các xe đã có sẵn trong hệ thống để tạo tính chân thực (ghế rạp phim đã có người ngồi)
    c.execute("SELECT BienSoXe, MaCuDan, ViTriDo FROM phuong_tien WHERE ViTriDo IS NOT NULL AND ViTriDo != ''")
    assigned = c.fetchall()
    for row in assigned:
        c.execute("""
            UPDATE bai_do 
            SET TrangThai = 'DaDat', BienSoXe = %s, MaCuDan = %s
            WHERE MaChoDo = %s
        """, (row["BienSoXe"], row["MaCuDan"], row["ViTriDo"]))
        
    # Nếu chưa có xe nào gán vị trí, gán thử một số xe đầu tiên vào một vài ô để sơ đồ hiển thị chân thực
    c.execute("SELECT COUNT(*) AS cnt FROM bai_do WHERE TrangThai = 'DaDat'")
    cnt = c.fetchone()["cnt"]
    if cnt == 0:
        c.execute("SELECT BienSoXe, MaCuDan FROM phuong_tien LIMIT 12")
        pts = c.fetchall()
        preset_slots = ["B1-A01", "B1-A03", "B1-B02", "B1-B06", "B1-VIP01", "B2-C02", "B2-C04", "B2-D01", "B2-D05"]
        for idx, pt in enumerate(pts):
            if idx < len(preset_slots):
                slot_id = preset_slots[idx]
                c.execute("""
                    UPDATE bai_do 
                    SET TrangThai = 'DaDat', BienSoXe = %s, MaCuDan = %s 
                    WHERE MaChoDo = %s
                """, (pt["BienSoXe"], pt["MaCuDan"], slot_id))
                c.execute("UPDATE phuong_tien SET ViTriDo = %s WHERE BienSoXe = %s", (slot_id, pt["BienSoXe"]))
                c.execute("UPDATE vehicles SET parking_slot = %s WHERE plate_text = %s", (slot_id, pt["BienSoXe"]))
        print("✅ Đã gán vị trí mẫu cho các xe hiện có để tạo trạng thái chân thực cho sơ đồ rạp phim.")
        
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    setup_bai_do()
