# 🔄 CẬP NHẬT TOÀN BỘ HỆ THỐNG

## 📝 CÁC THAY ĐỔI CHÍNH

### 1️⃣ **database.py** - Cập nhật schema với ràng buộc khóa ngoại
✅ Tạo 5 bảng đúng thứ tự:
  - `provinces` (tỉnh - TẠO TRƯỚC)
  - `vehicle_types` (loại xe - TẠO TRƯỚC)
  - `plates` (biển số - TẠO SAU)
  - `detections` (chi tiết phát hiện)
  - `statistics` (thống kê)

✅ Thêm ràng buộc khóa ngoại:
  ```sql
  FOREIGN KEY (province_code) REFERENCES provinces(code)
  FOREIGN KEY (vehicle_type) REFERENCES vehicle_types(type_name)
  FOREIGN KEY (plate_id) REFERENCES plates(id)
  ```

✅ Thêm các hàm mới:
  - `check_province_exists()` - Kiểm tra tỉnh tồn tại
  - `check_vehicle_type_exists()` - Kiểm tra loại xe tồn tại
  - `add_or_update_province()` - Thêm/cập nhật tỉnh
  - `add_or_update_vehicle_type()` - Thêm/cập nhật loại xe
  - `get_all_plates_with_details()` - Lấy biển số kèm tỉnh & loại xe
  - `get_plate_detections()` - Lấy lịch sử chi tiết
  - `update_statistics()` - Cập nhật thống kê

---

### 2️⃣ **app.py** - Cập nhật logic lưu trữ & API

✅ Hàm `save_plate_to_db()` cải tiến:
  ```python
  save_plate_to_db(
      plate_text='51G-12345',
      province_code='51',      # Trích từ biển số
      vehicle_type='Ô tô con',  # Mặc định
      confidence=0.95
  )
  ```

✅ Hàm `extract_province_code()` mới:
  - Tách mã tỉnh (2 chữ số đầu) từ biển số
  - Ví dụ: '51G-12345' → '51'

✅ API Routes mới:
  - `GET /get_plates` - Danh sách biển số (kèm tỉnh, loại xe, lần phát hiện)
  - `GET /get_plate_details/<plate_text>` - Chi tiết một biển số
  - `GET /get_plate_detections/<plate_text>` - Lịch sử phát hiện chi tiết
  - `GET /get_statistics` - Thống kê hàng ngày
  - `GET /get_stats_by_province` - Thống kê theo tỉnh
  - `GET /get_stats_by_vehicle_type` - Thống kê theo loại xe

✅ Tự động tạo province_code khi lưu biển số

---

### 3️⃣ **templates/index.html** - Giao diện hiển thị dữ liệu

✅ Hiển thị thêm thông tin:
  ```
  51G-12345
  📍 Thành phố Hồ Chí Minh
  🚗 Ô tô con
  🔍 Phát hiện: 5 lần
  📊 Độ tin cậy: 98.0%
  ```

✅ CSS mới: `.info-badge` - Badge thông tin màu xanh

✅ JavaScript cập nhật:
  - Lấy & hiển thị `province_name`, `vehicle_type`, `detection_count`, `confidence`
  - Định dạng lại giao diện danh sách biển số

---

### 4️⃣ **bien_so_xe_sample.sql** - Cập nhật schema & dữ liệu

✅ Schema mới (đúng thứ tự):
  1. CREATE TABLE provinces
  2. CREATE TABLE vehicle_types
  3. CREATE TABLE plates (có FK)
  4. CREATE TABLE detections (có FK)
  5. CREATE TABLE statistics

✅ Dữ liệu mẫu:
  - 8 tỉnh (29, 30, 31, 46, 51, 53, 54, 64)
  - 4 loại xe (Ô tô con, khách, tải, xe máy)
  - 9 biển số (51G-12345, 51H-67890, 30A-80008...)
  - 17 lần phát hiện chi tiết
  - 2 ngày thống kê

---

## ⚡ CÁCH CHẠY

### 1. Import dữ liệu mới
```bash
python import_data.py
```
Hoặc dùng MySQL CLI:
```sql
SOURCE bien_so_xe_sample.sql;
```

### 2. Khởi động Flask server
```bash
python app.py
```

### 3. Truy cập giao diện web
```
http://127.0.0.1:5000
```

---

## 📊 CÁC API MỚI CÓ THỂTHỬ

### Danh sách biển số (kèm chi tiết)
```
GET http://127.0.0.1:5000/get_plates
```
Response:
```json
[
  {
    "plate_text": "51G-12345",
    "province_code": "51",
    "province_name": "Thành phố Hồ Chí Minh",
    "vehicle_type": "Ô tô con",
    "detection_count": 5,
    "confidence": 0.98,
    "timestamp": "2026-04-18 08:15:30"
  }
]
```

### Chi tiết một biển số
```
GET http://127.0.0.1:5000/get_plate_details/51G-12345
```

### Lịch sử phát hiện
```
GET http://127.0.0.1:5000/get_plate_detections/51G-12345
```

### Thống kê theo tỉnh
```
GET http://127.0.0.1:5000/get_stats_by_province
```

### Thống kê theo loại xe
```
GET http://127.0.0.1:5000/get_stats_by_vehicle_type
```

---

## 🔗 RÀNG BUỘC KHÓA NGOẠI (FK)

```
provinces(code) ← plates(province_code)
                ↑ (ON DELETE SET NULL, ON UPDATE CASCADE)

vehicle_types(type_name) ← plates(vehicle_type)
                         ↑ (ON DELETE SET NULL, ON UPDATE CASCADE)

plates(id) ← detections(plate_id)
           ↑ (ON DELETE CASCADE, ON UPDATE CASCADE)
```

**Lợi ích:**
✅ Bảo toàn tính toàn vẹn dữ liệu
✅ Tự động cập nhật khi tỉnh/loại xe thay đổi
✅ Xóa biển số sẽ xóa toàn bộ lịch sử phát hiện

---

## ✅ KIỂM TRA

Sau khi import dữ liệu, kiểm tra:

```sql
-- Xem số lượng dữ liệu
SELECT COUNT(*) as total_plates FROM plates;       -- Phải >= 9
SELECT COUNT(*) as total_detections FROM detections; -- Phải >= 17
SELECT COUNT(*) as total_provinces FROM provinces;   -- Phải >= 8
SELECT COUNT(*) as total_vehicle_types FROM vehicle_types; -- Phải >= 4

-- Xem JOIN hoạt động
SELECT * FROM plates p
JOIN provinces pv ON p.province_code = pv.code
JOIN vehicle_types vt ON p.vehicle_type = vt.type_name
LIMIT 5;
```

---

## 🎯 TIẾP THEO

1. ✅ Chạy `python import_data.py` để import dữ liệu
2. ✅ Chạy `python app.py` để khởi động server
3. ✅ Mở `http://127.0.0.1:5000` để xem giao diện mới
4. ✅ Kiểm tra danh sách biển số với thông tin đầy đủ

---

**Tất cả đã sẵn sàng! 🚀**
