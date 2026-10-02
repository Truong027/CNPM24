# Phân hệ Backend & AI (BE) - Hệ thống Quản lý Bãi xe

Thư mục này chứa toàn bộ mã nguồn máy chủ, API RESTful, tầng xử lý cơ sở dữ liệu MySQL và các mô hình Trí tuệ nhân tạo (YOLO + OCR).

## Cấu trúc thư mục
```text
be/
├── app.py                     # Máy chủ Flask chính, xử lý API và luồng Video Streaming
├── database.py                # Tầng kết nối & thực thi truy vấn CSDL MySQL
├── plate_ocr_inference.py     # Module suy luận nhận diện ký tự biển số bằng CRNN-CTC
├── crnn_ocr_wrapper.py        # Lớp bọc tương thích OCR
├── plate_ocr_integration.py   # Module tích hợp OCR vào pipeline nhận diện
├── check_database.py          # Script kiểm tra kết nối CSDL
├── create_database.py         # Script tự động khởi tạo bảng CSDL
├── httt_quan_ly_bai_xe_ai.sql # Mã nguồn SQL đầy đủ của cơ sở dữ liệu
├── yolov8s.pt                 # Trọng số mô hình phát hiện vị trí biển số xe (YOLOv8)
├── artifacts/                 # Thư mục chứa trọng số mô hình CRNN-CTC và từ điển vocab.json
│   └── plate_ocr/
├── requirements.txt           # Danh sách thư viện Python cần thiết
└── test_detection.py          # Script kiểm tra phát hiện biển số trên ảnh mẫu
```

## Hướng dẫn khởi chạy Backend

1. **Kích hoạt môi trường ảo:**
   ```powershell
   cd d:\CNPM24CT2_OngThanQuocTruong
   .venv\Scripts\activate
   cd BienSoXe\be
   ```

2. **Cài đặt thư viện phụ thuộc (nếu chưa cài):**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Khởi tạo và kiểm tra CSDL MySQL:**
   - Đảm bảo MySQL đang chạy ở cổng `3306`.
   - Kiểm tra kết nối:
     ```powershell
     python check_database.py
     ```

4. **Chạy server Backend:**
   ```powershell
   python app.py
   ```
   *Server sẽ tự động nạp giao diện từ thư mục `../fe/templates/` và phục vụ tại: `http://127.0.0.1:5000`.*
