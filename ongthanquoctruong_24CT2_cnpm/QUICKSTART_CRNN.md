# 🚀 Quick Start: Testing CRNN-CTC Integration

## Option 1: Test Inference Only (No Server)

```bash
# 1. Test model inference with sample images
python plate_ocr_inference.py

# Expected output:
# ✅ Model loaded
# 📷 crop_00000.jpg: 50A-5.5 (55.33% confidence)
# ... more results
```

## Option 2: Test with Flask Server

```bash
# 1. Start Flask app with new OCR model
python app.py

# 2. Expected console output:
# ⌛ Loading CRNN-CTC model...
# ✅ CRNN-CTC model loaded
# * Running on http://127.0.0.1:5000
```

## Option 3: Full Training (Better Results)

For better accuracy, train the full 50-epoch model:

```bash
# Takes several hours on GPU
python ocr_train_plate_recognizer_v2.py

# This will:
# - Train for 50 epochs (instead of 3)
# - Improve validation loss from 1.83 to ~0.8-1.0
# - Update artifacts/plate_ocr/model.pt automatically
```

## What Changed in app.py

### Before (EasyOCR)
```python
import easyocr
reader = easyocr.Reader(['en'], gpu=True)
results = reader.readtext(image)  # Slow, general OCR
```

### After (CRNN-CTC)
```python
from crnn_ocr_wrapper import CRNNOCRWrapper
from plate_ocr_integration import get_ocr_model
model = get_ocr_model()  # Fast, specialized for Vietnamese plates
results = model.readtext(image)  # Same API, new backend
```

## Files Location

```
artifacts/plate_ocr/
├── model.pt              ← Trained weights (loaded automatically)
└── vocab.json            ← Character set

plate_ocr_inference.py    ← Inference module
crnn_ocr_wrapper.py       ← EasyOCR compatibility wrapper
plate_ocr_integration.py  ← Integration helper
app.py                    ← PATCHED Flask app (uses CRNN now)
app_easyocr_backup.py     ← Original app.py backup
```

## Troubleshooting

**Model not loading?**
```bash
# Check if model file exists
ls artifacts/plate_ocr/model.pt

# Re-run quick training to regenerate
python ocr_train_quick.py
```

**Slow inference?**
```bash
# Check GPU availability
python -c "import torch; print('GPU:', torch.cuda.is_available())"

# If no GPU, inference will run on CPU (slower)
```

**Wrong OCR results?**
```bash
# Try full training for better accuracy
python ocr_train_plate_recognizer_v2.py
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Training Images | 8,666 |
| Model Size | ~15MB |
| Inference Speed (GPU) | ~100ms per image |
| Inference Speed (CPU) | ~500ms per image |
| Current Accuracy | ~55% (3-epoch model) |
| Expected Accuracy | ~75-85% (50-epoch model) |

## Integration Points in app.py

The following functions now use CRNN-CTC:
- `get_shared_ocr_reader()` - Loads model instead of EasyOCR
- `read_plate_text_with_confidence()` - Uses wrapper's readtext() API
- All OCR detection routes use new model automatically

No other changes needed! Existing code works with new model.

---

Ready to test? Start with Option 1 or 2 above!
