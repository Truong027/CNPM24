"""
Simplified OCR reader wrapper for CRNN-CTC model.
Drop-in replacement for app.py functions.
"""

import cv2
import numpy as np
from plate_ocr_inference import PlateOCRInference

class CRNNOCRWrapper:
    """
    Wrapper to make CRNN-CTC model API compatible with EasyOCR-style code.
    """
    def __init__(self, ocr_model: PlateOCRInference):
        self.model = ocr_model
    
    def readtext(self, img, **kwargs):
        """
        Mimic EasyOCR readtext() API.
        Returns: list of [bbox, text, confidence] for compatibility
        """
        if img is None or img.size == 0:
            return []
        
        try:
            result = self.model.recognize(img)
            text = result['text']
            confidence = result['confidence'] / 100.0  # Convert to 0-1
            
            # Create fake bounding box (not used in code anyway)
            h, w = img.shape[:2]
            bbox = [[[0, 0], [w, 0], [w, h], [0, h]]]
            
            # Return in EasyOCR format: [bbox, text, confidence]
            return [bbox + [text, confidence]]
        except Exception as e:
            print(f"❌ CRNN OCR error: {e}")
            return []


def read_plate_text_with_confidence_crnn(plate_crop, ocr_wrapper):
    """
    Simplified plate OCR using CRNN-CTC model.
    Wrapper around original EasyOCR version.
    """
    if plate_crop is None or plate_crop.size == 0:
        return "", "", 0.0
    
    try:
        # Try normal
        result1 = ocr_wrapper.readtext(plate_crop)
        if result1:
            text = result1[0][1].strip()
            conf = result1[0][2]
            raw_text = text
            
            # Basic validation
            if len(text) >= 8:  # Valid VN plate format
                return text, raw_text, conf * 100
        
        # Try inverted
        inverted = cv2.bitwise_not(plate_crop)
        result2 = ocr_wrapper.readtext(inverted)
        if result2:
            text = result2[0][1].strip()
            conf = result2[0][2]
            raw_text = text
            if len(text) >= 8:
                return text, raw_text, conf * 100
        
        return "", "", 0.0
    
    except Exception as e:
        print(f"❌ Error reading plate: {e}")
        return "", "", 0.0
