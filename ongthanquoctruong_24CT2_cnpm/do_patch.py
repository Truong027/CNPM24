import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the function
pattern = r'def get_shared_ocr_reader\(\):.*?return OCR_READER_CACHE'
replacement = '''def get_shared_ocr_reader():
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
            else:
                print("❌ Failed to load CRNN-CTC model", flush=True)
    return OCR_READER_CACHE'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Function replaced')
