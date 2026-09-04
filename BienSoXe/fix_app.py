import re

# Fix duplicate code in app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the duplicate old EasyOCR code
# Pattern: Find the duplicate "with OCR_READER_LOCK:" block after the first return
pattern = r'(    return OCR_READER_CACHE)\n\n    with OCR_READER_LOCK:.*?return OCR_READER_CACHE'

# Replace with just the return statement
replacement = r'\1'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed app.py - removed duplicate code")
