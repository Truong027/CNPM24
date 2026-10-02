"""
Script để test YOLO detection và normalize_plate_text
"""
import cv2
import re
from ultralytics import YOLO
import torch

# ===== KẾT NỐI MODEL =====
MODEL_PATH = "runs/detect/train/weights/best.pt"
model = YOLO(MODEL_PATH)
print(f"✅ Model tải từ: {MODEL_PATH}")

# ===== TEST NORMALIZE FUNCTION =====
def normalize_plate_text(text):
    if not text:
        return ""
    text = text.upper().strip()
    general_replacements = {
        '|': '1', 'I': '1', 'Q': '0', 'O': '0', 'D': '0', 'S': '5',
        'Z': '7', 'T': '7', 'G': '6',
    }
    for old, new in general_replacements.items():
        text = text.replace(old, new)
    text_filtered = re.sub(r'[^A-Z0-9]', '', text)
    
    # Thử tìm định dạng 2 hàng (51G 12345)
    match = re.search(r'(\d{2})([A-Z0-9]{1,2})(\d{5})', text_filtered)
    if not match:
        # Nếu không, thử tìm định dạng đã có dấu chấm (51G123.45)
        match_dot = re.search(r'(\d{2})([A-Z0-9]{1,2})(\d{3})(\d{2})', text_filtered)
        if match_dot:
            tinh, series_raw, so_dau, so_cuoi = match_dot.groups()
            so_raw = so_dau + so_cuoi
        else:
            return ""
    else:
         tinh, series_raw, so_raw = match.groups()

    # Xử lý các phần
    tinh_clean = tinh.replace('B', '8').replace('L', '1').replace('O', '0').replace('D', '0').replace('G', '6').replace('S', '5')
    tinh_final = re.sub(r'[^0-9]', '', tinh_clean)
    
    series_clean = series_raw.replace('8', 'B').replace('3', 'B').replace('1', 'L').replace('0', 'O').replace('6', 'G').replace('5', 'S')
    series_final = re.sub(r'[^A-Z]', '', series_clean)
    series_final = series_final[:1] if series_final else ""
    
    so_clean = so_raw.replace('B', '8').replace('L', '1').replace('O', '0').replace('D', '0').replace('G', '6').replace('S', '5')
    so_final = re.sub(r'[^0-9]', '', so_clean)
    
    if len(tinh_final) == 2 and series_final and len(so_final) == 5:
        return f"{tinh_final}{series_final}-{so_final[:3]}.{so_final[3:]}"
        
    return ""

# ===== TEST VỚI WEBCAM =====
print("\n⌛ Đang mở Webcam để test (nhấn 'q' để thoát)...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Không thể mở webcam!")
    exit()

frame_count = 0
detected_plates = set()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # YOLO inference
    results = model.predict(frame, conf=0.3, imgsz=480, verbose=False)
    
    # Vẽ results
    annotated_frame = results[0].plot()
    
    # In thông tin
    num_detections = len(results[0].boxes)
    if num_detections > 0:
        print(f"\n🎯 Frame {frame_count}: Phát hiện {num_detections} biển số")
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            conf = box.conf[0].item()
            print(f"   - Confidence: {conf:.2f}, Box: ({x1}, {y1}) -> ({x2}, {y2})")
    
    # Hiển thị
    cv2.imshow("YOLO Detection Test", annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n✅ Test hoàn thành! Tổng frames: {frame_count}")

# ===== TEST NORMALIZE FUNCTION =====
print("\n" + "="*50)
print("🧪 TEST NORMALIZE_PLATE_TEXT")
print("="*50)

test_cases = [
    "51G12345",
    "51G-12345",
    "51 G 12345",
    "51 G 123 45",
    "30A80008",
    "30A-80008",
    "INVALID",
    "",
]

for test in test_cases:
    result = normalize_plate_text(test)
    print(f"Input: '{test}' -> Output: '{result}'")
