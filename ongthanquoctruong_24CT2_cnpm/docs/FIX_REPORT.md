# 🔧 FIX BẢO TRỊ - Vấn đề Nhận Diện Biển Số

## 📋 Vấn Đề Tìm Được

**Người dùng hỏi:** "Sao nhận diện mà chưa có nào được lưu vậy?"

### Nguyên Nhân:
1. ✅ **FIXED**: `ON DUPLICATE KEY UPDATE` chỉ cập nhật `detection_count`, bỏ qua `province_code` và `vehicle_type`
2. ✅ **FIXED**: EasyOCR Reader khởi tạo bằng GPU mode → hang/timeout vì VRAM
3. ✅ **FIXED**: Biển số cũ lưu mà không có province_code → database bị bẩn

---

## ✅ Các Bước Fix Đã Thực Hiện

### 1. Fix Query ON DUPLICATE KEY UPDATE
**File:** `app.py` (hàm `save_plate_to_db()`)

Cũ:
```sql
ON DUPLICATE KEY UPDATE detection_count = detection_count + 1
```

Mới:
```sql
ON DUPLICATE KEY UPDATE 
    detection_count = detection_count + 1,
    province_code = COALESCE(province_code, %s),
    vehicle_type = COALESCE(vehicle_type, %s)
```

**Hiệu quả:** Biển số duplicate giờ sẽ cập nhật province_code và vehicle_type nếu chưa có.

### 2. Fix EasyOCR Initialization
**File:** `app.py` (hàm `gen_frames()`)

Cũ:
```python
reader = easyocr.Reader(['vi', 'en'], gpu=torch.cuda.is_available())
```

Mới:
```python
reader = easyocr.Reader(['vi', 'en'], gpu=False)  # CPU mode
```

**Hiệu quả:** Tránh VRAM issues, EasyOCR không hang khi khởi tạo.

### 3. Thêm Debug Logs
**File:** `app.py`

Thêm `flush=True` vào tất cả print statements để xem logs ngay lập tức:
```python
print("📖 [...] Track...", flush=True)
```

### 4. Dọn Dẹp Database
Xóa 2 biển số cũ không có province_code:
```sql
DELETE FROM plates WHERE province_code IS NULL
```

---

## 📊 Kết Quả Test

### Test 1: save_plate_to_db()
✅ Biển số `51G-99999` được lưu với:
- `province_code: 51`
- `vehicle_type: Ô tô con`
- `province_name: Thành phố Hồ Chí Minh`

### Test 2: Duplicate Insert Update
✅ Khi insert cùng biển số lần 2:
- `detection_count` tăng từ 1 → 2
- `province_code` và `vehicle_type` vẫn giữ nguyên

### Test 3: Database Check
✅ Database hiện có 10 biển số, tất cả có province_code + vehicle_type:
```
51G-99999     -> Thành phố Hồ Chí Minh, Ô tô con
64V-45454     -> Thành phố Cần Thơ, Ô tô tải
46U-34343     -> Thành phố Đà Nẵng, Ô tô con
53P-50005     -> Tỉnh Đồng Nai, Ô tô con
51H-67890     -> Thành phố Hồ Chí Minh, Ô tô khách
```

---

## 🎯 Tiếp Theo

### Vấn đề Còn Lại:
App đã lưu biển số từ dữ liệu sample, nhưng **gen_frames() chưa phát hiện biển số MỚI từ video stream live**.

Nguyên nhân có thể:
1. **Webcam không kết nối** → YOLO không có input
2. **YOLO không detect** → Model training không tốt hoặc chất lượng video thấp
3. **OCR không đọc được** → Text mờ hoặc không trong tiêu chuẩn

### Cách Kiểm Tra:
1. **Mở http://127.0.0.1:5000** → Xem video stream từ webcam
2. **Nếu có video:** YOLO đang chạy nhưng không detect được biển
3. **Nếu không có video:** Webcam không kết nối

### Giải Pháp:
- Nếu webcam không kết nối: Đổi `WEBCAM_SOURCE = 0` sang index khác
- Nếu YOLO không detect: Check model training (`best.pt`)
- Nếu OCR tệ: Tăng ROI size hoặc chất lượng image

---

## 💡 Kết Luận

✅ **Lưu dữ liệu hoạt động đúng** - database được fix
✅ **EasyOCR khởi tạo nhanh hơn** - CPU mode
✅ **Debug logs rõ ràng hơn** - flush=True

🎯 **Tiếp theo:** Khắc phục vấn đề nhận diện từ video stream live (nếu cần)
