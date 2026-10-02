"""
Script tổ chức dataset từ archive sang format training.
Lấy ảnh từ archive/cropped/ và archive/generated/
Đọc CSV labels và tạo text files.
"""

import os
import csv
import shutil
from pathlib import Path

# ===== PATHS =====
ARCHIVE_DIR = "archive"
CROPPED_DIR = os.path.join(ARCHIVE_DIR, "cropped")
GENERATED_DIR = os.path.join(ARCHIVE_DIR, "generated")
LABELS_DIR = os.path.join(ARCHIVE_DIR, "labels")

OUTPUT_DIR = "data/plate_ocr"
OUTPUT_IMAGES = os.path.join(OUTPUT_DIR, "images")
OUTPUT_LABELS = os.path.join(OUTPUT_DIR, "labels")

# Tạo thư mục đích
os.makedirs(OUTPUT_IMAGES, exist_ok=True)
os.makedirs(OUTPUT_LABELS, exist_ok=True)

def normalize_plate_label(label_text):
    """
    Normalize label từ CSV (e.g., "30F 11292") 
    thành format biển số Việt Nam (e.g., "30F-112.92")
    
    Format biển số VN: XXY-NNN.NN
    - XX: Mã tỉnh/thành (2 chữ số)
    - Y: Ký tự (A-Z)
    - NNN.NN: Số hiệu (5 chữ số, dấu chấm ở giữa)
    """
    label_text = label_text.strip().upper()
    
    # Xóa spaces và ký tự không cần
    label_text = label_text.replace(" ", "")
    
    # Pattern: XXY-NNNNN hoặc XYNNNNN
    # Kiểm tra nếu có ít nhất 7 ký tự
    if len(label_text) < 7:
        return None
    
    # Lấy 2 chữ số đầu (tỉnh)
    tinh = label_text[:2]
    if not tinh.isdigit():
        return None
    
    # Lấy ký tự thứ 3
    series = label_text[2]
    if not series.isalpha():
        return None
    
    # Lấy 5 chữ số còn lại
    so = label_text[3:8]
    if not so.isdigit():
        return None
    
    # Format: XX-Y-NNN.NN
    return f"{tinh}{series}-{so[:3]}.{so[3:]}"

def process_csv_and_copy(csv_path, image_source_dir, output_prefix):
    """
    Đọc CSV, copy ảnh, tạo label files.
    """
    if not os.path.exists(csv_path):
        print(f"⚠️  File không tồn tại: {csv_path}")
        return 0
    
    if not os.path.exists(image_source_dir):
        print(f"⚠️  Thư mục không tồn tại: {image_source_dir}")
        return 0
    
    print(f"\n📥 Xử lý: {csv_path}")
    print(f"   Nguồn ảnh: {image_source_dir}")
    
    count = 0
    skipped = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or 'Name' not in row or 'Label' not in row:
                continue
            
            img_name = row['Name'].strip()
            label_text = row['Label'].strip()
            
            # Kiểm tra file ảnh có tồn tại
            src_img = os.path.join(image_source_dir, img_name)
            if not os.path.exists(src_img):
                skipped += 1
                continue
            
            # Normalize label
            normalized = normalize_plate_label(label_text)
            if not normalized:
                skipped += 1
                continue
            
            # Tạo tên output (duy nhất)
            output_id = f"{output_prefix}_{count:05d}"
            output_img_name = f"{output_id}.jpg"
            output_label_name = f"{output_id}.txt"
            
            # Copy ảnh
            dst_img = os.path.join(OUTPUT_IMAGES, output_img_name)
            shutil.copy2(src_img, dst_img)
            
            # Lưu label
            dst_label = os.path.join(OUTPUT_LABELS, output_label_name)
            with open(dst_label, 'w', encoding='utf-8') as lf:
                lf.write(normalized)
            
            count += 1
            if count % 50 == 0:
                print(f"   ✅ {count} ảnh...")
    
    print(f"   ✅ Thành công: {count}")
    print(f"   ⚠️  Bỏ qua: {skipped}")
    
    return count

# ===== MAIN =====
print("🚀 Tổ chức dataset cho OCR training...\n")

total = 0

# Process cropped images
csv_crop = os.path.join(LABELS_DIR, "crop_labels.csv")
total += process_csv_and_copy(csv_crop, CROPPED_DIR, "crop")

# Process generated images
csv_gen = os.path.join(LABELS_DIR, "gen_labels.csv")
total += process_csv_and_copy(csv_gen, GENERATED_DIR, "type1")

print(f"\n" + "="*50)
print(f"📊 TỔNG KẾT:")
print(f"   ✅ Tổng ảnh: {total}")
print(f"   📁 Lưu tại: {OUTPUT_DIR}/")
print(f"\n💡 Bước tiếp theo: python ocr_train_plate_recognizer.py")
print("="*50)
