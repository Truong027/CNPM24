"""
Hàm mới để integrate OCR model vào app.py
Thay thế cho EasyOCR
"""

import os
import torch
from plate_ocr_inference import PlateOCRInference
from threading import Lock

# ===== CACHE & LOCKS =====
OCR_MODEL_CACHE = None
OCR_MODEL_LOCK = Lock()

def get_ocr_model():
    """Load trained CRNN-CTC model (thay cho EasyOCR)."""
    global OCR_MODEL_CACHE
    
    if OCR_MODEL_CACHE is not None:
        return OCR_MODEL_CACHE
    
    with OCR_MODEL_LOCK:
        if OCR_MODEL_CACHE is None:
            print("⌛ Loading trained CRNN-CTC OCR model...", flush=True)
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            try:
                OCR_MODEL_CACHE = PlateOCRInference(
                    model_path="artifacts/plate_ocr/model.pt",
                    vocab_path="artifacts/plate_ocr/vocab.json",
                    device=device
                )
                print("✅ CRNN-CTC OCR model loaded", flush=True)
            except Exception as e:
                print(f"❌ Failed to load OCR model: {e}", flush=True)
                return None
    
    return OCR_MODEL_CACHE

def read_plate_ocr_crnn(ocr_model, plate_crop):
    """
    Đọc biển số từ plate crop bằng CRNN-CTC model.
    
    Args:
        ocr_model: PlateOCRInference instance
        plate_crop: numpy array (BGR format)
    
    Returns:
        tuple: (text, confidence)
    """
    if ocr_model is None:
        return "", 0.0
    
    try:
        result = ocr_model.recognize(plate_crop)
        text = result['text']
        confidence = result['confidence']
        
        return text, confidence
    
    except Exception as e:
        print(f"❌ OCR error: {e}", flush=True)
        return "", 0.0

# === EXAMPLE: How to integrate in app.py ===
INTEGRATION_CODE = """
# === TRONG app.py ===

# 1. THAY ĐỔI IMPORT (dòng đầu tiên):
# XÓA: import easyocr
# THÊM:
from plate_ocr_integration import get_ocr_model, read_plate_ocr_crnn

# 2. THAY ĐỔI get_shared_ocr_reader():
# XÓA hàm get_shared_ocr_reader() cũ
# THÊM:
def get_shared_ocr_reader():
    return get_ocr_model()

# 3. THAY ĐỔI read_plate_text_with_confidence():
# Simplify thành:
def read_plate_text_with_confidence(plate_crop, ocr_model):
    if plate_crop is None or plate_crop.size == 0:
        return "", "", 0.0
    
    text, confidence = read_plate_ocr_crnn(ocr_model, plate_crop)
    
    # Normalize
    text = normalize_plate_text(text)
    
    return text, text, confidence

# 4. CẬP NHẬT CÁC LỜI GỌI HÀM:
# Thay vì:
#   reader = get_shared_ocr_reader()
#   text, raw, conf = read_plate_text_with_confidence(crop, reader)
# 
# Thành:
#   ocr_model = get_shared_ocr_reader()
#   text, raw, conf = read_plate_text_with_confidence(crop, ocr_model)
"""

