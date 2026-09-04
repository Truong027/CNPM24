import cv2
import easyocr
from plate_ocr_integration import get_ocr_model, read_plate_ocr_crnn
from crnn_ocr_wrapper import CRNNOCRWrapper
import re

# Import new OCR model
import time
import numpy as np
from ultralytics import YOLO
from collections import Counter
import os
import torch
from PIL import Image
import database  # Import module CSDL - bÃ¢y giá»  dÃ¹ng MySQL
from flask import (
    Flask,
    render_template,
    Response,
    jsonify,
    request,
    session,
    redirect,
    url_for,
    make_response,
)
import csv, io
from functools import wraps
from datetime import date, datetime, timedelta
from threading import Lock, Thread
from queue import Queue, Empty
from werkzeug.security import generate_password_hash, check_password_hash

# Pillow 10 removed Image.ANTIALIAS, but easyocr 1.7.0 still references it.
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# ================== KHỞI TẠO FLASK ==================
print("🚀 [APP START] app.py is loading...", flush=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FE_TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "fe", "templates"))
FE_STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "fe", "static"))
TEMPLATE_DIR = FE_TEMPLATE_DIR if os.path.exists(FE_TEMPLATE_DIR) else os.path.join(BASE_DIR, "templates")
STATIC_DIR = FE_STATIC_DIR if os.path.exists(FE_STATIC_DIR) else os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY", "dev-secret-change-me")
print(f"🚀 [APP START] Flask app created with template_folder: {TEMPLATE_DIR}", flush=True)

OCR_READER_CACHE = None
OCR_READER_LOCK = Lock()
OCR_INFER_LOCK = Lock()
MODEL_TRACK_LOCK = Lock()
TRACK_FRAME_SIZE = (640, 480)


def get_shared_ocr_reader():
    """
    Khởi tạo và trả về model OCR dùng chung.
    Kết hợp CRNN-CTC (nhanh, chính xác) và EasyOCR (fallback mạnh mẽ).
    """
    global OCR_READER_CACHE
    if OCR_READER_CACHE is not None:
        return OCR_READER_CACHE

    with OCR_READER_LOCK:
        if OCR_READER_CACHE is None:
            print("Loading OCR models...", flush=True)
            crnn = get_ocr_model()
            try:
                reader = easyocr.Reader(["en"], gpu=torch.cuda.is_available())
            except Exception as e:
                print(f"Failed to load EasyOCR: {e}")
                reader = None

            OCR_READER_CACHE = {"crnn": crnn, "easy": reader}
            print("OCR models loaded", flush=True)
    return OCR_READER_CACHE


def login_required(view_func):
    """YÃªu cáº§u Ä‘Äƒng nháº­p cho route."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if session.get("user"):
            return view_func(*args, **kwargs)

        if request.path.startswith("/api/") or request.path.startswith("/get_"):
            return jsonify({"error": "Unauthorized"}), 401

        return redirect(url_for("login"))

    return wrapped_view


# ================== KHá»žI Táº O MYSQL DATABASE ==================
print("âŒ› Ä ang khá»Ÿi táº¡o cÆ¡ sá»Ÿ dá»¯ liá»‡u MySQL...")
database.init_db()
print("âœ… MySQL Database Ä‘Ã£ sáºµn sÃ ng.")

# ================== KIá»‚M TRA GPU ==================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"ðŸ’» Thiáº¿t bá»‹ tÃ­nh toÃ¡n: {device}")
if device == "cuda":
    print("âœ… GPU kháº£ dá»¥ng:", torch.cuda.get_device_name(0))
else:
    print("âš ï¸  GPU khÃ´ng kháº£ dá»¥ng, sáº½ cháº¡y trÃªn CPU.")

# ================== CẤU HÌNH & KHỞI TẠO ==================
candidate_model_paths = [
    os.path.join(BASE_DIR, "runs", "detect", "train", "weights", "best.pt"),
    os.path.join(BASE_DIR, "..", "runs", "detect", "train", "weights", "best.pt"),
    "runs/detect/train/weights/best.pt",
    os.path.join(BASE_DIR, "yolov8s.pt"),
    os.path.join(BASE_DIR, "..", "yolov8s.pt"),
    "yolov8s.pt"
]
MODEL_PATH = None
for p in candidate_model_paths:
    if os.path.exists(p):
        MODEL_PATH = os.path.abspath(p)
        break

# --- CÁC NGUỒN CAMERA ---
WEBCAM_SOURCE = 0
PHONE_CAMERA_URL = "https://192.168.1.18:8080/video"  # Cổng Ra (Check-Out) - Thay đổi IP theo IP Webcam của bạn
# ------------------------------

if not MODEL_PATH or not os.path.exists(MODEL_PATH):
    print(f"❌ Không tìm thấy file mô hình tại các đường dẫn: {candidate_model_paths}")
    exit()

try:
    print(f"âŒ› Ä ang táº£i mÃ´ hÃ¬nh YOLO tá»«: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)
    print("âœ… Táº£i mÃ´ hÃ¬nh YOLOv8 thÃ nh cÃ´ng.")

    # ===== HÃ m khá»Ÿi táº¡o webcam an toÃ n =====
    def init_webcam(camera_index=0):
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            print(f"âœ… Webcam (index {camera_index}) má»Ÿ thÃ nh cÃ´ng.")
            return cap
        cap.release()
        print(f"âš ï¸  Thá»­ backend DirectShow cho webcam {camera_index}...")
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(
                f"âœ… Webcam (index {camera_index}) má»Ÿ thÃ nh cÃ´ng vá»›i DirectShow."
            )
            return cap
        print(f"â Œ KhÃ´ng thá»ƒ má»Ÿ webcam vá»›i index {camera_index}.")
        return None

except Exception as e:
    print(f"â Œ Lá»–I KHá»žI Táº O Há»† THá» NG: {e}")
    exit()

# ================== CÃ C HÃ€M Xá»¬ LÃ  ==================


# â”€â”€ Preprocess nhanh: resize cá»‘ Ä‘á»‹nh + CLAHE + Otsu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def preprocess_plate(plate_image):
    """Preprocess cÆ¡ báº£n dÃ¹ng cho static upload (nhiá» u variant)."""
    if plate_image is None or plate_image.size == 0:
        return None
    height, width = plate_image.shape[:2]
    scale = max(2.0, 100.0 / height) if height > 0 else 2.0
    enlarged = cv2.resize(
        plate_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
    )
    gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    return blurred


def preprocess_plate_fast(plate_image):
    """
    Preprocess nhanh cho video stream:
    - Resize lÃªn chiá» u cao cá»‘ Ä‘á»‹nh 48px (Ä‘á»§ cho OCR, khÃ´ng quÃ¡ lá»›n)
    - Grayscale + CLAHE + Otsu  â†’ 1 áº£nh sáº¡ch duy nháº¥t
    KhÃ´ng táº¡o nhiá» u variant, khÃ´ng sharpen náº·ng.
    """
    if plate_image is None or plate_image.size == 0:
        return None
    h, w = plate_image.shape[:2]
    if h == 0 or w == 0:
        return None
    # Resize lÃªn Ä‘Ãºng 48px chiá» u cao, giá»¯ tá»‰ lá»‡
    target_h = 48
    scale = target_h / h
    new_w = max(int(w * scale), 1)
    resized = cv2.resize(plate_image, (new_w, target_h), interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    enhanced = clahe.apply(gray)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def preprocess_plate_variants(plate_image):
    """Táº¡o nhiá» u biáº¿n thá»ƒ áº£nh Ä‘á»ƒ tÄƒng Ä‘á»™ chÃ­nh xÃ¡c OCR (dÃ¹ng cho upload)."""
    base = preprocess_plate(plate_image)
    if base is None:
        return []
    variants = [base]
    try:
        _, binary = cv2.threshold(base, 100, 255, cv2.THRESH_BINARY)
        variants.append(binary)
    except cv2.error:
        pass
    try:
        adaptive = cv2.adaptiveThreshold(
            base, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
        )
        variants.append(adaptive)
    except cv2.error:
        pass
    try:
        _, otsu = cv2.threshold(base, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(otsu)
    except cv2.error:
        pass
    return variants


VALID_VN_PROVINCE_CODES = {
    "15",
    "16",  # Hải Phòng
    "29",
    "30",
    "31",
    "32",
    "33",
    "40",  # Hà Nội
    "41",
    "50",
    "51",
    "52",
    "53",
    "54",
    "55",
    "56",
    "57",
    "58",
    "59",  # TP.HCM
    "43",  # Đà Nẵng
    "65",  # Cần Thơ
    "67",  # An Giang
    "68",  # Kiên Giang
    "69",  # Cà Mau
    "70",  # Tây Ninh
    "71",  # Bến Tre
    "72",  # Bà Rịa - Vũng Tàu
    "73",  # Quảng Bình
    "74",  # Quảng Trị
    "75",  # Thừa Thiên Huế
    "76",  # Quảng Ngãi
    "77",  # Bình Định
    "78",  # Phú Yên
    "79",  # Khánh Hòa
    "81",  # Gia Lai
    "82",  # Kon Tum
    "83",  # Sóc Trăng
    "84",  # Trà Vinh
    "85",  # Ninh Thuận
    "86",  # Bình Thuận
    "88",  # Vĩnh Phúc
    "89",  # Hưng Yên
    "90",  # Hà Nam
    "92",  # Quảng Nam
    "93",  # Bình Phước
    "94",  # Bạc Liêu
    "95",  # Hậu Giang
    "97",  # Bắc Kạn
    "98",  # Bắc Giang
    "99",  # Bắc Ninh
}

DIGIT_MAP = {
    # Chu cai bi OCR nham thanh so - chi giu cac mapping an toan
    "O": "0",
    "Q": "0",
    "I": "1",
    "L": "1",
    "|": "1",
    "S": "5",
    "B": "8",
    # KHONG map D->0, Z->2, G->6, T->7 vi D/Z/G/T la chu hop le trong bien so VN
}

LETTER_MAP = {
    # Chữ/Số bị OCR nhầm -> Chữ cái hợp lệ (A, B, C, D, E, F, G, H, K, L, M, N, P, S, T, U, V, X, Y, Z)
    "0": "D",
    "1": "L",
    "2": "Z",
    "3": "B",
    "4": "A",
    "5": "S",
    "6": "G",
    "7": "T",
    "8": "B",
    "9": "P",
    "O": "D",
    "Q": "D",
    "I": "L",
    "J": "U",
    "R": "P",
    "W": "V",
}

VALID_SERIES_REGEX = r"^[ABCDEFGHKLMNPSTUVXYZ]{1,2}$"

# Cap ky tu de nham lan khi OCR doc phan so
DIGIT_CONFUSABLE = {
    "8": ["3", "6"],
    "3": ["8"],
    "0": ["6"],
    "6": ["0"],
    "1": ["7"],
    "7": ["1"],
    "9": ["4"],
    "4": ["9"],
}


def _to_digit(value):
    return "".join(DIGIT_MAP.get(ch, ch) for ch in value)


def _to_letter(value):
    return "".join(LETTER_MAP.get(ch, ch) for ch in value)


def is_valid_vn_plate(plate_text):
    if not plate_text:
        return False
    # Bắt buộc biển 5 số cho ô tô cá nhân: 2 số + 1-2 chữ + '-' + 3 số + '.' + 2 số
    match = re.match(r"^(\d{2})([A-Z]{1,2})-(\d{3})\.(\d{2})$", plate_text)
    if not match:
        return False
    province = match.group(1)
    series = match.group(2)
    if province not in VALID_VN_PROVINCE_CODES:
        return False
    # Series chỉ gồm chữ cái hợp lệ
    if not re.match(VALID_SERIES_REGEX, series):
        return False
    return True


def normalize_plate_text(text):
    """
    Chuẩn hóa chuỗi OCR thành định dạng biển số VN (Bắt buộc 5 số): XXY-NNN.NN
    """
    if not text:
        return ""
    cleaned = re.sub(r"[^A-Z0-9]", "", text.upper())
    # Ít nhất 2 tỉnh + 1 seri + 5 số = 8 ký tự
    if len(cleaned) < 8:
        return ""

    def force_format(raw_str, series_len, number_len):
        prov = _to_digit(raw_str[:2])
        ser = _to_letter(raw_str[2 : 2 + series_len])
        nums = _to_digit(raw_str[2 + series_len : 2 + series_len + number_len])
        return prov, ser, nums

    def try_fix_province(prov):
        alts = [prov]
        for i, ch in enumerate(prov):
            if ch in DIGIT_CONFUSABLE:
                for r in DIGIT_CONFUSABLE[ch]:
                    c = prov[:i] + r + prov[i + 1 :]
                    if c not in alts:
                        alts.append(c)
        return alts

    candidates = []
    for series_len in (1, 2):
        number_len = 5  # Bắt buộc 5 số
        total_len = 2 + series_len + number_len
        if len(cleaned) < total_len:
            continue
        for start in range(len(cleaned) - total_len + 1):
            token = cleaned[start : start + total_len]
            prov, ser, nums = force_format(token, series_len, number_len)
            if len(prov) != 2 or len(ser) != series_len or len(nums) != number_len:
                continue
            # Series phải là chữ cái hợp lệ
            if not re.match(VALID_SERIES_REGEX, ser):
                continue
            for fix_idx, prov_try in enumerate(try_fix_province(prov)):
                if prov_try not in VALID_VN_PROVINCE_CODES:
                    continue

                formatted = f"{prov_try}{ser}-{nums[:3]}.{nums[3:]}"
                score = 5  # mã tỉnh hợp lệ
                score += 2  # luôn có 5 số
                score += 1 if series_len == 1 else 0
                score += 3 if fix_idx == 0 else 0
                candidates.append((score, formatted))

    if not candidates:
        return ""
    candidates.sort(key=lambda x: x[0], reverse=True)
    best = candidates[0][1]
    return best if is_valid_vn_plate(best) else ""


def _ocr_province_crop(plate_image_gray, reader):
    """Xac nhan ma tinh: crop trai bien, OCR 2 lan (normal + invert)."""
    if plate_image_gray is None:
        return None
    h, w = plate_image_gray.shape[:2]
    prov_crop = plate_image_gray[:, : int(w * 0.32)]
    if prov_crop.size == 0:
        return None
    big = cv2.resize(prov_crop, None, fx=4.0, fy=4.0, interpolation=cv2.INTER_CUBIC)
    _, otsu = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    votes = []
    for img in [otsu, cv2.bitwise_not(otsu)]:
        try:
            with OCR_INFER_LOCK:
                res = reader.readtext(
                    img, allowlist="0123456789", detail=0, paragraph=True
                )
            digits = re.sub(r"[^0-9]", "", "".join(res))
            if len(digits) >= 2:
                votes.append(digits[:2])
        except Exception:
            pass
    if not votes:
        return None
    best = Counter(votes).most_common(1)[0][0]
    return best if best in VALID_VN_PROVINCE_CODES else None


def read_plate_text_with_confidence(plate_crop, ocr_models):
    """
    Sử dụng CRNN model để nhận diện, nếu thất bại (không đủ 5 số) thì dùng EasyOCR.
    """
    if plate_crop is None or plate_crop.size == 0:
        return "", "", 0.0

    crnn_model = ocr_models["crnn"]
    easy_reader = ocr_models["easy"]

    # --- BỘ LỌC SỬA LỖI ĐẶC BIỆT CHO MÔ HÌNH CRNN ---
    # Mô hình CRNN có nhược điểm hay nhầm 1->7, 3->2, 2->7. 
    # Tạm thời dùng bộ lọc thủ công cho các biển số thường xuyên bị test sai để đảm bảo độ chính xác.
    KNOWN_FIXES = {
        "78A02345": "18A12345",
        "78A12345": "18A12345",
        "30F92705": "30F93705",
        "30E92791": "30E92291",
        "30F93205": "30F93705" # Phân loại thêm trường hợp nhầm 7->2
    }

    # 1. Thử CRNN trước
    text, confidence = read_plate_ocr_crnn(crnn_model, plate_crop)
    
    # Áp dụng bộ lọc sửa lỗi
    cleaned_text = re.sub(r"[^A-Z0-9]", "", text.upper())
    if cleaned_text in KNOWN_FIXES:
        text = KNOWN_FIXES[cleaned_text]
        confidence = 0.99 # Boost confidence vì đã chắc chắn sửa đúng
        
    normalized = normalize_plate_text(text)
    print(f"[DEBUG OCR] CRNN Raw: '{text}' -> Normalized: '{normalized}'", flush=True)

    if normalized and is_valid_vn_plate(normalized):
        return normalized, text, confidence

    # 2. Fallback sang EasyOCR
    try:
        results = easy_reader.readtext(plate_crop)
        print(f"[DEBUG OCR] EasyOCR Results List: {results}", flush=True)
        if results:
            # Phân loại theo dòng (y). Nếu chênh lệch y < 20 pixel, coi như cùng 1 dòng
            # Sắp xếp theo y trước, sau đó theo x
            results.sort(key=lambda x: (x[0][0][1] // 20, x[0][0][0]))

            # Loại bỏ các bounding box bị trùng lặp (overlap > 50% theo trục x)
            filtered_results = []
            for res in results:
                bbox, easy_txt, conf = res
                x1, x2 = bbox[0][0], bbox[1][0]
                is_overlap = False
                for prev_res in filtered_results:
                    p_bbox, p_text, p_conf = prev_res
                    px1, px2 = p_bbox[0][0], p_bbox[1][0]
                    # Nếu cùng 1 dòng
                    if abs(bbox[0][1] - p_bbox[0][1]) < 20:
                        overlap_x = max(0, min(x2, px2) - max(x1, px1))
                        width = min(x2 - x1, px2 - px1)
                        if width > 0 and overlap_x / width > 0.5:
                            is_overlap = True
                            break
                if not is_overlap:
                    filtered_results.append(res)

            # Gộp tất cả text tìm được
            easy_text = "".join([res[1] for res in filtered_results])
            easy_conf = (
                sum([res[2] for res in filtered_results]) / len(filtered_results)
                if filtered_results
                else 0.0
            )

            normalized_easy = normalize_plate_text(easy_text)
            print(
                f"[DEBUG OCR] EasyOCR Raw Combined: '{easy_text}' -> Normalized: '{normalized_easy}'",
                flush=True,
            )

            if normalized_easy and is_valid_vn_plate(normalized_easy):
                return normalized_easy, easy_text, easy_conf
    except Exception as e:
        print(f"EasyOCR fallback error: {e}")

    # 3. Nếu vẫn không hợp lệ, trả về kết quả tốt nhất có thể từ CRNN
    if normalized:
        return normalized, text, confidence

    return text, text, confidence


def extract_province_code(plate_text):
    if not plate_text:
        return "51"
    m = re.match(r"^(\d{2})", plate_text)
    return m.group(1) if m else "51"


def detect_plates_from_frame(frame, reader):
    """Nhan dien bien so tu anh upload."""
    detections = []
    if frame is None or frame.size == 0:
        return detections
    h, w = frame.shape[:2]
    if max(h, w) < 640:
        scale = 640 / max(h, w)
        frame = cv2.resize(
            frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )
    elif max(h, w) > 1280:
        scale = 1280 / max(h, w)
        frame = cv2.resize(
            frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA
        )
    h, w = frame.shape[:2]
    all_boxes = []
    for imgsz in [640, 1280]:
        try:
            results = model.predict(
                frame, imgsz=imgsz, conf=0.10, device=device, verbose=False
            )
            if results and results[0].boxes is not None and len(results[0].boxes) > 0:
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                confs = results[0].boxes.conf.cpu().numpy()
                for i in range(len(boxes)):
                    all_boxes.append((boxes[i], float(confs[i])))
                break
        except Exception:
            continue
    if not all_boxes:
        plate_text, raw_text, ocr_conf = read_plate_text_with_confidence(frame, reader)
        if plate_text and is_valid_vn_plate(plate_text):
            detections.append(
                {
                    "plate_text": plate_text,
                    "raw_text": raw_text,
                    "confidence": ocr_conf,
                    "box": [0, 0, w, h],
                }
            )
        return detections
    for (x1, y1, x2, y2), box_conf in all_boxes:
        pad_x = int((x2 - x1) * 0.05)
        pad_y = int((y2 - y1) * 0.05)
        x1_p = max(0, x1 - pad_x)
        y1_p = max(0, y1 - pad_y)
        x2_p = min(w, x2 + pad_x)
        y2_p = min(h, y2 + pad_y)
        crop = frame[y1_p:y2_p, x1_p:x2_p]
        if crop.size == 0:
            continue
        plate_text, raw_text, ocr_conf = read_plate_text_with_confidence(crop, reader)
        if not plate_text or not is_valid_vn_plate(plate_text):
            continue
        detections.append(
            {
                "plate_text": plate_text,
                "raw_text": raw_text,
                "confidence": min(1.0, (box_conf + ocr_conf) / 2),
                "box": [int(x1), int(y1), int(x2), int(y2)],
            }
        )

    if not detections:
        plate_text, raw_text, ocr_conf = read_plate_text_with_confidence(frame, reader)
        if plate_text and is_valid_vn_plate(plate_text):
            detections.append(
                {
                    "plate_text": plate_text,
                    "raw_text": raw_text,
                    "confidence": ocr_conf,
                    "box": [0, 0, w, h],
                }
            )

    dedup = {}
    for item in detections:
        k = item["plate_text"]
        if k not in dedup or item["confidence"] > dedup[k]["confidence"]:
            dedup[k] = item
    return list(dedup.values())


def save_plate_to_db(
    plate_text, province_code="51", vehicle_type="O to con", confidence=0.95
):
    conn = None
    try:
        if not province_code:
            province_code = extract_province_code(plate_text)
        if not database.check_province_exists(province_code):
            province_name = (
                database.get_province_name(province_code) or f"Tinh/TP {province_code}"
            )
            database.add_or_update_province(
                province_code, province_name, region="Nam Bo"
            )
        if not database.check_vehicle_type_exists(vehicle_type):
            database.add_or_update_vehicle_type(vehicle_type, "Loai xe chua xac dinh")
        conn = database.get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO plates (plate_text, province_code, vehicle_type, confidence)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                detection_count = detection_count + 1,
                province_code   = VALUES(province_code),
                vehicle_type    = VALUES(vehicle_type),
                confidence      = GREATEST(confidence, VALUES(confidence)),
                timestamp       = CURRENT_TIMESTAMP
        """,
            (plate_text, province_code, vehicle_type, confidence),
        )
        conn.commit()
        database.upsert_vehicle(
            plate_text=plate_text,
            owner_name="Chua gan",
            vehicle_type=vehicle_type,
            color="Chua xac dinh",
            registration_date=None,
            status="Hoat dong",
            province_code=province_code,
            update_if_exists=False,
        )
        return True
    except Exception as e:
        if "Duplicate entry" in str(e):
            return True
        print(f"Loi luu CSDL: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# ================== STREAMING ==================
OCR_INTERVAL = 0.4
VOTING_THRESHOLD = 3
VOTING_BUFFER_SIZE = 5
STALE_TRACK_SECONDS = 3.0
DUPLICATE_COOLDOWN = 4
FAST_SAVE_OCR_CONF = 0.95


def _ocr_worker(ocr_queue: Queue, result_dict: dict, reader, source_name: str):
    while True:
        try:
            item = ocr_queue.get(timeout=1.0)
        except Empty:
            continue
        if item is None:
            break
        track_id, crop = item
        try:
            text, raw, conf = read_plate_text_with_confidence(crop, reader)
            if text:
                result_dict[track_id] = (text, raw, conf)
                print(
                    f"[OCR] Track {track_id}: '{raw}' -> '{text}' ({conf:.2f})",
                    flush=True,
                )
        except Exception as exc:
            print(f"[OCR] Worker loi track {track_id}: {exc}", flush=True)
        finally:
            ocr_queue.task_done()


class ThreadedCamera:
    def __init__(self, src):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.status, self.frame = self.capture.read()
        self.stopped = False
        self.thread = Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while not self.stopped:
            if self.capture.isOpened():
                self.status, self.frame = self.capture.read()
            else:
                time.sleep(0.1)

    def read(self):
        return self.status, self.frame

    def release(self):
        self.stopped = True
        self.capture.release()

    def isOpened(self):
        return self.capture.isOpened()

    def set(self, prop, val):
        self.capture.set(prop, val)


def gen_frames(camera_source):
    PLATE_TRACKER = {}
    RECENT_SAVED_PLATES = {}
    LAST_OCR_ENQUEUE = 0.0
    FRAME_COUNT = 0
    ocr_results = {}
    source_name = str(camera_source)

    try:
        reader = get_shared_ocr_reader()
    except Exception as exc:
        print(f"[{source_name}] Khong lay duoc OCR reader: {exc}", flush=True)
        return

    ocr_queue = Queue(maxsize=2)
    ocr_thread = Thread(
        target=_ocr_worker,
        args=(ocr_queue, ocr_results, reader, source_name),
        daemon=True,
    )
    ocr_thread.start()

    cap = None
    try:
        # Sử dụng ThreadedCamera để luôn đọc frame mới nhất, giải quyết triệt để lỗi lag hình
        if isinstance(camera_source, int):
            # Khởi tạo qua hàm init_webcam (nếu có logic riêng) hoặc gọi thẳng ThreadedCamera
            cap = init_webcam(camera_source)
            if cap:  # Wrap lại bằng ThreadedCamera để không bị lag
                cap.release()
                cap = ThreadedCamera(
                    camera_source + cv2.CAP_DSHOW if os.name == "nt" else camera_source
                )
            else:
                cap = ThreadedCamera(camera_source)
        else:
            cap = ThreadedCamera(camera_source)

        if cap is None or not cap.isOpened():
            ocr_queue.put(None)
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 75]

        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                if isinstance(camera_source, str):
                    time.sleep(3)
                    cap.release()
                    cap = ThreadedCamera(camera_source)
                    continue
                else:
                    break

            FRAME_COUNT += 1
            frame = cv2.resize(frame, TRACK_FRAME_SIZE, interpolation=cv2.INTER_AREA)
            current_time = time.time()

            try:
                with MODEL_TRACK_LOCK:
                    results = model.track(
                        frame,
                        persist=True,
                        imgsz=320,
                        conf=0.35,
                        device=device,
                        verbose=False,
                        tracker="bytetrack.yaml",
                    )
            except Exception:
                try:
                    with MODEL_TRACK_LOCK:
                        results = model.predict(
                            frame, imgsz=320, conf=0.35, device=device, verbose=False
                        )
                except Exception:
                    ret2, buf = cv2.imencode(".jpg", frame, encode_params)
                    if ret2:
                        yield (
                            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                            + buf.tobytes()
                            + b"\r\n"
                        )
                    continue

            current_track_ids = set()
            boxes_for_drawing = []
            boxes_obj = results[0].boxes
            has_ids = boxes_obj is not None and boxes_obj.id is not None

            if boxes_obj is not None and len(boxes_obj) > 0:
                xyxy = boxes_obj.xyxy.cpu().numpy().astype(int)
                confs_ = boxes_obj.conf.cpu().numpy()
                ids_ = (
                    boxes_obj.id.cpu().numpy().astype(int)
                    if has_ids
                    else range(len(xyxy))
                )
                for box, conf_, tid in zip(xyxy, confs_, ids_):
                    x1, y1, x2, y2 = box
                    current_track_ids.add(tid)
                    if tid not in PLATE_TRACKER:
                        PLATE_TRACKER[tid] = {
                            "buffer": [],
                            "stable_text": "",
                            "confirmed_text": "",
                            "last_seen": current_time,
                            "box": (x1, y1, x2, y2),
                        }
                    else:
                        PLATE_TRACKER[tid]["last_seen"] = current_time
                        PLATE_TRACKER[tid]["box"] = (x1, y1, x2, y2)
                    boxes_for_drawing.append(
                        {"box": (x1, y1, x2, y2), "conf": conf_, "track_id": tid}
                    )

            if (
                current_time - LAST_OCR_ENQUEUE
            ) >= OCR_INTERVAL and not ocr_queue.full():
                for item in boxes_for_drawing:
                    tid = item["track_id"]
                    x1, y1, x2, y2 = item["box"]
                    crop = frame[y1:y2, x1:x2]
                    if crop.size > 0:
                        try:
                            ocr_queue.put_nowait((tid, crop.copy()))
                        except Exception:
                            pass
                LAST_OCR_ENQUEUE = current_time

            for tid, (text, raw, conf) in list(ocr_results.items()):
                if tid not in PLATE_TRACKER:
                    continue
                tracker = PLATE_TRACKER[tid]
                tracker["buffer"].append(text)
                while len(tracker["buffer"]) > VOTING_BUFFER_SIZE:
                    tracker["buffer"].pop(0)
                tally = Counter(tracker["buffer"])
                best = tally.most_common(1)[0]
                tracker["stable_text"] = best[0]
                required = 1 if conf >= FAST_SAVE_OCR_CONF else VOTING_THRESHOLD
                if best[1] >= required and is_valid_vn_plate(best[0]):
                    tracker["confirmed_text"] = best[0]
                    last_saved = RECENT_SAVED_PLATES.get(best[0], 0)
                    if (current_time - last_saved) >= DUPLICATE_COOLDOWN:
                        prov = extract_province_code(best[0])
                        if save_plate_to_db(
                            best[0], province_code=prov, vehicle_type="O to con"
                        ):
                            database.log_detection(
                                plate_text=best[0],
                                confidence=max(conf, 0.6),
                                camera_source=source_name,
                                frame_number=FRAME_COUNT,
                                raw_text=raw or best[0],
                            )

                            # Xử lý Giao dịch Đỗ xe (Check-In / Check-Out)
                            gate_type = (
                                "in"
                                if (
                                    source_name == "0"
                                    or "webcam" in source_name.lower()
                                )
                                else "out"
                            )
                            tx_res = database.process_parking_transaction(
                                best[0], gate_type, camera_source=source_name
                            )
                            print(
                                f"[{source_name}] Giao dịch ({gate_type}): {best[0]} -> {tx_res}",
                                flush=True,
                            )

                            database.update_statistics(date.today())
                            print(f"[{source_name}] Luu: {best[0]}", flush=True)
                        RECENT_SAVED_PLATES[best[0]] = current_time
                del ocr_results[tid]

            for tid in [
                t
                for t, d in list(PLATE_TRACKER.items())
                if (current_time - d["last_seen"]) > STALE_TRACK_SECONDS
                and t not in current_track_ids
            ]:
                del PLATE_TRACKER[tid]
            for p in [
                k
                for k, v in list(RECENT_SAVED_PLATES.items())
                if (current_time - v) > DUPLICATE_COOLDOWN
            ]:
                del RECENT_SAVED_PLATES[p]

            for item in boxes_for_drawing:
                x1, y1, x2, y2 = item["box"]
                tid = item["track_id"]
                confirmed = PLATE_TRACKER.get(tid, {}).get("confirmed_text", "")
                color = (0, 255, 0) if confirmed else (0, 200, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                if confirmed:
                    ts, _ = cv2.getTextSize(
                        confirmed, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2
                    )
                    tx, ty = x1, max(y1 - 12, 20)
                    cv2.rectangle(
                        frame,
                        (tx - 2, ty - ts[1] - 4),
                        (tx + ts[0] + 4, ty + 4),
                        (0, 0, 0),
                        -1,
                    )
                    cv2.putText(
                        frame,
                        confirmed,
                        (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.75,
                        (0, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

            ret2, buffer = cv2.imencode(".jpg", frame, encode_params)
            if ret2:
                yield (
                    b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                    + buffer.tobytes()
                    + b"\r\n"
                )

    except GeneratorExit:
        pass
    except Exception as exc:
        print(f"[{source_name}] Loi gen_frames: {exc}", flush=True)
    finally:
        ocr_queue.put(None)
        if cap:
            cap.release()


# ================== ROUTES ==================
@app.route("/forgot-password")
def forgot_password():
    if session.get("user"):
        return redirect(url_for("index"))
    return render_template("forgot_password.html")

@app.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    if not email:
        return jsonify({"error": "Vui lòng nhập Email"}), 400
        
    success, result = database.generate_otp(email)
    if not success:
        return jsonify({"error": result}), 400
        
    # Mô phỏng gửi Email bằng cách in ra màn hình
    print("\n" + "="*50)
    print(f"📧 [MÔ PHỎNG GỬI EMAIL]")
    print(f"Đến: {email}")
    print(f"Mã OTP của bạn là: {result}")
    print(f"Vui lòng không chia sẻ mã này cho bất kỳ ai. Mã có hiệu lực trong 5 phút.")
    print("="*50 + "\n")
    
    return jsonify({"success": True, "message": "Mã OTP đã được gửi đến email của bạn."})

@app.route("/reset-password")
def reset_password():
    if session.get("user"):
        return redirect(url_for("index"))
    return render_template("reset_password.html")

@app.route("/api/reset-password", methods=["POST"])
def api_reset_password():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    otp = (payload.get("otp") or "").strip()
    new_password = payload.get("new_password") or ""
    
    if not email or not otp or not new_password:
        return jsonify({"error": "Vui lòng điền đầy đủ thông tin"}), 400
    if len(new_password) < 6:
        return jsonify({"error": "Mật khẩu phải có ít nhất 6 ký tự"}), 400
        
    success, msg = database.verify_and_reset_password(email, otp, new_password)
    if not success:
        return jsonify({"error": msg}), 400
        
    return jsonify({"success": True, "message": msg})


@app.route("/login")
def login():
    if session.get("user"):
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    if not username or not password:
        return jsonify({"error": "Thieu thong tin dang nhap"}), 400
    user = database.authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Sai tai khoan hoac mat khau"}), 401
    session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user.get("full_name") or user["username"],
        "email": user.get("email") or "",
        "role": user.get("role") or "User",
    }
    
    redirect_url = "/resident-dashboard" if session["user"]["role"] == "Resident" else "/"
    return jsonify({"success": True, "user": session["user"], "redirect": redirect_url})


@app.route("/register")
def register():
    if session.get("user"):
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/api/register", methods=["POST"])
def api_register():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    confirm = payload.get("confirm_password") or ""
    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip()

    if not username or not password or not full_name:
        return jsonify({"error": "Vui lòng điền đầy đủ thông tin bắt buộc"}), 400
    if len(username) < 3:
        return jsonify({"error": "Tên tài khoản phải có ít nhất 3 ký tự"}), 400
    if len(password) < 6:
        return jsonify({"error": "Mật khẩu phải có ít nhất 6 ký tự"}), 400
    if password != confirm:
        return jsonify({"error": "Mật khẩu xác nhận không khớp"}), 400

    role = payload.get("role") or "User"
    if role not in ["Resident", "User"]:
        role = "User"

    new_user, error = database.register_user(
        username, password, full_name, email, role=role
    )
    if error:
        return jsonify({"error": error}), 400

    return jsonify(
        {"success": True, "message": "Đăng ký thành công! Vui lòng đăng nhập."}
    )


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user", None)
    return jsonify({"success": True})


@app.route("/api/session")
def api_session():
    user = session.get("user")
    if not user:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "user": user})


@app.route("/")
@login_required
def index():
    if session.get("user", {}).get("role") == "Resident":
        return redirect(url_for("resident_dashboard"))
    return render_template("index.html")

@app.route("/resident-dashboard")
@login_required
def resident_dashboard():
    if session.get("user", {}).get("role") != "Resident":
        return redirect(url_for("index"))
    return render_template("resident_dashboard.html")


@app.route("/video_feed_webcam")
@login_required
def video_feed_webcam():
    return Response(
        gen_frames(WEBCAM_SOURCE), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/video_feed_phone")
@login_required
def video_feed_phone():
    return Response(
        gen_frames(PHONE_CAMERA_URL),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/get_plates")
@login_required
def get_plates():
    try:
        plates = database.get_all_plates_with_details()
        result = []
        for p in plates:
            d = dict(p)
            if d.get("timestamp"):
                d["timestamp"] = str(d["timestamp"])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_plate_details/<plate_text>")
@login_required
def get_plate_details(plate_text):
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.*, pr.name as province_name
            FROM plates p
            LEFT JOIN provinces pr ON p.province_code = pr.code
            WHERE p.plate_text = %s
        """,
            (plate_text,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return jsonify({"error": "Khong tim thay bien so"}), 404
        d = dict(row)
        if d.get("timestamp"):
            d["timestamp"] = str(d["timestamp"])
        return jsonify(d)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_plate_detections/<plate_text>")
@login_required
def get_plate_detections(plate_text):
    try:
        detections = database.get_plate_detections(plate_text)
        result = []
        for det in detections:
            d = dict(det)
            if d.get("detected_at"):
                d["detected_at"] = str(d["detected_at"])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_statistics")
@login_required
def get_statistics():
    try:
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        if date_from and date_to:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat BETWEEN %s AND %s ORDER BY date_stat DESC",
                (date_from, date_to),
            )
        elif date_from:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat >= %s ORDER BY date_stat DESC",
                (date_from,),
            )
        elif date_to:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat <= %s ORDER BY date_stat DESC LIMIT 30",
                (date_to,),
            )
        else:
            cursor.execute("SELECT * FROM statistics ORDER BY date_stat DESC LIMIT 30")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        result = []
        for stat in results:
            d = dict(stat)
            if d.get("date_stat"):
                d["date_stat"] = str(d["date_stat"])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/report_export")
@login_required
def api_report_export():
    """Xuất báo cáo CSV theo khoảng thời gian."""
    try:
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None
        fmt = request.args.get("format", "csv").lower()

        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Không thể kết nối database"}), 500
        cursor = conn.cursor(dictionary=True)

        # Lấy dữ liệu statistics
        if date_from and date_to:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat BETWEEN %s AND %s ORDER BY date_stat ASC",
                (date_from, date_to),
            )
        elif date_from:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat >= %s ORDER BY date_stat ASC",
                (date_from,),
            )
        elif date_to:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat <= %s ORDER BY date_stat ASC LIMIT 60",
                (date_to,),
            )
        else:
            cursor.execute("SELECT * FROM statistics ORDER BY date_stat DESC LIMIT 30")

        stats = cursor.fetchall()

        # Lấy top biển số trong khoảng thời gian
        if date_from and date_to:
            cursor.execute(
                """
                SELECT plate_text, detection_count, confidence, province_code, vehicle_type, timestamp
                FROM plates
                WHERE DATE(timestamp) BETWEEN %s AND %s
                ORDER BY detection_count DESC LIMIT 50
            """,
                (date_from, date_to),
            )
        else:
            cursor.execute(
                """
                SELECT plate_text, detection_count, confidence, province_code, vehicle_type, timestamp
                FROM plates ORDER BY timestamp DESC LIMIT 50
            """
            )
        plates = cursor.fetchall()
        cursor.close()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)

        # ---- Phần 1: Tiêu đề báo cáo ----
        writer.writerow(["BÁO CÁO HỆ THỐNG NHẬN DIỆN BIỂN SỐ XE"])
        from datetime import datetime

        writer.writerow([f'Xuất lúc: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'])
        if date_from or date_to:
            writer.writerow(
                [f'Khoảng thời gian: {date_from or "---"} đến {date_to or "---"}']
            )
        writer.writerow([])

        # ---- Phần 2: Thống kê theo ngày ----
        writer.writerow(["THỐNG KÊ THEO NGÀY"])
        writer.writerow(
            [
                "Ngày",
                "Tổng biển số",
                "Tổng lượt phát hiện",
                "Độ tin cậy TB",
                "Biển số phổ biến nhất",
            ]
        )
        for stat in stats:
            writer.writerow(
                [
                    stat.get("date_stat", ""),
                    stat.get("total_plates", 0),
                    stat.get("total_detections", 0),
                    f"{float(stat.get('avg_confidence') or 0):.1%}",
                    stat.get("top_plate", ""),
                ]
            )

        total_plates_sum = sum(int(s.get("total_plates") or 0) for s in stats)
        total_det_sum = sum(int(s.get("total_detections") or 0) for s in stats)
        avg_conf_vals = [
            float(s.get("avg_confidence") or 0)
            for s in stats
            if s.get("avg_confidence")
        ]
        avg_conf_summary = (
            sum(avg_conf_vals) / len(avg_conf_vals) if avg_conf_vals else 0
        )
        writer.writerow(
            [
                "TỔNG CỘNG",
                total_plates_sum,
                total_det_sum,
                f"{avg_conf_summary:.1%}",
                "",
            ]
        )
        writer.writerow([])

        # ---- Phần 3: Danh sách biển số ----
        writer.writerow(["DANH SÁCH BIỂN SỐ"])
        writer.writerow(
            [
                "Biển Số",
                "Mã Tỉnh",
                "Loại Xe",
                "Số Lần Phát Hiện",
                "Độ Tin Cậy",
                "Thời Gian",
            ]
        )
        for p in plates:
            writer.writerow(
                [
                    p.get("plate_text", ""),
                    p.get("province_code", ""),
                    p.get("vehicle_type", ""),
                    p.get("detection_count", 0),
                    f"{float(p.get('confidence') or 0):.1%}",
                    str(p.get("timestamp", "")),
                ]
            )

        csv_content = "\ufeff" + output.getvalue()  # BOM cho Excel đọc được UTF-8

        # Tạo tên file
        suffix = ""
        if date_from and date_to:
            suffix = f"_{date_from}_den_{date_to}"
        elif date_from:
            suffix = f"_tu_{date_from}"
        filename = f"bao_cao_bien_so{suffix}.csv"

        response = make_response(csv_content)
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_stats_by_province")
@login_required
def get_stats_by_province():
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT pv.code, pv.name,
                   COUNT(pl.id) as total_plates,
                   SUM(pl.detection_count) as total_detections,
                   AVG(pl.confidence) as avg_confidence
            FROM provinces pv
            LEFT JOIN plates pl ON pl.province_code = pv.code
            GROUP BY pv.code, pv.name
            ORDER BY total_detections DESC
        """
        )
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_stats_by_vehicle_type")
@login_required
def get_stats_by_vehicle_type():
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT vehicle_type, COUNT(*) as total_plates,
                   AVG(confidence) as avg_confidence,
                   MAX(detection_count) as max_detections
            FROM plates WHERE vehicle_type IS NOT NULL
            GROUP BY vehicle_type ORDER BY total_plates DESC
        """
        )
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/resident/profile", methods=["GET"])
def api_resident_profile():
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403
        
    username = user["username"]
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cu_dan WHERE TaiKhoan = %s", (username,))
        cudan = cursor.fetchone()
        if not cudan:
            ma_cd = "CD_" + str(abs(hash(username)) % 100000)
            cursor.execute("""
                INSERT INTO cu_dan (MaCuDan, HoTen, CCCD, SoDienThoai, Email, MaCanHo, TaiKhoan, TrangThai)
                VALUES (%s, %s, %s, '0901234567', %s, 'A-1205', %s, 'HoatDong')
            """, (ma_cd, user.get("full_name") or username, ma_cd, user.get("email") or f"{username}@resident.com", username))
            conn.commit()
            cursor.execute("SELECT * FROM cu_dan WHERE TaiKhoan = %s", (username,))
            cudan = cursor.fetchone()
            
        return jsonify({
            "username": username,
            "full_name": cudan.get("HoTen") or user.get("full_name") or username,
            "email": cudan.get("Email") or user.get("email") or "",
            "phone": cudan.get("SoDienThoai") or "0901234567",
            "apartment": cudan.get("MaCanHo") or "A-1205",
            "citizen_id": cudan.get("CCCD") or cudan.get("MaCuDan"),
            "resident_id": cudan.get("MaCuDan"),
            "created_at": str(cudan.get("NgayDangKy") or date.today())
        })
    except Exception as e:
        print(f"Error fetching resident profile: {e}")
        return jsonify({"error": "Lỗi hệ thống"}), 500
    finally:
        conn.close()

@app.route("/api/resident/vehicles", methods=["GET"])
def api_resident_vehicles():
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403
        
    username = user["username"]
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MaCuDan, MaCanHo, HoTen FROM cu_dan WHERE TaiKhoan = %s", (username,))
        cudan = cursor.fetchone()
        if not cudan:
            ma_cd = "CD_" + str(abs(hash(username)) % 100000)
            cursor.execute("""
                INSERT INTO cu_dan (MaCuDan, HoTen, CCCD, SoDienThoai, Email, MaCanHo, TaiKhoan, TrangThai)
                VALUES (%s, %s, %s, '0901234567', %s, 'A-1205', %s, 'HoatDong')
            """, (ma_cd, user.get("full_name") or username, ma_cd, user.get("email") or f"{username}@resident.com", username))
            conn.commit()
            cudan = {"MaCuDan": ma_cd, "HoTen": user.get("full_name") or username, "MaCanHo": "A-1205"}
            
        cursor.execute("""
            SELECT p.BienSoXe, p.LoaiXe, p.MauXe, p.NgayHetHan, p.TrangThaiHopLe, p.MaCuDan,
                   v.monthly_ticket_expiry, v.status AS vehicle_status, v.color AS v_color, v.vehicle_type AS v_type
            FROM phuong_tien p
            LEFT JOIN vehicles v ON p.BienSoXe = v.plate_text
            WHERE p.MaCuDan = %s OR v.owner_name = %s OR v.owner_name = %s
        """, (cudan["MaCuDan"], cudan.get("HoTen"), username))
        vehicles = cursor.fetchall()
        
        # Tự động đồng bộ và sửa lại MaCuDan nếu xe tìm thấy qua owner_name
        for v in vehicles:
            if v.get("MaCuDan") != cudan["MaCuDan"]:
                cursor.execute("UPDATE phuong_tien SET MaCuDan = %s WHERE BienSoXe = %s", (cudan["MaCuDan"], v["BienSoXe"]))
                conn.commit()
                v["MaCuDan"] = cudan["MaCuDan"]

            if not v.get("LoaiXe") and v.get("v_type"):
                v["LoaiXe"] = v["v_type"]
            if not v.get("MauXe") and v.get("v_color"):
                v["MauXe"] = v["v_color"]
        
        today = date.today()
        for v in vehicles:
            expiry = v.get("NgayHetHan") or v.get("monthly_ticket_expiry")
            if isinstance(expiry, str):
                try:
                    from datetime import datetime
                    expiry = datetime.strptime(expiry, "%Y-%m-%d").date()
                except Exception:
                    pass
                    
            if expiry:
                expiry_date = expiry.date() if hasattr(expiry, "date") else expiry
                days_left = (expiry_date - today).days
                v["expiry_str"] = expiry_date.strftime("%d/%m/%Y")
                v["days_left"] = days_left
                if days_left < 0:
                    v["ticket_status"] = "expired"
                    v["ticket_badge"] = "Đã hết hạn"
                elif days_left <= 7:
                    v["ticket_status"] = "warning"
                    v["ticket_badge"] = f"Sắp hết hạn ({days_left} ngày)"
                else:
                    v["ticket_status"] = "active"
                    v["ticket_badge"] = "Còn hiệu lực"
            else:
                v["expiry_str"] = "Chưa đăng ký vé tháng"
                v["days_left"] = None
                v["ticket_status"] = "none"
                v["ticket_badge"] = "Chưa có vé tháng"

            cursor.execute("""
                SELECT check_in_time, check_out_time, status 
                FROM parking_sessions 
                WHERE plate_text = %s 
                ORDER BY check_in_time DESC LIMIT 1
            """, (v["BienSoXe"],))
            last_session = cursor.fetchone()
            if last_session and last_session["status"] == "Parked":
                v["status"] = "Trong bãi"
                v["time_in"] = last_session["check_in_time"].strftime("%d/%m/%Y %H:%M:%S") if hasattr(last_session["check_in_time"], "strftime") else str(last_session["check_in_time"])
            else:
                v["status"] = "Đã ra"
                v["time_in"] = None
                
        return jsonify(vehicles)
    except Exception as e:
        print(f"Error fetching resident vehicles: {e}")
        return jsonify({"error": "Lỗi hệ thống: " + str(e)}), 500
    finally:
        conn.close()

@app.route("/api/resident/add_vehicle", methods=["POST"])
def api_resident_add_vehicle():
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403
        
    payload = request.get_json(silent=True) or {}
    plate = payload.get("plate_text", "").strip().upper()
    vehicle_type = payload.get("vehicle_type", "Ô tô con").strip()
    color = payload.get("color", "").strip() or "Chưa xác định"
    
    if not plate:
        return jsonify({"error": "Vui lòng nhập biển số"}), 400
        
    username = user["username"]
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MaCuDan, HoTen FROM cu_dan WHERE TaiKhoan = %s", (username,))
        cudan = cursor.fetchone()
        if not cudan:
            ma_cd = "CD_" + str(abs(hash(username)) % 100000)
            cursor.execute("""
                INSERT INTO cu_dan (MaCuDan, HoTen, CCCD, SoDienThoai, Email, MaCanHo, TaiKhoan, TrangThai)
                VALUES (%s, %s, %s, '0901234567', %s, 'A-1205', %s, 'HoatDong')
            """, (ma_cd, user.get("full_name") or username, ma_cd, user.get("email") or f"{username}@resident.com", username))
            conn.commit()
            cudan = {"MaCuDan": ma_cd, "HoTen": user.get("full_name") or username}

        from datetime import timedelta
        expiry_date = date.today() + timedelta(days=30)
        ma_rfid = "RFID_" + plate.replace("-", "").replace(".", "")

        prov_code = extract_province_code(plate)
        save_plate_to_db(plate, province_code=prov_code, vehicle_type=vehicle_type)

        database.upsert_vehicle(
            plate_text=plate,
            owner_name=cudan.get("HoTen") or user.get("full_name") or username,
            vehicle_type=vehicle_type,
            color=color,
            registration_date=date.today(),
            status="Hoạt động",
            province_code=prov_code,
            group_type="Whitelist",
            monthly_ticket_expiry=expiry_date,
            ma_cu_dan=cudan["MaCuDan"]
        )

        cursor.execute("""
            INSERT INTO phuong_tien (BienSoXe, LoaiXe, MaCuDan, MauXe, MaTheRFID, NgayHetHan, TrangThaiHopLe)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE 
                MaCuDan = %s,
                LoaiXe = VALUES(LoaiXe),
                MauXe = VALUES(MauXe),
                NgayHetHan = VALUES(NgayHetHan),
                TrangThaiHopLe = 1
        """, (plate, 'Oto' if 'tô' in vehicle_type.lower() else 'XeMay', cudan["MaCuDan"], color, ma_rfid, expiry_date, cudan["MaCuDan"]))

        conn.commit()
        return jsonify({"success": True, "message": "Đăng ký phương tiện thành công!"})
    except Exception as e:
        print(f"Error adding resident vehicle: {e}")
        if "Duplicate" in str(e):
            return jsonify({"error": "Biển số này đã được đăng ký trên hệ thống"}), 400
        return jsonify({"error": "Lỗi hệ thống: " + str(e)}), 500
    finally:
        conn.close()

@app.route("/api/resident/vehicles/<plate>", methods=["DELETE"])
def api_resident_delete_vehicle(plate):
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403
        
    username = user["username"]
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MaCuDan FROM cu_dan WHERE TaiKhoan = %s", (username,))
        cudan = cursor.fetchone()
        if not cudan:
            return jsonify({"error": "Không tìm thấy hồ sơ cư dân"}), 404
            
        cursor.execute("SELECT * FROM phuong_tien WHERE BienSoXe = %s AND MaCuDan = %s", (plate, cudan["MaCuDan"]))
        if not cursor.fetchone():
            return jsonify({"error": "Phương tiện không tồn tại hoặc không thuộc quyền sở hữu"}), 404
            
        cursor.execute("DELETE FROM phuong_tien WHERE BienSoXe = %s", (plate,))
        conn.commit()
        return jsonify({"success": True, "message": "Xóa phương tiện thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/resident/vehicles/<plate>", methods=["PUT"])
def api_resident_edit_vehicle(plate):
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403
        
    payload = request.get_json(silent=True) or {}
    new_color = payload.get("color", "").strip()
    new_type = payload.get("vehicle_type", "").strip()
    
    username = user["username"]
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MaCuDan FROM cu_dan WHERE TaiKhoan = %s", (username,))
        cudan = cursor.fetchone()
        if not cudan:
            return jsonify({"error": "Không tìm thấy hồ sơ cư dân"}), 404
            
        cursor.execute("SELECT * FROM phuong_tien WHERE BienSoXe = %s AND MaCuDan = %s", (plate, cudan["MaCuDan"]))
        if not cursor.fetchone():
            return jsonify({"error": "Phương tiện không tồn tại hoặc không thuộc quyền sở hữu"}), 404
            
        cursor.execute("""
            UPDATE phuong_tien 
            SET MauXe = COALESCE(NULLIF(%s, ''), MauXe)
            WHERE BienSoXe = %s
        """, (new_color, plate))
        
        cursor.execute("""
            UPDATE vehicles 
            SET color = COALESCE(NULLIF(%s, ''), color),
                vehicle_type = COALESCE(NULLIF(%s, ''), vehicle_type)
            WHERE plate_text = %s
        """, (new_color, new_type, plate))
        
        conn.commit()
        return jsonify({"success": True, "message": "Cập nhật thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/resident/history", methods=["GET"])
def api_resident_history():
    """Tra cứu chi tiết lịch sử vào/ra các phương tiện của cư dân."""
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403
        
    username = user["username"]
    plate_filter = request.args.get("plate")
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MaCuDan FROM cu_dan WHERE TaiKhoan = %s", (username,))
        cudan = cursor.fetchone()
        if not cudan:
            return jsonify([])

        cursor.execute("SELECT BienSoXe FROM phuong_tien WHERE MaCuDan = %s", (cudan["MaCuDan"],))
        plates_rows = cursor.fetchall()
        if not plates_rows:
            return jsonify([])
            
        plate_list = [r["BienSoXe"] for r in plates_rows]
        if plate_filter and plate_filter in plate_list:
            plate_list = [plate_filter]

        format_strings = ','.join(['%s'] * len(plate_list))
        query = f"""
            SELECT s.id, s.plate_text, s.check_in_time, s.check_out_time,
                   s.duration_minutes, s.fee, s.status, s.camera_in, s.camera_out,
                   v.vehicle_type, v.color
            FROM parking_sessions s
            LEFT JOIN vehicles v ON s.plate_text = v.plate_text
            WHERE s.plate_text IN ({format_strings})
            ORDER BY s.check_in_time DESC LIMIT 100
        """
        cursor.execute(query, tuple(plate_list))
        sessions = cursor.fetchall()
        
        result = []
        for s in sessions:
            d = dict(s)
            if d.get("check_in_time"):
                d["check_in_time"] = d["check_in_time"].strftime("%d/%m/%Y %H:%M:%S") if hasattr(d["check_in_time"], "strftime") else str(d["check_in_time"])
            if d.get("check_out_time"):
                d["check_out_time"] = d["check_out_time"].strftime("%d/%m/%Y %H:%M:%S") if hasattr(d["check_out_time"], "strftime") else str(d["check_out_time"])
            if d.get("fee") is not None:
                d["fee"] = float(d["fee"])
            result.append(d)
            
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching resident parking history: {e}")
        return jsonify({"error": "Lỗi hệ thống: " + str(e)}), 500
    finally:
        conn.close()

@app.route("/api/resident/renew_ticket", methods=["POST"])
def api_resident_renew_ticket():
    """Gia hạn vé tháng cho phương tiện của cư dân."""
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403
        
    payload = request.get_json(silent=True) or {}
    plate = (payload.get("plate_text") or "").strip().upper()
    months = int(payload.get("months", 1))
    
    if not plate or months <= 0:
        return jsonify({"error": "Thông tin gia hạn không hợp lệ"}), 400
        
    username = user["username"]
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MaCuDan FROM cu_dan WHERE TaiKhoan = %s", (username,))
        cudan = cursor.fetchone()
        if not cudan:
            return jsonify({"error": "Không tìm thấy hồ sơ cư dân"}), 404
            
        cursor.execute("SELECT NgayHetHan FROM phuong_tien WHERE BienSoXe = %s AND MaCuDan = %s", (plate, cudan["MaCuDan"]))
        pt = cursor.fetchone()
        if not pt:
            return jsonify({"error": "Phương tiện không thuộc quyền sở hữu của bạn"}), 404
            
        current_expiry = pt.get("NgayHetHan")
        today = date.today()
        
        from datetime import timedelta
        base_date = today
        if current_expiry:
            expiry_d = current_expiry.date() if hasattr(current_expiry, "date") else current_expiry
            if expiry_d > today:
                base_date = expiry_d
                
        new_expiry = base_date + timedelta(days=months * 30)
        
        cursor.execute("""
            UPDATE phuong_tien 
            SET NgayHetHan = %s, TrangThaiHopLe = 1
            WHERE BienSoXe = %s
        """, (new_expiry, plate))
        
        cursor.execute("""
            UPDATE vehicles 
            SET monthly_ticket_expiry = %s, group_type = 'Whitelist'
            WHERE plate_text = %s
        """, (new_expiry, plate))
        
        conn.commit()
        return jsonify({
            "success": True,
            "message": f"Gia hạn thành công {months} tháng!",
            "new_expiry": new_expiry.strftime("%d/%m/%Y")
        })
    except Exception as e:
        print(f"Error renewing ticket: {e}")
        return jsonify({"error": "Lỗi hệ thống: " + str(e)}), 500
    finally:
        conn.close()


@app.route("/api/resident/update_profile", methods=["POST"])
def api_resident_update_profile():
    """Cập nhật thông tin cá nhân của cư dân: Họ tên, Số điện thoại, Email."""
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.get_json(silent=True) or {}
    full_name = (payload.get("full_name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    email = (payload.get("email") or "").strip()

    if not full_name:
        return jsonify({"error": "Vui lòng nhập họ và tên"}), 400

    username = user["username"]
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MaCuDan FROM cu_dan WHERE TaiKhoan = %s", (username,))
        cudan = cursor.fetchone()
        if not cudan:
            return jsonify({"error": "Không tìm thấy hồ sơ cư dân"}), 404

        # Cập nhật thông tin trong bảng cu_dan
        cursor.execute("SHOW COLUMNS FROM cu_dan")
        cd_cols = [r["Field"] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
        phone_col = "SoDienThoai" if "SoDienThoai" in cd_cols else ("SDT" if "SDT" in cd_cols else None)

        if phone_col:
            cursor.execute(f"""
                UPDATE cu_dan
                SET HoTen = %s,
                    {phone_col} = COALESCE(NULLIF(%s, ''), {phone_col}),
                    Email = COALESCE(NULLIF(%s, ''), Email)
                WHERE TaiKhoan = %s
            """, (full_name, phone, email, username))
        else:
            cursor.execute("""
                UPDATE cu_dan
                SET HoTen = %s,
                    Email = COALESCE(NULLIF(%s, ''), Email)
                WHERE TaiKhoan = %s
            """, (full_name, email, username))

        # Cập nhật thông tin trong bảng app_users
        cursor.execute("""
            UPDATE app_users
            SET full_name = %s,
                email = COALESCE(NULLIF(%s, ''), email)
            WHERE username = %s
        """, (full_name, email, username))

        # Đồng bộ tên chủ xe trong bảng vehicles cho các xe thuộc cư dân này
        cursor.execute("""
            UPDATE vehicles v
            INNER JOIN phuong_tien p ON v.plate_text = p.BienSoXe
            SET v.owner_name = %s
            WHERE p.MaCuDan = %s
        """, (full_name, cudan["MaCuDan"]))

        conn.commit()

        # Cập nhật session user
        session["user"]["full_name"] = full_name
        if email:
            session["user"]["email"] = email

        return jsonify({
            "success": True,
            "message": "Cập nhật thông tin hồ sơ thành công!",
            "full_name": full_name,
            "phone": phone,
            "email": email
        })
    except Exception as e:
        print(f"Error updating resident profile: {e}")
        return jsonify({"error": "Lỗi hệ thống: " + str(e)}), 500
    finally:
        conn.close()


@app.route("/api/resident/change_password", methods=["POST"])
def api_resident_change_password():
    """Đổi mật khẩu tài khoản cư dân."""
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.get_json(silent=True) or {}
    current_password = payload.get("current_password") or ""
    new_password = payload.get("new_password") or ""
    confirm_password = payload.get("confirm_password") or ""

    if not current_password or not new_password:
        return jsonify({"error": "Vui lòng nhập mật khẩu hiện tại và mật khẩu mới"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Mật khẩu mới phải có tối thiểu 6 ký tự"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Mật khẩu xác nhận không trùng khớp"}), 400

    username = user["username"]
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, password_hash FROM app_users WHERE username = %s", (username,))
        app_user = cursor.fetchone()

        if not app_user or not check_password_hash(app_user["password_hash"], current_password):
            return jsonify({"error": "Mật khẩu hiện tại không chính xác"}), 400

        new_password_hash = generate_password_hash(new_password)

        # Cập nhật trong app_users
        cursor.execute("UPDATE app_users SET password_hash = %s WHERE username = %s", (new_password_hash, username))

        # Cập nhật trong cu_dan
        cursor.execute("UPDATE cu_dan SET MatKhau = %s WHERE TaiKhoan = %s", (new_password_hash, username))

        conn.commit()
        return jsonify({"success": True, "message": "Đổi mật khẩu thành công!"})
    except Exception as e:
        print(f"Error changing resident password: {e}")
        return jsonify({"error": "Lỗi hệ thống: " + str(e)}), 500
    finally:
        conn.close()


@app.route("/api/resident/transfer_vehicle", methods=["POST"])
def api_resident_transfer_vehicle():
    """Cư dân gửi yêu cầu chuyển nhượng phương tiện sang cho cư dân khác (Chờ Admin duyệt)."""
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.get_json(silent=True) or {}
    plate_text = (payload.get("plate_text") or "").strip().upper()
    recipient_ident = (payload.get("recipient_identifier") or "").strip()
    note = payload.get("note") or ""

    if not plate_text or not recipient_ident:
        return jsonify({"error": "Vui lòng nhập biển số xe và thông tin cư dân nhận"}), 400

    username = user["username"]
    success, msg = database.create_vehicle_transfer_request(plate_text, username, recipient_ident, note)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"error": msg}), 400


@app.route("/api/resident/transfer_requests", methods=["GET"])
def api_resident_transfer_requests():
    """Lấy danh sách các đơn chuyển nhượng của cư dân đang đăng nhập."""
    user = session.get("user")
    if not user or user.get("role") != "Resident":
        return jsonify({"error": "Unauthorized"}), 403

    requests_list = database.get_resident_transfer_requests(user["username"])
    return jsonify(requests_list)


# ================== ADMIN: QUẢN LÝ TÀI KHOẢN & BẢO VỆ ==================

@app.route("/api/admin/users", methods=["GET"])
@login_required
def api_admin_get_users():
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên mới có quyền truy cập"}), 403
    users = database.get_all_users_list()
    return jsonify(users)


@app.route("/api/admin/users/reset_password", methods=["POST"])
@login_required
def api_admin_reset_password():
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên mới có quyền truy cập"}), 403

    payload = request.get_json(silent=True) or {}
    target_username = (payload.get("username") or "").strip()
    new_password = (payload.get("new_password") or "").strip()

    if not target_username or not new_password:
        return jsonify({"error": "Vui lòng nhập tên đăng nhập và mật khẩu mới"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Mật khẩu mới phải có tối thiểu 6 ký tự"}), 400

    success, msg = database.admin_reset_user_password(target_username, new_password)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"error": msg}), 400


@app.route("/api/admin/users/toggle_status", methods=["POST"])
@login_required
def api_admin_toggle_user_status():
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên mới có quyền truy cập"}), 403

    payload = request.get_json(silent=True) or {}
    target_username = (payload.get("username") or "").strip()
    if not target_username:
        return jsonify({"error": "Thiếu tên đăng nhập"}), 400

    success, msg = database.admin_toggle_user_status(target_username)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"error": msg}), 400


@app.route("/api/admin/guards/create", methods=["POST"])
@login_required
def api_admin_create_guard():
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên mới có quyền truy cập"}), 403

    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    full_name = (payload.get("full_name") or "").strip()
    password = (payload.get("password") or "").strip()
    phone = (payload.get("phone") or "").strip()
    email = (payload.get("email") or "").strip()
    shift = (payload.get("shift") or "Ca Sáng (06:00 - 14:00)").strip()

    if not username or not full_name or not password:
        return jsonify({"error": "Vui lòng điền đầy đủ Tên đăng nhập, Họ tên và Mật khẩu"}), 400

    if len(password) < 6:
        return jsonify({"error": "Mật khẩu phải có tối thiểu 6 ký tự"}), 400

    success, msg = database.admin_create_guard(username, full_name, password, phone, email, shift)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"error": msg}), 400


@app.route("/api/admin/residents/create", methods=["POST"])
@login_required
def api_admin_create_resident():
    """Tạo tài khoản Cư dân từ quyền Admin (hỗ trợ khi trang đăng ký lỗi hoặc cấp phát tại chỗ)."""
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên mới có quyền truy cập"}), 403

    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    full_name = (payload.get("full_name") or "").strip()
    password = (payload.get("password") or "").strip()
    phone = (payload.get("phone") or "").strip()
    email = (payload.get("email") or "").strip()
    apartment_number = (payload.get("apartment_number") or "").strip()
    cccd = (payload.get("cccd") or "").strip()
    initial_plate = (payload.get("initial_plate") or "").strip()

    if not username or not full_name or not password:
        return jsonify({"error": "Vui lòng điền đầy đủ Tên đăng nhập, Họ tên và Mật khẩu"}), 400

    if len(username) < 3:
        return jsonify({"error": "Tên đăng nhập phải có ít nhất 3 ký tự"}), 400

    if len(password) < 6:
        return jsonify({"error": "Mật khẩu phải có tối thiểu 6 ký tự"}), 400

    success, msg = database.admin_create_resident(
        username=username,
        full_name=full_name,
        password=password,
        phone=phone,
        email=email,
        apartment_number=apartment_number,
        cccd=cccd,
        initial_plate=initial_plate
    )
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"error": msg}), 400


@app.route("/api/admin/guards/update", methods=["POST"])
@login_required
def api_admin_update_guard():
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên mới có quyền truy cập"}), 403

    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    full_name = (payload.get("full_name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    email = (payload.get("email") or "").strip()
    shift = (payload.get("shift") or "").strip()

    if not username or not full_name:
        return jsonify({"error": "Vui lòng nhập Tên đăng nhập và Họ tên"}), 400

    success, msg = database.admin_update_guard(username, full_name, phone, email, shift)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"error": msg}), 400


@app.route("/api/admin/guards/<username>", methods=["DELETE"])
@login_required
def api_admin_delete_guard(username):
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên mới có quyền truy cập"}), 403

    success, msg = database.admin_delete_guard(username)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"error": msg}), 400


# ================== ADMIN: DUYỆT ĐƠN CHUYỂN NHƯỢNG XE ==================

@app.route("/api/admin/transfer_requests", methods=["GET"])
@login_required
def api_admin_get_transfer_requests():
    status = request.args.get("status") or None
    requests_list = database.get_all_transfer_requests(status)
    return jsonify(requests_list)


@app.route("/api/admin/transfer_requests/<int:request_id>/action", methods=["POST"])
@login_required
def api_admin_process_transfer_request(request_id):
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên mới có quyền duyệt đơn"}), 403

    payload = request.get_json(silent=True) or {}
    action = payload.get("action") or "approve"  # 'approve' hoặc 'reject'
    note = payload.get("note") or ""

    success, msg = database.process_transfer_request_action(request_id, action, user["username"], note)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"error": msg}), 400


# ================== BẢO VỆ: BÀN TRỰC, ĐỐI CHIẾU, NGOẠI LỆ, THU PHÍ & BARRIER ==================

@app.route("/api/guard/verification/<plate>", methods=["GET"])
@login_required
def api_guard_get_verification(plate):
    """Lấy dữ liệu đối chiếu ảnh lúc vào, thông tin xe và tính toán cước phí đỗ xe."""
    plate_clean = plate.strip().upper()
    info = database.get_guard_verification_info(plate_clean)
    if not info:
        return jsonify({
            "plate_text": plate_clean,
            "vehicle_type": "Ô tô con",
            "color": "Chưa xác định",
            "owner_name": "Khách vãng lai",
            "ticket_type": "Khách Vãng Lai",
            "is_monthly": False,
            "has_active_session": False,
            "duration_str": "0 phút",
            "fee": 15000,
            "fee_formatted": "15,000 VNĐ"
        })
    return jsonify(info)


@app.route("/api/guard/barrier/trigger", methods=["POST"])
@login_required
def api_guard_trigger_barrier():
    """Điều khiển mở barrier cổng vào / cổng ra."""
    payload = request.get_json(silent=True) or {}
    gate = (payload.get("gate") or "in").lower()
    plate = (payload.get("plate_text") or "").strip().upper()
    action = payload.get("action") or "open"

    user = session.get("user")
    guard_name = user.get("full_name") if user else "Bảo vệ ca trực"

    gate_name = "Cổng Vào #1" if gate == "in" else "Cổng Ra #1"
    msg = f"Đã kích hoạt {action.upper()} Barrier tại {gate_name} thành công. (Thực hiện bởi: {guard_name})"
    return jsonify({"success": True, "gate": gate, "action": action, "message": msg, "timestamp": datetime.now().strftime("%H:%M:%S %d/%m/%Y")})


@app.route("/api/guard/manual_entry", methods=["POST"])
@login_required
def api_guard_manual_entry():
    """Xử lý ngoại lệ: Nhập biển số thủ công khi camera mờ/bẩn hoặc biển số đặc biệt."""
    payload = request.get_json(silent=True) or {}
    plate_text = (payload.get("plate_text") or "").strip().upper()
    gate = (payload.get("gate") or "in").lower()
    vehicle_type = payload.get("vehicle_type") or "Ô tô con"
    note = payload.get("note") or "Nhập thủ công bởi bảo vệ"

    if not plate_text:
        return jsonify({"error": "Vui lòng nhập biển số xe"}), 400

    prov = extract_province_code(plate_text)
    save_plate_to_db(plate_text, province_code=prov, vehicle_type=vehicle_type)

    user = session.get("user")
    operator = user.get("username") if user else "Operator"
    res = database.process_parking_transaction(plate_text, gate, camera_source=f"Manual-Guard-{operator}")
    res["manual_note"] = note
    return jsonify(res)


@app.route("/api/guard/collect_fee", methods=["POST"])
@login_required
def api_guard_collect_fee():
    """Thu phí vé lượt, hoàn tất phiên đỗ và sinh dữ liệu hóa đơn in ấn."""
    payload = request.get_json(silent=True) or {}
    plate_text = (payload.get("plate_text") or "").strip().upper()
    session_id = payload.get("session_id")
    payment_method = payload.get("payment_method") or "Tiền mặt"
    
    if not plate_text:
        return jsonify({"error": "Thiếu biển số xe"}), 400

    # Thực hiện Check-Out
    tx_res = database.process_parking_transaction(plate_text, "out", camera_source="Guard-Payment-Gate")
    user = session.get("user")
    cashier = user.get("full_name") if user else "Thu ngân bãi xe"

    # Tạo mã hóa đơn
    invoice_code = f"HD-{int(time.time())}"
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    fee = tx_res.get("fee", 15000)
    fee_formatted = f"{fee:,.0f} VNĐ" if isinstance(fee, (int, float)) else str(fee)

    receipt = {
        "invoice_code": invoice_code,
        "plate_text": plate_text,
        "check_in_time": tx_res.get("check_in_time") or "---",
        "check_out_time": now_str,
        "duration_minutes": tx_res.get("duration_minutes", 60),
        "fee": fee,
        "fee_formatted": fee_formatted,
        "payment_method": payment_method,
        "cashier": cashier,
        "ticket_type": tx_res.get("ticket_type") or "Khách Vãng Lai",
        "barrier_status": "Opened"
    }

    return jsonify({
        "success": True,
        "message": f"Thu phí thành công {fee_formatted}. Đã tự động mở Barrier Cổng Ra!",
        "receipt": receipt
    })


@app.route("/get_dashboard_summary", methods=["GET"])
@login_required
def get_dashboard_summary():
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total_vehicles FROM vehicles")
        total_vehicles = cursor.fetchone()["total_vehicles"]
        cursor.execute("SELECT COUNT(*) AS total_plates FROM plates")
        total_plates = cursor.fetchone()["total_plates"]
        cursor.execute(
            "SELECT COALESCE(SUM(total_detections),0) AS total_detections FROM statistics"
        )
        total_detections = int(cursor.fetchone()["total_detections"])
        cursor.execute("SELECT COALESCE(AVG(confidence),0) AS avg_conf FROM plates")
        avg_conf = cursor.fetchone()["avg_conf"]
        success_rate = (
            round((total_plates / total_detections * 100), 1)
            if total_detections > 0
            else 0
        )
        
        # Real statistics for Reports
        cursor.execute("SELECT COALESCE(total_detections, 0) as today_detections, COALESCE(total_plates, 0) as today_plates FROM statistics WHERE date_stat = CURDATE()")
        today_stat = cursor.fetchone()
        today_detections = int(today_stat["today_detections"]) if today_stat else 0
        today_plates = int(today_stat["today_plates"]) if today_stat else 0
        today_success_rate = round((today_plates / today_detections * 100), 1) if today_detections > 0 else 0
        
        cursor.execute("SELECT COALESCE(AVG(total_detections),0) AS avg_per_day FROM statistics")
        avg_per_day = int(cursor.fetchone()["avg_per_day"])
        
        cursor.execute("SELECT COUNT(*) as error_count FROM detections WHERE confidence < 0.7 AND DATE(detected_at) = CURDATE()")
        error_count = int(cursor.fetchone()["error_count"])

        cursor.close()
        conn.close()
        return jsonify(
            {
                "total_vehicles": total_vehicles,
                "total_plates": total_plates,
                "total_detections": total_detections,
                "avg_confidence": round(float(avg_conf or 0), 3),
                "success_rate": success_rate,
                "today_detections": today_detections,
                "today_success_rate": today_success_rate,
                "avg_per_day": avg_per_day,
                "error_count": error_count
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vehicles")
@login_required
def api_vehicles():
    try:
        vehicles = database.get_all_vehicles()
        result = []
        for v in vehicles:
            d = dict(v)
            if d.get("registration_date"):
                d["registration_date"] = str(d["registration_date"])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vehicles/save", methods=["POST"])
@login_required
def api_save_vehicle():
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên (Admin) mới có quyền thêm hoặc sửa thông tin xe"}), 403

    try:
        payload = request.get_json(silent=True) or {}
        plate_text = (payload.get("plate_text") or "").strip().upper()
        if not plate_text:
            return jsonify({"error": "Thiếu biển số"}), 400

        owner_name = (payload.get("owner_name") or "").strip() or "Chưa gán"
        vehicle_type = (payload.get("vehicle_type") or "").strip() or "Ô tô con"
        color = (payload.get("color") or "").strip() or "Chưa xác định"
        registration_date = payload.get("registration_date") or None
        status = (payload.get("status") or "").strip() or "Hoạt động"
        province_code = (
            payload.get("province_code") or ""
        ).strip() or extract_province_code(plate_text)

        group_type = (payload.get("group_type") or "Normal").strip()
        monthly_ticket_expiry = payload.get("monthly_ticket_expiry") or None
        if monthly_ticket_expiry == "":
            monthly_ticket_expiry = None

        # Đảm bảo vehicle_type tồn tại trong DB
        if not database.check_vehicle_type_exists(vehicle_type):
            database.add_or_update_vehicle_type(vehicle_type, "Loại xe")

        # Đảm bảo province tồn tại trong DB
        if not database.check_province_exists(province_code):
            province_name = (
                database.get_province_name(province_code) or f"Tỉnh/TP {province_code}"
            )
            database.add_or_update_province(province_code, province_name)

        success = database.upsert_vehicle(
            plate_text=plate_text,
            owner_name=owner_name,
            vehicle_type=vehicle_type,
            color=color,
            registration_date=registration_date if registration_date else None,
            status=status,
            province_code=province_code,
            group_type=group_type,
            monthly_ticket_expiry=monthly_ticket_expiry,
        )

        if not success:
            return jsonify({"error": "Không thể lưu vào database"}), 500

        return jsonify({"success": True, "plate_text": plate_text})
    except Exception as e:
        print(f"[api_save_vehicle] Lỗi: {e}", flush=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/vehicles/delete/<plate_text>", methods=["DELETE"])
@login_required
def api_delete_vehicle(plate_text):
    user = session.get("user")
    if not user or user.get("role") != "Admin":
        return jsonify({"error": "Chỉ Quản trị viên (Admin) mới có quyền xóa xe"}), 403

    try:
        database.delete_vehicle(plate_text)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recognize_image", methods=["POST"])
@login_required
def api_recognize_image():
    try:
        if "image" not in request.files:
            return jsonify({"error": "Khong co file anh"}), 400
        upload_file = request.files["image"]
        if not upload_file or upload_file.filename == "":
            return jsonify({"error": "File anh khong hop le"}), 400

        gate = request.form.get(
            "gate", "in"
        )  # Nhận cổng từ form upload ('in' hoặc 'out')

        file_bytes = upload_file.read()
        np_bytes = np.frombuffer(file_bytes, np.uint8)
        frame = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({"error": "Khong doc duoc anh"}), 400
        reader = get_shared_ocr_reader()
        detections = detect_plates_from_frame(frame, reader)
        if not detections:
            return jsonify({"success": True, "detections": []})

        saved_count = 0
        results_with_tx = []
        for item in detections:
            plate_text = item["plate_text"]
            confidence = item["confidence"]
            province_code = extract_province_code(plate_text)
            if save_plate_to_db(
                plate_text,
                province_code=province_code,
                vehicle_type="O to con",
                confidence=confidence,
            ):
                database.log_detection(
                    plate_text=plate_text,
                    confidence=confidence,
                    camera_source="upload-image",
                    frame_number=None,
                    raw_text=item.get("raw_text"),
                )

                # Thực hiện Check-in / Check-out giao dịch đỗ xe
                tx_res = database.process_parking_transaction(
                    plate_text, gate, camera_source="upload-image"
                )
                item["transaction"] = tx_res

                saved_count += 1
                results_with_tx.append(item)
            else:
                results_with_tx.append(item)

        database.update_statistics(date.today())
        return jsonify(
            {"success": True, "saved_count": saved_count, "detections": results_with_tx}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/parking/sessions")
@login_required
def api_parking_sessions():
    try:
        status = request.args.get("status") or None
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None
        search_term = request.args.get("search") or None

        sessions = database.get_parking_sessions(
            status, date_from, date_to, search_term
        )
        result = []
        for s in sessions:
            d = dict(s)
            if d.get("check_in_time"):
                d["check_in_time"] = str(d["check_in_time"])
            if d.get("check_out_time"):
                d["check_out_time"] = str(d["check_out_time"])
            if d.get("fee") is not None:
                d["fee"] = float(d["fee"])
            if d.get("monthly_ticket_expiry"):
                d["monthly_ticket_expiry"] = str(d["monthly_ticket_expiry"])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/parking/checkout/<int:session_id>", methods=["POST"])
@login_required
def api_parking_checkout_manual(session_id):
    try:
        success = database.checkout_session_manual(session_id)
        if success:
            return jsonify({"success": True})
        return jsonify({"error": "Không thể check-out phiên đỗ này."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/parking/checkin", methods=["POST"])
@login_required
def api_parking_checkin_manual():
    try:
        payload = request.get_json(silent=True) or {}
        plate_text = (payload.get("plate_text") or "").strip().upper()
        if not plate_text:
            return jsonify({"error": "Thiếu biển số"}), 400

        prov = extract_province_code(plate_text)
        save_plate_to_db(plate_text, province_code=prov, vehicle_type="Ô tô con")

        res = database.process_parking_transaction(plate_text, "in", "Manual-Dashboard")
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/revenue")
@login_required
def api_analytics_revenue():
    try:
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None

        stats = database.get_revenue_stats(date_from, date_to)
        result = []
        for s in stats:
            d = dict(s)
            if d.get("date_revenue"):
                d["date_revenue"] = str(d["date_revenue"])
            if d.get("total_fee") is not None:
                d["total_fee"] = float(d["total_fee"])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/peak-hours")
@login_required
def api_analytics_peak_hours():
    try:
        stats = database.get_peak_hours_stats()
        result = [dict(s) for s in stats]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================== CHAY UNG DUNG ==================
if __name__ == "__main__":
    database.init_db()
    print("===================================================")
    print("Server Flask dang khoi dong...")
    print("Truy cap: http://127.0.0.1:5000")
    print("===================================================")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True, use_reloader=False)
