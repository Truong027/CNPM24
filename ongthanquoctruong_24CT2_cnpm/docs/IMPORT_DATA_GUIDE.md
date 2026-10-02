# 📊 HƯỚNG DẪN IMPORT DỮ LIỆU MẪU MYSQL

## 📋 Cấu Trúc Cơ Sở Dữ Liệu

### 🗂️ **5 Bảng Chính:**

#### **1. plates** (Biển Số Xe)
- `id` - ID tự động tăng (khóa chính)
- `plate_text` - Biển số (ví dụ: 51G-12345) - UNIQUE
- `timestamp` - Thời gian phát hiện
- `detection_count` - Số lần phát hiện
- `confidence` - Độ tin cậy (0-1)
- `province_code` - Mã tỉnh (51=TP.HCM, 54=Bình Dương...)
- `vehicle_type` - Loại xe (Ô tô, Xe máy...)

```sql
-- Ví dụ dữ liệu:
51G-12345 | 2026-04-18 08:15:30 | 5 lần phát hiện | 0.98 | 51 | Ô tô con
30A-80008 | 2026-04-18 07:30:00 | 8 lần phát hiện | 0.97 | 30 | Ô tô con
```

#### **2. detections** (Lịch Sử Chi Tiết)
- `id` - ID chi tiết phát hiện
- `plate_id` - Liên kết tới bảng plates
- `plate_text` - Biển số
- `detected_at` - Thời gian phát hiện
- `confidence` - Độ tin cậy của lần phát hiện này
- `camera_source` - Nguồn camera (webcam_0, ipcam_office...)
- `frame_number` - Số khung hình video
- `raw_text` - Text gốc trước chuẩn hóa

```sql
-- Ví dụ: Cùng một biển số 51G-12345 được phát hiện 5 lần
| plate_id=1 | plate_text=51G-12345 | detected_at=08:15:30 | confidence=0.98 | raw_text=51G12345
| plate_id=1 | plate_text=51G-12345 | detected_at=08:15:31 | confidence=0.97 | raw_text=51G-12345
...
```

#### **3. provinces** (Tỉnh/Thành Phố)
- `id` - ID tỉnh
- `code` - Mã tỉnh (29, 30, 51, 54...)
- `name` - Tên tiếng Việt
- `name_en` - Tên tiếng Anh
- `region` - Vùng (Bắc, Trung, Nam)

```sql
| code=51 | name=TP. HCM | region=Nam Bộ
| code=30 | name=Hà Nội | region=Bắc Bộ
```

#### **4. vehicle_types** (Loại Xe)
- `id` - ID loại xe
- `type_name` - Tên loại xe
- `seats` - Số chỗ ngồi
- `max_weight` - Trọng tải tối đa

```sql
| type_name=Ô tô con | seats=4 | max_weight=1.5
| type_name=Ô tô khách | seats=30 | max_weight=10
```

#### **5. statistics** (Thống Kê)
- `id` - ID thống kê
- `date_stat` - Ngày thống kê
- `total_plates` - Tổng số biển số độc lập
- `total_detections` - Tổng số lần phát hiện
- `avg_confidence` - Độ tin cậy trung bình
- `top_plate` - Biển số phát hiện nhiều nhất

---

## 🚀 **CÁCH IMPORT DỮ LIỆU**

### **Cách 1: Dùng MySQL Command Line (Dễ Nhất)**

#### Bước 1: Mở Command Prompt / Terminal
```bash
cd D:\AI\BienSoXe
```

#### Bước 2: Đăng nhập MySQL
```bash
mysql -u root -p
```
(Nhập mật khẩu MySQL của bạn)

#### Bước 3: Import File SQL
```bash
mysql -u root -p < bien_so_xe_sample.sql
```

Hoặc nếu bạn đã vào MySQL CLI:
```sql
SOURCE bien_so_xe_sample.sql;
```

#### Bước 4: Kiểm tra
```sql
USE bien_so_xe;
SELECT * FROM plates LIMIT 5;
```

---

### **Cách 2: Dùng MySQL Workbench (GUI)**

1. Mở MySQL Workbench
2. Kết nối tới MySQL Server của bạn
3. Tạo tab mới: File → New Query Tab
4. Mở file: File → Open SQL Script → `bien_so_xe_sample.sql`
5. Nhấn ⚡ **Execute** (Ctrl + Shift + Enter)
6. Chọn **Use Database**: bien_so_xe

---

### **Cách 3: Dùng Python Script**

Tạo file `import_data.py`:

```python
import mysql.connector
from mysql.connector import Error

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # ← THAY MẬT KHẨU
}

try:
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    # Đọc file SQL
    with open('bien_so_xe_sample.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Thực thi từng câu lệnh
    for statement in sql_script.split(';'):
        if statement.strip():
            cursor.execute(statement)
    
    conn.commit()
    print("✅ Import dữ liệu thành công!")
    
except Error as e:
    print(f"❌ Lỗi: {e}")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
```

Chạy:
```bash
python import_data.py
```

---

## 📊 **CÁC QUERY PHỔ BIẾN**

### 1️⃣ **Xem tất cả biển số TP.HCM**
```sql
SELECT * FROM plates 
WHERE province_code = '51'
ORDER BY detection_count DESC;
```

### 2️⃣ **Biển số phát hiện nhiều nhất**
```sql
SELECT plate_text, detection_count, confidence
FROM plates
ORDER BY detection_count DESC
LIMIT 10;
```

### 3️⃣ **Biển số được phát hiện trong 24h qua**
```sql
SELECT * FROM plates
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY)
ORDER BY timestamp DESC;
```

### 4️⃣ **Lịch sử chi tiết của một biển số**
```sql
SELECT detected_at, camera_source, confidence, raw_text
FROM detections
WHERE plate_text = '51G-12345'
ORDER BY detected_at DESC;
```

### 5️⃣ **Thống kê theo tỉnh**
```sql
SELECT 
    pv.code,
    pv.name,
    COUNT(p.id) as total_plates,
    SUM(p.detection_count) as total_detections,
    AVG(p.confidence) as avg_confidence
FROM plates p
LEFT JOIN provinces pv ON p.province_code = pv.code
GROUP BY pv.code, pv.name
ORDER BY total_detections DESC;
```

### 6️⃣ **Thống kê theo loại xe**
```sql
SELECT 
    vehicle_type,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence
FROM plates
GROUP BY vehicle_type
ORDER BY count DESC;
```

### 7️⃣ **Biển số mới nhất phát hiện**
```sql
SELECT plate_text, timestamp, camera_source
FROM detections
ORDER BY detected_at DESC
LIMIT 20;
```

### 8️⃣ **Độ tin cậy trung bình theo camera**
```sql
SELECT 
    camera_source,
    COUNT(*) as detections,
    AVG(confidence) as avg_confidence
FROM detections
GROUP BY camera_source
ORDER BY avg_confidence DESC;
```

### 9️⃣ **Biển số có độ tin cậy thấp (dưới 90%)**
```sql
SELECT * FROM plates
WHERE confidence < 0.90
ORDER BY confidence ASC;
```

### 🔟 **Biển số chưa được xác minh (phát hiện chỉ 1 lần)**
```sql
SELECT plate_text, confidence, timestamp
FROM plates
WHERE detection_count = 1
ORDER BY timestamp DESC;
```

---

## 🔗 **QUAN HỆ GIỮA CÁC BẢNG**

```
┌─────────────┐
│  provinces  │  (code: 51, 30, 54...)
└──────┬──────┘
       │ (province_code)
       ├─────────────────┐
       │                 │
┌──────┴──────┐    ┌─────┴──────┐
│   plates    │    │vehicle_types│
└──────┬──────┘    └─────────────┘
       │ (plate_id)
       │
┌──────┴──────────┐
│  detections     │  (Chi tiết từng lần phát hiện)
└─────────────────┘
```

**Ví dụ Relationship:**
- plates có nhiều detections (1:N)
- provinces có nhiều plates (1:N)
- vehicle_types có nhiều plates (1:N)

---

## ✅ **KIỂM TRA SAU KHI IMPORT**

Chạy các lệnh này để kiểm tra:

```sql
-- Kiểm tra số bảng
SHOW TABLES;

-- Kiểm tra cấu trúc bảng plates
DESC plates;

-- Kiểm tra dữ liệu
SELECT COUNT(*) FROM plates;      -- Phải >= 27 biển số
SELECT COUNT(*) FROM detections;  -- Phải >= 45 lần phát hiện

-- Kiểm tra tỉnh
SELECT COUNT(*) FROM provinces;   -- Phải = 38 tỉnh

-- Kiểm tra thống kê
SELECT * FROM statistics;
```

---

## 🎯 **SỬ DỤNG VỚI APP.PY**

Cập nhật `database.py`:

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # ← THAY MẬT KHẨU
    'database': 'bien_so_xe',     # ← Dữ liệu đã tạo
}
```

Chạy app:
```bash
python app.py
```

App sẽ tự động kết nối và bắt đầu lưu biển số mới vào database! 🚀

---

## 📝 **GỒM DỮ LIỆU**

File `bien_so_xe_sample.sql` chứa:

✅ **27 biển số xe** từ các tỉnh khác nhau:
- TP.HCM (51): 9 biển
- Hà Nội (30): 4 biển
- Bình Dương (54): 4 biển
- Đồng Nai (53): 3 biển
- Hải Phòng (29): 2 biển
- Đà Nẵng (46): 1 biển
- Cần Thơ (64): 1 biển

✅ **45+ lần phát hiện** cho các biển số khác nhau

✅ **38 tỉnh/thành phố** Việt Nam

✅ **9 loại xe** khác nhau

✅ **4 ngày thống kê** (2026-04-15 đến 2026-04-18)

---

## ❓ **CÂU HỎI THƯỜNG GẶP**

**Q: Dữ liệu sẽ bị xóa nếu chạy lại SQL không?**
A: Không, file SQL có `DROP DATABASE IF EXISTS` ở đầu, nên sẽ xóa database cũ và tạo mới. Nếu muốn giữ dữ liệu, hãy xóa dòng đó.

**Q: Tôi có thể thêm biển số tùy chỉnh không?**
A: Có, chỉnh sửa phần "CHÈN DỮ LIỆU MẪU" trong file SQL.

**Q: Camera_source có ý nghĩa gì?**
A: Cho biết biển số được phát hiện từ camera nào (webcam_0, ipcam_office...). Bạn có thể thay đổi tên này trong app.py.

---

Xong! Database sẵn sàng để viết query! 🎉
