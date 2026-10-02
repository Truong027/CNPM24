"""Train plate OCR recognizer for Vietnamese car plates (no diacritics).

This repo currently uses EasyOCR. This script builds a lightweight CRNN (CNN+BiLSTM)
trained with CTC loss to recognize plate strings.

IMPORTANT:
- You must create a dataset first.
- This script assumes a label format like: 51G-123.45 or 43A-272.08
- It supports two-part format with '-' and '.', but the model learns a character set.

Dataset format expected (after running dataset builder):
    data/plate_ocr/{images,label}
where label is a .txt per image with the ground-truth string.

Because we don't have enough ground-truth OCR data in this repo automatically,
training requires you to create/copy labels for images.

Usage:
  python ocr_train_plate_recognizer.py

It will generate:
  artifacts/plate_ocr/model.pt
  artifacts/plate_ocr/vocab.json
"""

import os
import json
import math
import random
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

try:
    import cv2
except Exception:
    cv2 = None

# -------------------- Config --------------------

SEED = 42
random.seed(SEED)

DATA_ROOT = os.getenv("PLATE_OCR_DATA_ROOT", "data/plate_ocr")
# Ví dụ dataset:
#   data/plate_ocr/images/*.jpg
#   data/plate_ocr/labels/*.txt

IMAGES_DIR = os.path.join(DATA_ROOT, "images")
LABELS_DIR = os.path.join(DATA_ROOT, "labels")

ART_DIR = os.getenv("PLATE_OCR_ART_DIR", "artifacts/plate_ocr")
MODEL_OUT = os.path.join(ART_DIR, "model.pt")
VOCAB_OUT = os.path.join(ART_DIR, "vocab.json")

# training params (tune later)
BATCH_SIZE = int(os.getenv("PLATE_OCR_BATCH", "16"))
EPOCHS = int(os.getenv("PLATE_OCR_EPOCHS", "30"))
LR = float(os.getenv("PLATE_OCR_LR", "1e-3"))
NUM_WORKERS = int(os.getenv("PLATE_OCR_WORKERS", "2"))

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# -------------------- Vocab --------------------
# Allowed characters for VN plates (upper, no diacritics)
# We include digits, A-Z, '-', '.'

CHARSET = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-.")
# CTC blank index will be len(CHARSET)

BLANK_TOKEN = "[blank]"


def build_vocab():
    stoi = {ch: i for i, ch in enumerate(CHARSET)}
    itos = {i: ch for ch, i in stoi.items()}
    blank_index = len(CHARSET)
    return stoi, itos, blank_index


# -------------------- Model --------------------

class CRNN(nn.Module):
    def __init__(self, num_classes: int, hidden_size: int = 256):
        super().__init__()
        # CNN encoder (lightweight)
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            # Keep width resolution
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
        # x: (B,1,H,W)
        feat = self.cnn(x)  # (B,C,H',W')
        B, C, H, W = feat.shape
        # collapse H'
        feat = feat.permute(0, 3, 1, 2).contiguous()  # (B,W',C,H')
        feat = feat.view(B, W, C * H)
        # project to 256 using a linear-like implicit approach by reshaping not good;
        # so instead we average over H'
        # Let's do: average over H'
        feat = feat.view(B, W, C, H).mean(-1)  # (B,W',C)
        feat = feat.permute(1, 0, 2).contiguous()  # (T,B,C)
        out, _ = self.rnn(feat)
        logits = self.fc(out)  # (T,B,num_classes)
        return logits


# -------------------- Dataset --------------------

class PlateOcrDataset(Dataset):
    def __init__(self, images_dir, labels_dir, img_size=(48, 160)):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.img_size = img_size  # (H,W)

        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        files = []
        for fn in os.listdir(images_dir):
            _, ext = os.path.splitext(fn)
            if ext.lower() in exts:
                files.append(fn)
        files.sort()
        self.files = files

    def __len__(self):
        return len(self.files)

    def _load_gray(self, path):
        if cv2 is None:
            raise RuntimeError("opencv-python not available")
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise RuntimeError(f"Cannot read image: {path}")
        img = cv2.resize(img, (self.img_size[1], self.img_size[0]), interpolation=cv2.INTER_CUBIC)
        # normalize to [0,1]
        img = img.astype("float32") / 255.0
        # invert if needed (keep as-is; can be improved)
        return img

    def __getitem__(self, idx):
        fn = self.files[idx]
        img_path = os.path.join(self.images_dir, fn)
        base, _ = os.path.splitext(fn)
        label_path = os.path.join(self.labels_dir, base + ".txt")

        with open(label_path, "r", encoding="utf-8") as f:
            text = f.read().strip().upper()

        img = self._load_gray(img_path)  # (H,W)
        # (1,H,W)
        x = torch.from_numpy(img).unsqueeze(0)
        return x, text


def encode_text(text: str, stoi: dict):
    # remove unsupported chars
    out = []
    for ch in text:
        if ch in stoi:
            out.append(stoi[ch])
        else:
            # skip unknown
            pass
    return out


def pad_collate(batch, stoi):
    """CTC collate: images are fixed-size; targets are variable length."""
    xs = []
    targets = []
    input_lengths = []
    target_lengths = []

    # fixed image H,W; but time steps depend on CNN/RNN reduction.
    # We'll approximate T by W after pooling; compute from model is better, but ok for training.

    for x, text in batch:
        xs.append(x)
        enc = encode_text(text, stoi)
        targets.extend(enc)
        target_lengths.append(len(enc))

    x_tensor = torch.stack(xs, dim=0)
    targets_tensor = torch.tensor(targets, dtype=torch.long)

    # For CTC in this CRNN, time steps roughly equals W after CNN pools.
    # Since we used fixed (H=48,W=160), we can compute once.
    # Empirically, after pools: W reduces by /2 /2 then /2? We keep width with (2,1) pool.
    # Let's approximate: W=160 -> after pool2x2 twice => 40.
    # We'll derive: MaxPool2d(2,2) twice reduces W by 4 => 40; then MaxPool2d((2,1)) keeps W.
    # So T=40.
    T = 40
    input_lengths = torch.full((x_tensor.size(0),), T, dtype=torch.long)

    return x_tensor, targets_tensor, input_lengths, torch.tensor(target_lengths, dtype=torch.long)


# -------------------- Train / Main --------------------

@dataclass
class TrainConfig:
    batch_size: int = BATCH_SIZE
    epochs: int = EPOCHS
    lr: float = LR


def main():
    os.makedirs(ART_DIR, exist_ok=True)
    stoi, itos, blank_index = build_vocab()

    # sanity check dataset
    if not os.path.isdir(IMAGES_DIR) or not os.path.isdir(LABELS_DIR):
        raise RuntimeError(f"Dataset not found. Expected: {DATA_ROOT}/images and {DATA_ROOT}/labels")

    dataset = PlateOcrDataset(IMAGES_DIR, LABELS_DIR)
    if len(dataset) < 10:
        raise RuntimeError(f"Dataset too small (n={len(dataset)}). Need more labeled plate crops for training OCR.")

    # split
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
        num_workers=NUM_WORKERS,
        collate_fn=lambda b: pad_collate(b, stoi),
        drop_last=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=max(1, BATCH_SIZE // 2),
        shuffle=False,
        num_workers=NUM_WORKERS,
        collate_fn=lambda b: pad_collate(b, stoi),
        drop_last=False,
    )

    num_classes = len(CHARSET) + 1  # + blank

    model = CRNN(num_classes=num_classes, hidden_size=256).to(DEVICE)

    criterion = nn.CTCLoss(blank=blank_index, zero_infinity=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)

    vocab_payload = {"charset": CHARSET, "blank_index": blank_index}
    with open(VOCAB_OUT, "w", encoding="utf-8") as f:
        json.dump(vocab_payload, f, ensure_ascii=False, indent=2)

    best_val = 1e18
    global_step = 0

    for epoch in range(1, EPOCHS + 1):
        model.train()
        train_loss_sum = 0.0
        n_batches = 0

        for x, targets, input_lengths, target_lengths in train_loader:
            x = x.to(DEVICE)
            targets = targets.to(DEVICE)
            input_lengths = input_lengths.to(DEVICE)
            target_lengths = target_lengths.to(DEVICE)

            logits = model(x)  # (T,B,C)
            log_probs = F.log_softmax(logits, dim=-1)

            loss = criterion(log_probs, targets, input_lengths, target_lengths)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

            train_loss_sum += float(loss.item())
            n_batches += 1
            global_step += 1

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

        print(f"[Epoch {epoch}/{EPOCHS}] train_loss={train_loss:.4f} val_loss={val_loss:.4f}", flush=True)

        if val_loss < best_val:
            best_val = val_loss
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "char_set": CHARSET,
                    "blank_index": blank_index,
                    "arch": "CRNN_CTC",
                    "img_size": dataset.img_size,
                },
                MODEL_OUT,
            )
            print(f"  -> saved best model to {MODEL_OUT} (val_loss={val_loss:.4f})")

    print("Training completed.")


if __name__ == "__main__":
    main()

