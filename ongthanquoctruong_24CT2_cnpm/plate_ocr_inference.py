"""
Inference module để sử dụng trained OCR model.
Thay thế cho EasyOCR trong app.py
"""

import os
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2
import numpy as np

# ===== MODEL ARCHITECTURE =====
class CRNN(nn.Module):
    def __init__(self, num_classes=37, hidden_size=256):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(1, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d((2, 2), (2, 2)),

            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d((2, 2), (2, 2)),

            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d((2, 1), (2, 1)),

            nn.Conv2d(256, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
        )

        self.rnn = nn.LSTM(
            input_size=256,
            hidden_size=hidden_size,
            num_layers=2,
            bidirectional=True,
            batch_first=False,
        )

        self.fc = nn.Linear(hidden_size * 2, num_classes)

    def forward(self, x):
        feat = self.cnn(x)
        B, C, H, W = feat.shape
        feat = feat.permute(0, 3, 1, 2).contiguous()
        feat = feat.view(B, W, C * H)
        feat = feat.view(B, W, C, H).mean(-1)
        feat = feat.permute(1, 0, 2).contiguous()
        out, _ = self.rnn(feat)
        logits = self.fc(out)
        return logits

# ===== LOADER & INFERENCE =====
class PlateOCRInference:
    def __init__(self, model_path="artifacts/plate_ocr/model.pt", 
                 vocab_path="artifacts/plate_ocr/vocab.json",
                 device='cuda'):
        self.device = device
        self.model_path = model_path
        self.vocab_path = vocab_path
        
        # Load vocab
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
        
        self.charset = vocab_data['charset']
        self.blank_index = vocab_data['blank_index']
        self.idx_to_char = {i: c for i, c in enumerate(self.charset)}
        self.char_to_idx = {c: i for i, c in enumerate(self.charset)}
        
        # Load model
        num_classes = len(self.charset) + 1
        self.model = CRNN(num_classes=num_classes, hidden_size=256).to(device)
        
        checkpoint = torch.load(model_path, map_location=device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        self.img_size = checkpoint.get('img_size', (32, 128))
        
        print(f"✅ Model loaded from: {model_path}")
        print(f"   Charset: {self.charset}")
        print(f"   Image size: {self.img_size}")

    def preprocess_image(self, image, target_size=None):
        """
        Preprocess image cho OCR.
        Hỗ trợ: numpy array hoặc file path
        """
        if target_size is None:
            target_size = self.img_size
        
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError(f"Cannot read image: {image}")
        else:
            # Assume numpy array (BGR or grayscale)
            if len(image.shape) == 3:
                img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                img = image
        
        # Resize
        h, w = img.shape
        target_h, target_w = target_size
        scale = min(target_h / h, target_w / w)
        new_h, new_w = int(h * scale), int(w * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Pad
        pad_img = np.ones((target_h, target_w), dtype=np.uint8) * 255
        y_off = (target_h - new_h) // 2
        x_off = (target_w - new_w) // 2
        pad_img[y_off : y_off + new_h, x_off : x_off + new_w] = img
        
        # Normalize
        img_tensor = torch.from_numpy(pad_img).unsqueeze(0).float() / 255.0
        
        return img_tensor

    def recognize(self, image, confidence_threshold=0.5):
        """
        Nhận diện plate text từ image crop.
        
        Args:
            image: numpy array (BGR) hoặc path string
            confidence_threshold: ngưỡng confidence tối thiểu
        
        Returns:
            dict: {
                'text': 'XXY-NNN.NN',
                'confidence': 0.95,
                'raw_output': '...'
            }
        """
        img_tensor = self.preprocess_image(image)
        img_tensor = img_tensor.unsqueeze(0).to(self.device)  # (1, 1, H, W)
        
        with torch.no_grad():
            logits = self.model(img_tensor)  # (T, B, C)
        
        # Decode using greedy approach
        log_probs = F.log_softmax(logits, dim=-1)  # (T, B, C)
        probs, indices = torch.max(log_probs, dim=-1)  # (T, B)
        
        # Convert indices to chars
        indices = indices[:, 0].cpu().numpy()  # (T,)
        
        # Remove consecutive duplicates (collapse)
        result = []
        prev_idx = -1
        for idx in indices:
            if idx != prev_idx and idx != self.blank_index:
                result.append(idx)
                prev_idx = idx
        
        # Convert to text
        text = ''.join([self.idx_to_char[idx] for idx in result])
        
        # Calculate confidence
        if len(result) > 0:
            result_probs = probs[indices != self.blank_index].cpu().numpy()
            confidence = np.mean(np.exp(result_probs))
        else:
            confidence = 0.0
        
        return {
            'text': text,
            'confidence': float(confidence),
            'raw_output': ''.join([self.idx_to_char[idx] if idx < len(self.idx_to_char) else '?' for idx in indices])
        }

    def recognize_batch(self, images, confidence_threshold=0.5):
        """Nhận diện batch images."""
        results = []
        for img in images:
            results.append(self.recognize(img, confidence_threshold))
        return results

# ===== Test function =====
def test_inference(model_path="artifacts/plate_ocr/model.pt",
                   test_image_dir="data/plate_ocr/images"):
    """Test model trên một số ảnh."""
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    print("\n🧪 Testing OCR Inference...\n")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    ocr = PlateOCRInference(model_path, device=device)
    
    # Test trên một số ảnh
    test_images = [f for f in os.listdir(test_image_dir) if f.endswith(('.jpg', '.png'))][:5]
    
    for img_name in test_images:
        img_path = os.path.join(test_image_dir, img_name)
        result = ocr.recognize(img_path)
        
        print(f"📷 {img_name}")
        print(f"   Text: {result['text']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print()

if __name__ == "__main__":
    test_inference()
