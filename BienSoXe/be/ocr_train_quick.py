"""
Quick OCR training - ít epochs để test nhanh.
Sau khi verify hoạt động, có thể chạy full version.
"""

import os
import json
import random
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np

try:
    import cv2
except Exception:
    cv2 = None

# ===== CONFIG - QUICK VERSION =====
SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)
np.random.seed(SEED)

DATA_ROOT = "data/plate_ocr"
IMAGES_DIR = os.path.join(DATA_ROOT, "images")
LABELS_DIR = os.path.join(DATA_ROOT, "labels")

BATCH_SIZE = 64  # Larger batch
EPOCHS = 3  # Quick test - only 3 epochs
LR = 1e-3
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Output paths
OUTPUT_DIR = "artifacts/plate_ocr"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_OUT = os.path.join(OUTPUT_DIR, "model.pt")
VOCAB_OUT = os.path.join(OUTPUT_DIR, "vocab.json")

CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-."
blank_index = len(CHARSET)

# ===== DATASET =====
class PlateOcrDataset(Dataset):
    def __init__(self, images_dir, labels_dir, img_size=(32, 128)):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.img_size = img_size  # (H, W)

        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        self.files = []
        for fn in os.listdir(images_dir):
            _, ext = os.path.splitext(fn)
            if ext.lower() in exts:
                self.files.append(fn)

        print(f"📊 Dataset: {len(self.files)} ảnh")

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        img_file = self.files[idx]
        base_name, _ = os.path.splitext(img_file)

        img_path = os.path.join(self.images_dir, img_file)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            img = np.ones((self.img_size[0], self.img_size[1]), dtype=np.uint8) * 255

        h, w = img.shape
        target_h, target_w = self.img_size
        scale = min(target_h / h, target_w / w)
        new_h, new_w = int(h * scale), int(w * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        pad_img = np.ones((target_h, target_w), dtype=np.uint8) * 255
        y_off = (target_h - new_h) // 2
        x_off = (target_w - new_w) // 2
        pad_img[y_off : y_off + new_h, x_off : x_off + new_w] = img

        img_tensor = torch.from_numpy(pad_img).unsqueeze(0).float() / 255.0

        label_path = os.path.join(self.labels_dir, base_name + ".txt")
        if os.path.exists(label_path):
            with open(label_path, 'r', encoding='utf-8') as f:
                text = f.read().strip().upper()
        else:
            text = ""

        char_to_idx = {c: i for i, c in enumerate(CHARSET)}
        indices = []
        for c in text:
            if c in char_to_idx:
                indices.append(char_to_idx[c])

        return img_tensor, indices

def collate_fn_wrapper(batch):
    images = []
    text_indices = []
    target_lengths = []

    for img, indices in batch:
        images.append(img)
        text_indices.extend(indices)
        target_lengths.append(len(indices))

    images = torch.stack(images, dim=0)
    B, C, H, W = images.shape
    input_lengths = torch.full((B,), W // 4, dtype=torch.long)

    targets = torch.tensor(text_indices, dtype=torch.long)
    target_lengths = torch.tensor(target_lengths, dtype=torch.long)

    return images, targets, input_lengths, target_lengths

# ===== MODEL =====
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

def main():
    print("🚀 Quick OCR training (3 epochs for testing)...\n")
    print(f"💾 Device: {DEVICE}")

    if not os.path.exists(IMAGES_DIR) or not os.path.exists(LABELS_DIR):
        print(f"❌ Dataset not found at {DATA_ROOT}")
        return

    dataset = PlateOcrDataset(IMAGES_DIR, LABELS_DIR)
    if len(dataset) == 0:
        print("❌ No images found!")
        return

    idxs = list(range(len(dataset)))
    random.shuffle(idxs)
    split = int(0.9 * len(idxs))
    train_idx = idxs[:split]
    val_idx = idxs[split:]

    train_ds = torch.utils.data.Subset(dataset, train_idx)
    val_ds = torch.utils.data.Subset(dataset, val_idx)

    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        collate_fn=collate_fn_wrapper,
        drop_last=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=max(1, BATCH_SIZE // 2),
        shuffle=False,
        num_workers=0,
        collate_fn=collate_fn_wrapper,
        drop_last=False,
    )

    num_classes = len(CHARSET) + 1

    model = CRNN(num_classes=num_classes, hidden_size=256).to(DEVICE)
    print(f"📦 Model: CRNN-CTC, {sum(p.numel() for p in model.parameters())} params\n")

    criterion = nn.CTCLoss(blank=blank_index, zero_infinity=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)

    vocab_payload = {"charset": CHARSET, "blank_index": blank_index}
    with open(VOCAB_OUT, "w", encoding="utf-8") as f:
        json.dump(vocab_payload, f, ensure_ascii=False, indent=2)
    print(f"✅ Vocab saved: {VOCAB_OUT}\n")

    best_val = 1e18

    print("🔥 Training...\n")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        train_loss_sum = 0.0
        n_batches = 0

        for x, targets, input_lengths, target_lengths in train_loader:
            x = x.to(DEVICE)
            targets = targets.to(DEVICE)
            input_lengths = input_lengths.to(DEVICE)
            target_lengths = target_lengths.to(DEVICE)

            logits = model(x)
            log_probs = F.log_softmax(logits, dim=-1)

            loss = criterion(log_probs, targets, input_lengths, target_lengths)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

            train_loss_sum += float(loss.item())
            n_batches += 1

        train_loss = train_loss_sum / max(1, n_batches)

        model.eval()
        val_loss_sum = 0.0
        val_batches = 0
        with torch.no_grad():
            for x, targets, input_lengths, target_lengths in val_loader:
                x = x.to(DEVICE)
                targets = targets.to(DEVICE)
                input_lengths = input_lengths.to(DEVICE)
                target_lengths = target_lengths.to(DEVICE)

                logits = model(x)
                log_probs = F.log_softmax(logits, dim=-1)
                loss = criterion(log_probs, targets, input_lengths, target_lengths)
                val_loss_sum += float(loss.item())
                val_batches += 1

        val_loss = val_loss_sum / max(1, val_batches)

        print(f"[Epoch {epoch}/{EPOCHS}] train_loss={train_loss:.4f} val_loss={val_loss:.4f}")

        if val_loss < best_val:
            best_val = val_loss
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "char_set": CHARSET,
                    "blank_index": blank_index,
                    "arch": "CRNN_CTC",
                    "img_size": (32, 128),
                },
                MODEL_OUT,
            )
            print(f"  ✅ Model saved (val_loss={val_loss:.4f})")

    print(f"\n✅ Training complete!")
    print(f"📦 Model: {MODEL_OUT}")
    print(f"📝 Next: python plate_ocr_inference.py to test")

if __name__ == "__main__":
    main()
