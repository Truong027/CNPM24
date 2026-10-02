"""
Script để manual label các ảnh biển số.
Hiển thị ảnh và nhập text biển số tương ứng.
"""

import os
import cv2
from pathlib import Path

IMAGES_DIR = "data/plate_ocr/images"
LABELS_DIR = "data/plate_ocr/labels"

def label_images_interactive():
    """
    Hiển thị ảnh và nhập text biển số từ bàn phím.
    Format: 51G-123.45 hoặc 30A-800.08
    """
    
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ Thư mục không tồn tại: {IMAGES_DIR}")
        return
    
    images = sorted([f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.png', '.jpeg'))])
    
    if not images:
        print(f"❌ Không có ảnh nào trong {IMAGES_DIR}")
        return
    
    print(f"📊 Tìm thấy {len(images)} ảnh")
    print("💡 Nhập biển số theo format: 51G-123.45")
    print("   - Nhấn 's' để bỏ qua ảnh này")
    print("   - Nhấn 'q' để thoát\n")
    
    labeled_count = 0
    
    for idx, img_file in enumerate(images):
        img_path = os.path.join(IMAGES_DIR, img_file)
        label_file = img_file.rsplit('.', 1)[0] + '.txt'
        label_path = os.path.join(LABELS_DIR, label_file)
        
        # Kiểm tra nếu đã có label
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                existing = f.read().strip()
                if existing:
                    print(f"⏭️  [{idx+1}/{len(images)}] {img_file} - Đã có label: {existing}")
                    labeled_count += 1
                    continue
        
        # Hiển thị ảnh
        img = cv2.imread(img_path)
        if img is None:
            print(f"❌ Không thể đọc: {img_file}")
            continue
        
        # Resize để hiển thị
        h, w = img.shape[:2]
        if w > 400:
            scale = 400 / w
            img_display = cv2.resize(img, (400, int(h * scale)))
        else:
            img_display = img
        
        cv2.imshow("Plate OCR Labeler", img_display)
        cv2.setWindowTitle("Plate OCR Labeler", f"[{idx+1}/{len(images)}] {img_file}")
        
        # Nhập từ console
        print(f"\n[{idx+1}/{len(images)}] {img_file}")
        user_input = input("Nhập biển số (hoặc 's' để bỏ qua, 'q' để thoát): ").strip().upper()
        
        if user_input.lower() == 'q':
            print("👋 Thoát")
            break
        
        if user_input.lower() == 's':
            print("⏭️  Bỏ qua")
            continue
        
        # Validate format cơ bản
        if not user_input or len(user_input) < 7:
            print("⚠️  Format không hợp lệ, bỏ qua")
            continue
        
        # Lưu label
        with open(label_path, 'w') as f:
            f.write(user_input)
        
        labeled_count += 1
        print(f"✅ Đã lưu: {user_input}")
    
    cv2.destroyAllWindows()
    print(f"\n✅ Hoàn thành! Labeled: {labeled_count}/{len(images)}")

def batch_rename_labels(prefix="PLATE"):
    """
    Đổi tên các ảnh theo format: PLATE00001.jpg, PLATE00002.jpg, ...
    """
    images = sorted([f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.png', '.jpeg'))])
    
    print(f"📝 Đổi tên {len(images)} ảnh...")
    
    for idx, old_name in enumerate(images):
        old_path = os.path.join(IMAGES_DIR, old_name)
        old_label_path = os.path.join(LABELS_DIR, old_name.rsplit('.', 1)[0] + '.txt')
        
        ext = old_name.rsplit('.', 1)[1]
        new_name = f"{prefix}{idx+1:05d}.{ext}"
        new_path = os.path.join(IMAGES_DIR, new_name)
        new_label_path = os.path.join(LABELS_DIR, f"{prefix}{idx+1:05d}.txt")
        
        # Rename ảnh
        if old_path != new_path:
            os.rename(old_path, new_path)
        
        # Rename label
        if os.path.exists(old_label_path):
            os.rename(old_label_path, new_label_path)
        else:
            # Tạo file label trống
            open(new_label_path, 'a').close()
    
    print(f"✅ Đã đổi tên hoàn thành!")

def check_labels_status():
    """
    Kiểm tra trạng thái labeling.
    """
    images = os.listdir(IMAGES_DIR)
    
    labeled = 0
    unlabeled = 0
    empty_labels = 0
    
    for img_file in images:
        if not img_file.endswith(('.jpg', '.png', '.jpeg')):
            continue
        
        label_file = img_file.rsplit('.', 1)[0] + '.txt'
        label_path = os.path.join(LABELS_DIR, label_file)
        
        if not os.path.exists(label_path):
            unlabeled += 1
        else:
            with open(label_path, 'r') as f:
                content = f.read().strip()
                if content:
                    labeled += 1
                else:
                    empty_labels += 1
    
    total = labeled + unlabeled + empty_labels
    print(f"\n📊 Trạng thái labeling:")
    print(f"  ✅ Đã label: {labeled}/{total}")
    print(f"  ⚠️  Trống: {empty_labels}/{total}")
    print(f"  ❌ Chưa tạo label: {unlabeled}/{total}")
    print(f"\n  Hoàn thành: {labeled*100//total if total > 0 else 0}%")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            check_labels_status()
        elif sys.argv[1] == "--rename":
            prefix = sys.argv[2] if len(sys.argv) > 2 else "PLATE"
            batch_rename_labels(prefix)
    else:
        label_images_interactive()
