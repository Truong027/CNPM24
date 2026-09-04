# OCR train (VN biển số) – hướng dẫn chạy

Mục tiêu: train mô hình OCR nhận diện **chuỗi biển số VN** (A–Z không dấu + 0–9 + '-', '.') để thay EasyOCR.

## 1) Dataset (bắt buộc)
Tạo thư mục:
- `data/plate_ocr/images/` : ảnh crop biển số (jpg/png/…)
- `data/plate_ocr/labels/` : nhãn text, cùng tên file với ảnh

Quy ước tên:
- `data/plate_ocr/images/ABC001.jpg` ↔ `data/plate_ocr/labels/ABC001.txt`

Nội dung mỗi file `.txt`:
- 1 dòng duy nhất: chuỗi biển số chuẩn, in hoa (không dấu), ví dụ:
  - `51G-123.45`
  - `30A-800.08`

## 2) Train
Kích hoạt venv rồi chạy:
```bash
(.venv) python ocr_train_plate_recognizer.py
```

Sau khi train, model sẽ lưu tại:
- `artifacts/plate_ocr/model.pt`
- `artifacts/plate_ocr/vocab.json`

## 3) Lưu ý
- Hiện repo chưa có sẵn dataset `data/plate_ocr/*`, nên lệnh train sẽ báo "Dataset not found".
- Cần ít nhất ~10 mẫu để chạy được; để chất lượng tốt nên có hàng trăm → hàng nghìn crop.

## 4) Bước tiếp theo (nếu muốn thay trong app)
Sau khi có model, cần:
- viết hàm recognize bằng PyTorch model
- thay `get_shared_ocr_reader()` + `read_plate_text_with_confidence()` trong `app.py`

Tài liệu này chỉ bao gồm bước train recognition.

