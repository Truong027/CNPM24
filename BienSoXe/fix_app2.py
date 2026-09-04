import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and remove lines with old EasyOCR code
# We want to keep only the CRNN code and remove everything after "return OCR_READER_CACHE" up to the next function
output = []
skip = False
for i, line in enumerate(lines):
    # Check if this is the old with OCR_READER_LOCK block with easyocr
    if 'easyocr.Reader' in line or ('Shared EasyOCR' in line):
        # Skip this line and keep skipping until we find the next function
        skip = True
        continue
    
    # If we hit a new function definition, stop skipping
    if line.startswith('def ') and skip:
        skip = False
    
    # If not in skip mode, add the line
    if not skip:
        output.append(line)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print('✅ Fixed - removed old EasyOCR code')
