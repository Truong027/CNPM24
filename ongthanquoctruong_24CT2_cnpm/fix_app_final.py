import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace import easyocr
content = content.replace(
    'import easyocr',
    '# import easyocr  # Replaced with CRNN-CTC model'
)

# 2. Add CRNN imports after cv2 import
content = content.replace(
    'import cv2\n# import easyocr',
    '''import cv2
# import easyocr  # Replaced with CRNN-CTC model
import re

# Import CRNN model
from plate_ocr_integration import get_ocr_model, read_plate_ocr_crnn
from crnn_ocr_wrapper import CRNNOCRWrapper'''
)

# 3. Replace the get_shared_ocr_reader function completely
old_func = '''def get_shared_ocr_reader():
    """Láº¥y EasyOCR Reader dÃ¹ng chung cho cÃ¡c tÃ¡c vá»¥ request (nháº­n diá»‡n áº£nh)."""
    global OCR_READER_CACHE
    if OCR_READER_CACHE is not None:
        return OCR_READER_CACHE

    with OCR_READER_LOCK:
        if OCR_READER_CACHE is None:
            print("âŒ› [OCR] Äang khá»Ÿi táº¡o shared EasyOCR reader...", flush=True)
            # Cáº¢I TIáº¾N 1: Bá» 'vi', chá»‰ dÃ¹ng 'en' Ä'á»ƒ trÃ¡nh lá»—i áº£o giÃ¡c dáº¥u tiáº¿ng Viá»‡t
            OCR_READER_CACHE = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
            print("âœ… [OCR] Shared EasyOCR reader Ä'Ã£ sáºµn sÃ ng.", flush=True)
    return OCR_READER_CACHE'''

new_func = '''def get_shared_ocr_reader():
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

content = content.replace(old_func, new_func)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ app.py fixed correctly')
