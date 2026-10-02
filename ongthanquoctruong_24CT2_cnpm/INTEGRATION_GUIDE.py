"""
Integration guide: Replace EasyOCR with trained CRNN-CTC model in app.py

This script shows how to modify app.py to use the new OCR model.
"""

# === CHANGES TO MAKE IN app.py ===

CHANGES = """
1. **Replace imports** (top of app.py):

   BEFORE:
   --------
   import easyocr
   
   AFTER:
   ------
   from plate_ocr_inference import PlateOCRInference


2. **Replace get_shared_ocr_reader() function**:

   BEFORE:
   -------
   def get_shared_ocr_reader():
       global OCR_READER_CACHE
       if OCR_READER_CACHE is not None:
           return OCR_READER_CACHE

       with OCR_READER_LOCK:
           if OCR_READER_CACHE is None:
               print("⌛ Loading shared EasyOCR reader...", flush=True)
               OCR_READER_CACHE = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
               print("✅ Shared EasyOCR reader ready.", flush=True)
       return OCR_READER_CACHE

   AFTER:
   ------
   def get_shared_ocr_reader():
       global OCR_READER_CACHE
       if OCR_READER_CACHE is not None:
           return OCR_READER_CACHE

       with OCR_READER_LOCK:
           if OCR_READER_CACHE is None:
               print("⌛ Loading trained CRNN-CTC model...", flush=True)
               device = 'cuda' if torch.cuda.is_available() else 'cpu'
               OCR_READER_CACHE = PlateOCRInference(
                   model_path="artifacts/plate_ocr/model.pt",
                   vocab_path="artifacts/plate_ocr/vocab.json",
                   device=device
               )
               print("✅ CRNN-CTC model ready.", flush=True)
       return OCR_READER_CACHE


3. **Replace read_plate_text_with_confidence() function**:

   BEFORE:
   -------
   def read_plate_text_with_confidence(reader, plate_crop):
       try:
           results = reader.readtext(plate_crop)
           if results:
               text_raw = ''.join([r[1] for r in results])
               conf_raw = np.mean([r[2] for r in results]) if results else 0
               text = normalize_plate_text(text_raw)
               return text, conf_raw
       except Exception as e:
           print(f"❌ EasyOCR error: {e}")
       return "", 0

   AFTER:
   ------
   def read_plate_text_with_confidence(ocr_model, plate_crop):
       try:
           result = ocr_model.recognize(plate_crop)
           text = result['text']
           confidence = result['confidence']
           
           # Normalize if needed
           text = normalize_plate_text(text)
           
           return text, confidence
       except Exception as e:
           print(f"❌ OCR error: {e}")
       return "", 0


4. **Update all calls** to the OCR functions:

   Look for lines using `get_shared_ocr_reader()` and 
   update function signature from `readtext()` to the new `recognize()` method.

   Example change:
   BEFORE: reader = get_shared_ocr_reader(); text, conf = read_plate_text_with_confidence(reader, crop)
   AFTER: ocr_model = get_shared_ocr_reader(); text, conf = read_plate_text_with_confidence(ocr_model, crop)
"""

print(CHANGES)

# ===== BACKUP AND AUTO-PATCH (optional) =====

def apply_changes_to_app():
    \"\"\"Auto-patch app.py with new OCR model (requires backup).\"\"\"
    import shutil
    
    app_path = "app.py"
    backup_path = "app.py.backup"
    
    # Backup
    if os.path.exists(app_path):
        shutil.copy2(app_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
    
    # Read
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace imports
    content = content.replace(
        "import easyocr",
        "from plate_ocr_inference import PlateOCRInference"
    )
    
    # Save
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ app.py updated!")
    print("⚠️  Manual changes needed: see CHANGES above for function updates")

if __name__ == "__main__":
    print(__doc__)
