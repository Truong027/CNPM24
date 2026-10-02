# 🚗 Nhận Diện Biển Số Xe - Hướng Dẫn MySQL

## 📁 **Tệp Đã Tạo**

| Tệp | Mô Tả |
|-----|-------|
| `bien_so_xe_sample.sql` | **File SQL hoàn chỉnh** với tất cả dữ liệu mẫu (5 bảng, 27 biển số) |
| `import_data.py` | **Script Python** để import dữ liệu tự động |
| `IMPORT_DATA_GUIDE.md` | **Hướng dẫn chi tiết** về cấu trúc database & query |
| `database.py` | **Module kết nối MySQL** (đã cập nhật) |
| `app.py` | **App Flask chính** (đã cập nhật) |

---

## 🚀 **CÁC BƯỚC NHANH (3 PHÚT)**

### **Bước 1: Cài Đặt Package**
```bash
pip install mysql-connector-python
```

### **Bước 2: Cập Nhật Mật Khẩu MySQL**

Mở `import_data.py`, tìm dòng:
```python
'password': 'your_password',  # ← THAY MẬT KHẨU
```

Thay `your_password` thành mật khẩu MySQL của bạn.

### **Bước 3: Import Dữ Liệu**

```bash
python import_data.py
```

Chương trình sẽ:
- ✅ Tạo database `bien_so_xe`
- ✅ Tạo 5 bảng (plates, detections, provinces, vehicle_types, statistics)
- ✅ Import 27 biển số mẫu + dữ liệu chi tiết
- ✅ Hiển thị thống kê

### **Bước 4: Chạy App**

```bash
python app.py
```

App sẽ kết nối MySQL tự động! 🎉

---

## 📊 **CẤUTRÚC DATABASE**

### **5 Bảng Chính:**

```
┌──────────────┐
│   plates     │ ← Danh sách biển số (27 mẫu)
└──────┬───────┘
       ├─ 51G-12345 (phát hiện 5 lần)
       ├─ 30A-80008 (phát hiện 8 lần)
       └─ ... (25 biển khác)
       
┌──────────────┐
│  detections  │ ← Chi tiết mỗi lần phát hiện (45+ mẫu)
└──────────────┘
       └─ 51G-12345 lúc 08:15:30, confidence=0.98
       └─ 51G-12345 lúc 08:15:31, confidence=0.97
       └─ ... (43 lần phát hiện khác)

┌──────────────┐
│  provinces   │ ← 38 tỉnh/thành phố Việt Nam
└──────────────┘
       ├─ 51 = TP. HCM
       ├─ 30 = Hà Nội
       └─ ... (36 tỉnh khác)

┌──────────────┐
│ vehicle_types│ ← 9 loại xe
└──────────────┘
       ├─ Ô tô con
       ├─ Ô tô tải
       └─ ... (7 loại khác)

┌──────────────┐
│ statistics   │ ← Thống kê 4 ngày
└──────────────┘
       └─ 2026-04-18: 27 biển, 45 lần phát hiện, accuracy=94.8%
```

---

## 📝 **QUERY MẪU**

### 1️⃣ **Xem tất cả biển số**
```sql
SELECT plate_text, detection_count, confidence, vehicle_type 
FROM plates 
ORDER BY detection_count DESC;
```

### 2️⃣ **Lịch sử phát hiện của một biển**
```sql
SELECT detected_at, camera_source, confidence 
FROM detections 
WHERE plate_text = '51G-12345' 
ORDER BY detected_at DESC;
```

### 3️⃣ **Biển số từ TP.HCM**
```sql
SELECT p.plate_text, p.detection_count, pv.name 
FROM plates p 
LEFT JOIN provinces pv ON p.province_code = pv.code 
WHERE p.province_code = '51';
```

### 4️⃣ **Thống kê theo loại xe**
```sql
SELECT vehicle_type, COUNT(*) as count, AVG(confidence) 
FROM plates 
GROUP BY vehicle_type 
ORDER BY count DESC;
```

### 5️⃣ **Biển mới nhất phát hiện**
```sql
SELECT plate_text, detected_at, camera_source 
FROM detections 
ORDER BY detected_at DESC 
LIMIT 10;
```

**📚 Xem thêm 15+ query trong `IMPORT_DATA_GUIDE.md`**

---

## 🔧 **CẤU HÌNH MYSQL (CẬP NHẬT)**

Cập nhật 3 file này với mật khẩu MySQL:

### **1. database.py**
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # ← THAY ĐÂY
    'database': 'bien_so_xe',
    'port': 3306,
}
```

### **2. import_data.py**
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # ← THAY ĐÂY
    'port': 3306,
}
```

### **3. app.py** (Tự động dùng database.py)

---

## ✅ **KIỂM TRA SAU KHI IMPORT**

### Trong MySQL CLI:
```sql
USE bien_so_xe;

-- Kiểm tra bảng
SHOW TABLES;

-- Kiểm tra dữ liệu
SELECT COUNT(*) as total FROM plates;      -- Phải >= 27
SELECT COUNT(*) as total FROM detections;  -- Phải >= 45

-- Xem mẫu
SELECT * FROM plates LIMIT 5;
```

### Trong Python:
```python
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='bien_so_xe'
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM plates")
print(f"Tổng biển số: {cursor.fetchone()[0]}")

conn.close()
```

---

## 📍 **TỈNH/THÀNH PHỐ CÓ DỮ LIỆU**

| Mã | Tỉnh | Số Biển | Lần Phát Hiện |
|----|------|---------|---------------|
| 51 | TP.HCM | 9 | 20+ |
| 30 | Hà Nội | 4 | 15+ |
| 54 | Bình Dương | 4 | 12+ |
| 53 | Đồng Nai | 3 | 8+ |
| 29 | Hải Phòng | 2 | 5+ |
| 46 | Đà Nẵng | 1 | 1 |
| 64 | Cần Thơ | 1 | 2 |

---

## 🚨 **KHẮC PHỤC SỰ CỐ**

### **Lỗi: "Access denied for user 'root'@'localhost'"**
→ Mật khẩu sai. Kiểm tra lại trong `import_data.py` và `database.py`

### **Lỗi: "Can't connect to MySQL server"**
→ MySQL chưa chạy. Khởi động MySQL Server:
- Windows: `services.msc` → MySQL80 → Start
- Linux: `sudo systemctl start mysql`
- macOS: `brew services start mysql`

### **Lỗi: "Table 'bien_so_xe.plates' doesn't exist"**
→ Chạy `python import_data.py` để tạo bảng

### **Lỗi: "mysql.connector not found"**
→ Cài đặt: `pip install mysql-connector-python`

---

## 📚 **LỘNG TRÌNH HỌC**

1. ✅ Hiểu cấu trúc database (5 bảng)
2. ✅ Import dữ liệu mẫu
3. ✅ Viết các query cơ bản (SELECT, WHERE, ORDER BY)
4. ✅ Viết query nâng cao (JOIN, GROUP BY, HAVING)
5. ✅ Tích hợp query vào app.py

**📖 Tất cả ví dụ trong `IMPORT_DATA_GUIDE.md`**

---

## 🎯 **TIẾP THEO**

Sau khi import xong, bạn có thể:

1. **Viết API Flask để query database**
   ```python
   @app.route('/api/plates')
   def get_plates():
       # Lấy dữ liệu từ database
   ```

2. **Tạo dashboard thống kê**
3. **Phát triển tính năng tìm kiếm biển số**
4. **Xuất báo cáo thống kê**

---

## 📞 **LIÊN HỆ/HỖ TRỢ**

- ❓ Câu hỏi về query? → Xem `IMPORT_DATA_GUIDE.md`
- 🐛 Lỗi kết nối MySQL? → Kiểm tra `database.py`
- 📊 Muốn thêm dữ liệu? → Chỉnh sửa `bien_so_xe_sample.sql`

---

**🎉 Sẵn sàng! Hãy chạy: `python import_data.py`**
