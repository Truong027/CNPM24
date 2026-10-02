#!/usr/bin/env python3
import sys

# Read original
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Simple find and replace
# 1. Comment out easyocr
content = content.replace(
    'import easyocr\n',
    '# import easyocr  # Replaced with CRNN model\n'
)

# 2. Add CRNN imports after cv2 import
content = content.replace(
    'import cv2\n# import easyocr',
    '''import cv2
# import easyocr  # Replaced with CRNN model
from plate_ocr_integration import get_ocr_model, read_plate_ocr_crnn
from crnn_ocr_wrapper import CRNNOCRWrapper'''
)

# 3. Replace the full get_shared_ocr_reader function using regex
import re

pattern = r'def get_shared_ocr_reader\(\):.*?print\(".*?Shared EasyOCR reader.*?\n    return OCR_READER_CACHE'

replacement = '''def get_shared_ocr_reader():
    """Get CRNN-CTC model (replaces EasyOCR)."""
    global OCR_READER_CACHE
    if OCR_READER_CACHE is not None:
        return OCR_READER_CACHE

    with OCR_READER_LOCK:
        if OCR_READER_CACHE is None:
            print("Loading CRNN-CTC model...", flush=True)
            model = get_ocr_model()
            if model:
                OCR_READER_CACHE = CRNNOCRWrapper(model)
                print("CRNN-CTC model loaded", flush=True)
            else:
                print("Failed to load CRNN-CTC model", flush=True)
    return OCR_READER_CACHE'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ app.py fixed')
