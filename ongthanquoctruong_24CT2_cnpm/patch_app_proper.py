#!/usr/bin/env python3
"""Patch app.py to use CRNN model - surgical approach"""

# Read the original backup
with open('app_easyocr_backup.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Process line by line
output = []
skip_until_login = False
imports_added = False

for i, line in enumerate(lines):
    # Skip import easyocr, replace with comment
    if 'import easyocr' in line:
        output.append('# import easyocr  # Replaced with CRNN model\n')
        continue
    
    # Add imports after "import re"
    if 'import re' in line and not imports_added:
        output.append(line)
        output.append('\n# Import CRNN model\n')
        output.append('from plate_ocr_integration import get_ocr_model, read_plate_ocr_crnn\n')
        output.append('from crnn_ocr_wrapper import CRNNOCRWrapper\n')
        imports_added = True
        continue
    
    # Replace the entire get_shared_ocr_reader function
    if 'def get_shared_ocr_reader():' in line:
        # Write new function
        output.append(line)  # def get_shared_ocr_reader():
        output.append('    """Get CRNN-CTC model (replaces EasyOCR)."""\n')
        output.append('    global OCR_READER_CACHE\n')
        output.append('    if OCR_READER_CACHE is not None:\n')
        output.append('        return OCR_READER_CACHE\n')
        output.append('\n')
        output.append('    with OCR_READER_LOCK:\n')
        output.append('        if OCR_READER_CACHE is None:\n')
        output.append('            print("Loading CRNN-CTC model...", flush=True)\n')
        output.append('            model = get_ocr_model()\n')
        output.append('            if model:\n')
        output.append('                OCR_READER_CACHE = CRNNOCRWrapper(model)\n')
        output.append('                print("CRNN-CTC model loaded", flush=True)\n')
        output.append('            else:\n')
        output.append('                print("Failed to load CRNN-CTC model", flush=True)\n')
        output.append('    return OCR_READER_CACHE\n')
        
        # Skip old function lines until next "def"
        j = i + 1
        while j < len(lines):
            if lines[j].startswith('def '):
                break
            j += 1
        
        # Jump to the next function
        i = j - 1
        continue
    
    # Add everything else
    output.append(line)

# Write to app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print('✅ app.py patched correctly')
