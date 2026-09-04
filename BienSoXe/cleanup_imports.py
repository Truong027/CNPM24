with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove duplicate imports and clean up
output = []
seen = set()

for line in lines:
    # Skip duplicate imports
    stripped = line.strip()
    if 'from plate_ocr' in stripped or 'from crnn_ocr' in stripped:
        if stripped in seen:
            continue
        seen.add(stripped)
    
    # Clean up line 4 comment artifact
    if 'CRNNOCRWrapper  # Replaced with CRNN-CTC model' in line:
        line = line.replace('  # Replaced with CRNN-CTC model', '')
    
    output.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print('✅ Imports cleaned')
