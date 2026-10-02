"""
Script để tạo dataset cho train OCR nhận diện biển số.
Sử dụng YOLO detect để crop biển số từ video/ảnh.
"""

import os
import cv2
from ultralytics import YOLO
from pathlib import Path
import argparse

# ===== CẤU HÌNH =====
MODEL_PATH = "runs/detect/train/weights/best.pt"
OUTPUT_DIR = "data/plate_ocr"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
LABELS_DIR = os.path.join(OUTPUT_DIR, "labels")

# Tạo thư mục nếu chưa tồn tại
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(LABELS_DIR, exist_ok=True)

# Load YOLO model
print(f"📥 Đang load model từ: {MODEL_PATH}")
model = YOLO(MODEL_PATH)

def crop_plates_from_video(video_path, conf_threshold=0.5, max_crops=None):
    """
    Crop biển số từ video.
    
    Args:
        video_path: Đường dẫn video (hoặc webcam index 0)
        conf_threshold: Mức tin cậy detection tối thiểu
        max_crops: Giới hạn số ảnh crop (None = không giới hạn)
    """
    print(f"\n🎬 Xử lý video: {video_path}")
    
    if isinstance(video_path, int) or video_path == "0":
        cap = cv2.VideoCapture(0)
        print("📹 Sử dụng Webcam")
    else:
        cap = cv2.VideoCapture(video_path)
        print(f"📹 Sử dụng video file: {video_path}")
    
    if not cap.isOpened():
        print("❌ Không thể mở video!")
        return
    
    frame_count = 0
    crop_count = 0
    skipped = 0
    
    while crop_count < (max_crops or float('inf')):
        ret, frame = cap.read()
        if not ret:
            print("\n✅ Video kết thúc")
            break
        
        frame_count += 1
        if frame_count % 5 != 0:  # Lấy 1 frame/5 để tránh quá nhiều ảnh tương tự
            continue
        
        # YOLO detect
        results = model.predict(frame, conf=conf_threshold, verbose=False)
        
        if len(results[0].boxes) > 0:
            for idx, box in enumerate(results[0].boxes):
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = box.conf[0].item()
                
                # Crop biển số
                plate_crop = frame[y1:y2, x1:x2]
                
                # Bỏ qua nếu quá nhỏ
                if plate_crop.shape[0] < 20 or plate_crop.shape[1] < 50:
                    skipped += 1
                    continue
                
                # Lưu ảnh
                crop_id = f"{crop_count:05d}"
                img_path = os.path.join(IMAGES_DIR, f"{crop_id}.jpg")
                cv2.imwrite(img_path, plate_crop)
                
                # Tạo file label trống (cần manual label sau)
                label_path = os.path.join(LABELS_DIR, f"{crop_id}.txt")
                with open(label_path, 'w') as f:
                    f.write("")  # Trống, chờ manual input
                
                crop_count += 1
                print(f"  ✅ Crop #{crop_count}: conf={conf:.2f}, size={plate_crop.shape[1]}x{plate_crop.shape[0]}")
                
                if crop_count >= (max_crops or float('inf')):
                    break
        
        # Hiển thị tiến độ
        if frame_count % 30 == 0:
            print(f"  ⏳ Frame: {frame_count}, Crops: {crop_count}")
        
        # Nhấn 'q' để dừng khi dùng webcam
        if isinstance(video_path, int) or video_path == "0":
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n⏹️ Dừng webcam")
                break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n📊 Kết quả:")
    print(f"  - Tổng frame xử lý: {frame_count}")
    print(f"  - Crop thành công: {crop_count}")
    print(f"  - Bỏ qua (quá nhỏ): {skipped}")
    print(f"  - Thư mục: {IMAGES_DIR}/")

def crop_plates_from_image(image_path, conf_threshold=0.5):
    """
    Crop biển số từ ảnh.
    """
    print(f"\n📷 Xử lý ảnh: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ Ảnh không tồn tại: {image_path}")
        return
    
    frame = cv2.imread(image_path)
    if frame is None:
        print("❌ Không thể đọc ảnh!")
        return
    
    # YOLO detect
    results = model.predict(frame, conf=conf_threshold, verbose=False)
    
    crop_count = 0
    for idx, box in enumerate(results[0].boxes):
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        conf = box.conf[0].item()
        
        plate_crop = frame[y1:y2, x1:x2]
        
        if plate_crop.shape[0] < 20 or plate_crop.shape[1] < 50:
            continue
        
        crop_id = f"{crop_count:05d}"
        img_path = os.path.join(IMAGES_DIR, f"{crop_id}.jpg")
        cv2.imwrite(img_path, plate_crop)
        
        label_path = os.path.join(LABELS_DIR, f"{crop_id}.txt")
        with open(label_path, 'w') as f:
            f.write("")
        
        crop_count += 1
        print(f"  ✅ Crop #{crop_count}: conf={conf:.2f}")
    
    print(f"  📊 Tổng crops: {crop_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo dataset OCR biển số từ video/ảnh")
    parser.add_argument("--video", type=str, help="Đường dẫn video (hoặc '0' cho webcam)", default="0")
    parser.add_argument("--image", type=str, help="Đường dẫn ảnh (thay vì video)")
    parser.add_argument("--conf", type=float, default=0.5, help="Confidence threshold")
    parser.add_argument("--max-crops", type=int, help="Giới hạn số ảnh crop")
    
    args = parser.parse_args()
    
    if args.image:
        crop_plates_from_image(args.image, args.conf)
    else:
        video_source = 0 if args.video == "0" else args.video
        crop_plates_from_video(video_source, args.conf, args.max_crops)
    
    print(f"\n💡 Bước tiếp theo: Manual label các ảnh trong {LABELS_DIR}/")
