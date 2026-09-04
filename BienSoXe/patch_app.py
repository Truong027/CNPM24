#!/usr/bin/env python3
"""
Patch app.py to use CRNN-CTC model instead of EasyOCR.
Run this ONCE to update app.py permanently.
"""

import re

def patch_app_py():
    app_file = 'app.py'
    
    # Read current file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Replace import easyocr with comment
    content = re.sub(
        r'import easyocr',
        '# import easyocr  # Replaced with CRNN-CTC model',
        content
    )
    
    # 2. Add import for CRNN model (after existing imports, before app creation)
    if 'from plate_ocr_integration import' not in content:
        insert_pos = content.find('# Pillow 10 removed Image.ANTIALIAS')
        if insert_pos != -1:
            content = (
                content[:insert_pos] + 
                '# Import CRNN-CTC OCR model\nfrom crnn_ocr_wrapper import CRNNOCRWrapper, read_plate_text_with_confidence_crnn\nfrom plate_ocr_integration import get_ocr_model\n\n' +
                content[insert_pos:]
            )
    
    # 3. Replace get_shared_ocr_reader function
    old_func = r'''def get_shared_ocr_reader\(\):.*?return OCR_READER_CACHE'''
    new_func = '''def get_shared_ocr_reader():
    """Get CRNN-CTC model (replaces EasyOCR)."""
    global OCR_READER_CACHE
    if OCR_READER_CACHE is not None:
        return OCR_READER_CACHE
    
    with OCR_READER_LOCK:
        if OCR_READER_CACHE is None:
            print("⌛ Loading CRNN-CTC model...", flush=True)
            model = get_ocr_model()
            if model:
                OCR_READER_CACHE = CRNNOCRWrapper(model)
                print("✅ CRNN-CTC model loaded", flush=True)
    
    return OCR_READER_CACHE'''
    
    content = re.sub(old_func, new_func, content, flags=re.DOTALL)
    
    # Write back
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patched app.py successfully!")
    print("📝 Backup saved: app_easyocr_backup.py")

if __name__ == '__main__':
    patch_app_py()
