# Thư mục Kiểm Thử (Tests) - Quản Lý Bãi Đỗ Xe Thông Minh AI

Thư mục này chứa toàn bộ các kịch bản kiểm thử (Unit tests, Integration tests, API tests) cho hệ thống.

## Danh sách tệp kiểm thử

| Tên File | Chức Năng Kiểm Thử |
| :--- | :--- |
| `test_cinema_parking.py` | Kiểm thử logic sơ đồ bãi đỗ xe kiểu rạp phim (100 ô 2 tầng hầm B1/B2, API `/api/parking/map`, đặt chỗ, đổi vị trí) |
| `test_api_simple.py` | Kiểm thử endpoint lấy danh sách biển số (`/get_plates`) |
| `test_save_plate.py` | Kiểm thử hàm `save_plate_to_db` và tra cứu bản ghi trong CSDL |
| `test_detection.py` | Kiểm thử mô hình nhận diện biển số YOLOv8 và chuẩn hóa chuỗi ký tự |
| `test_get_plates_func.py` | Kiểm thử hàm truy vấn chi tiết biển số `database.get_all_plates_with_details()` |
| `test_http_request.py` | Kiểm thử luồng phát video streaming `/video_feed_webcam` |
| `test_30f.jpg` | Ảnh mẫu biển số ô tô phục vụ test offline |

## Cách chạy kiểm thử

### 1. Chạy toàn bộ Unit Tests với `unittest`:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

### 2. Chạy từng test cụ thể:
```powershell
python tests/test_cinema_parking.py
python tests/test_save_plate.py
python tests/test_api_simple.py
```
