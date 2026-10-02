# TODO - Train OCR chữ Việt Nam (biển số VN)

## Mục tiêu
Train mô hình OCR nhận diện **chuỗi biển số VN** (ký tự A–Z không dấu + 0–9, dạng XXY-NNN.NN) thay cho EasyOCR.

## Các bước
- [ ] B1: Chốt kiến trúc nhận diện (CRNN-CTC khuyến nghị) và tokenizer/vocab cho A–Z0–9 + ký tự '-' '.'
- [x] B2: (đã chuẩn bị khung) Dataset cần tạo thủ công/hoặc qua script
- [ ] B2.1: Tạo script sinh dataset `data/plate_ocr/images` + `labels` từ YOLO crop + gán label

- [ ] B3: Tạo pipeline augment (lệch sáng, mờ, nhiễu, warp nhẹ, blur, motion blur, phản quang)
- [ ] B4: Huấn luyện CRNN-CTC (train/val split, early stopping, lưu best checkpoint)
- [ ] B5: Viết `recognize_plate_text_with_confidence()` dùng model mới (có normalize + validate + voting theo track)
- [ ] B6: Thay thế trong `app.py` chỗ gọi EasyOCR
- [ ] B7: Chạy test nhanh trên ảnh/video mẫu + đo exact plate accuracy
- [ ] B8: Cập nhật requirements/model path và hướng dẫn chạy

