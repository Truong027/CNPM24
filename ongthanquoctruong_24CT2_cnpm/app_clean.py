import cv2
# import easyocr  # Replaced with CRNN-CTC model
import re

# Import new OCR model
from plate_ocr_integration import get_ocr_model, read_plate_ocr_crnn
import time
import numpy as np
from ultralytics import YOLO
from collections import Counter
import os
import torch
from PIL import Image
import database  # Import module CSDL - bÃ¢y giá» dÃ¹ng MySQL
from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for, make_response
import csv, io
from functools import wraps
from datetime import date
from threading import Lock, Thread
from queue import Queue, Empty

# Pillow 10 removed Image.ANTIALIAS, but easyocr 1.7.0 still references it.
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# ================== KHá»žI Táº O FLASK ==================
print("ðŸš€ [APP START] app.py is loading...", flush=True)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY', 'dev-secret-change-me')
print("ðŸš€ [APP START] Flask app created", flush=True)

OCR_READER_CACHE = None
OCR_READER_LOCK = Lock()
OCR_INFER_LOCK = Lock()
MODEL_TRACK_LOCK = Lock()
TRACK_FRAME_SIZE = (640, 480)

def get_shared_ocr_reader():
    """Láº¥y EasyOCR Reader dÃ¹ng chung cho cÃ¡c tÃ¡c vá»¥ request (nháº­n diá»‡n áº£nh)."""
    global OCR_READER_CACHE
    if OCR_READER_CACHE is not None:
        return OCR_READER_CACHE

    with OCR_READER_LOCK:
        if OCR_READER_CACHE is None:
            print("âŒ› [OCR] Äang khá»Ÿi táº¡o shared EasyOCR reader...", flush=True)
            # Cáº¢I TIáº¾N 1: Bá» 'vi', chá»‰ dÃ¹ng 'en' Ä‘á»ƒ trÃ¡nh lá»—i áº£o giÃ¡c dáº¥u tiáº¿ng Viá»‡t
            OCR_READER_CACHE = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
            print("âœ… [OCR] Shared EasyOCR reader Ä‘Ã£ sáºµn sÃ ng.", flush=True)
    return OCR_READER_CACHE

def login_required(view_func):
    """YÃªu cáº§u Ä‘Äƒng nháº­p cho route."""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if session.get('user'):
            return view_func(*args, **kwargs)

        if request.path.startswith('/api/') or request.path.startswith('/get_'):
            return jsonify({"error": "Unauthorized"}), 401

        return redirect(url_for('login'))
    return wrapped_view

# ================== KHá»žI Táº O MYSQL DATABASE ==================
print("âŒ› Äang khá»Ÿi táº¡o cÆ¡ sá»Ÿ dá»¯ liá»‡u MySQL...")
database.init_db()
print("âœ… MySQL Database Ä‘Ã£ sáºµn sÃ ng.")

# ================== KIá»‚M TRA GPU ==================
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"ðŸ’» Thiáº¿t bá»‹ tÃ­nh toÃ¡n: {device}")
if device == 'cuda':
    print("âœ… GPU kháº£ dá»¥ng:", torch.cuda.get_device_name(0))
else:
    print("âš ï¸ GPU khÃ´ng kháº£ dá»¥ng, sáº½ cháº¡y trÃªn CPU.")

# ================== Cáº¤U HÃŒNH & KHá»žI Táº O ==================
MODEL_PATH = "runs/detect/train/weights/best.pt"

# --- CÃC NGUá»’N CAMERA ---
WEBCAM_SOURCE = 0
PHONE_CAMERA_URL = "http://172.16.128.106:8080/video"  # << THAY Äá»ŠA CHá»ˆ IP Cá»¦A Báº N
# ------------------------------

if not os.path.exists(MODEL_PATH):
    print(f"âŒ KhÃ´ng tÃ¬m tháº¥y file mÃ´ hÃ¬nh táº¡i Ä‘Æ°á»ng dáº«n: {MODEL_PATH}")
    exit()

try:
    print(f"âŒ› Äang táº£i mÃ´ hÃ¬nh YOLO tá»«: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)
    print("âœ… Táº£i mÃ´ hÃ¬nh YOLOv8 thÃ nh cÃ´ng.")

    # ===== HÃ m khá»Ÿi táº¡o webcam an toÃ n =====
    def init_webcam(camera_index=0):
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            print(f"âœ… Webcam (index {camera_index}) má»Ÿ thÃ nh cÃ´ng.")
            return cap
        cap.release()
        print(f"âš ï¸ Thá»­ backend DirectShow cho webcam {camera_index}...")
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(f"âœ… Webcam (index {camera_index}) má»Ÿ thÃ nh cÃ´ng vá»›i DirectShow.")
            return cap
        print(f"âŒ KhÃ´ng thá»ƒ má»Ÿ webcam vá»›i index {camera_index}.")
        return None

except Exception as e:
    print(f"âŒ Lá»–I KHá»žI Táº O Há»† THá»NG: {e}")
    exit()

# ================== CÃC HÃ€M Xá»¬ LÃ ==================

# â”€â”€ Preprocess nhanh: resize cá»‘ Ä‘á»‹nh + CLAHE + Otsu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def preprocess_plate(plate_image):
    """Preprocess cÆ¡ báº£n dÃ¹ng cho static upload (nhiá»u variant)."""
    if plate_image is None or plate_image.size == 0:
        return None
    height, width = plate_image.shape[:2]
    scale = max(2.0, 100.0 / height) if height > 0 else 2.0
    enlarged = cv2.resize(plate_image, None, fx=scale, fy=scale,
                          interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    return blurred


def preprocess_plate_fast(plate_image):
    """
    Preprocess nhanh cho video stream:
    - Resize lÃªn chiá»u cao cá»‘ Ä‘á»‹nh 48px (Ä‘á»§ cho OCR, khÃ´ng quÃ¡ lá»›n)
    - Grayscale + CLAHE + Otsu  â†’ 1 áº£nh sáº¡ch duy nháº¥t
    KhÃ´ng táº¡o nhiá»u variant, khÃ´ng sharpen náº·ng.
    """
    if plate_image is None or plate_image.size == 0:
        return None
    h, w = plate_image.shape[:2]
    if h == 0 or w == 0:
        return None
    # Resize lÃªn Ä‘Ãºng 48px chiá»u cao, giá»¯ tá»‰ lá»‡
    target_h = 48
    scale = target_h / h
    new_w = max(int(w * scale), 1)
    resized = cv2.resize(plate_image, (new_w, target_h),
                         interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    enhanced = clahe.apply(gray)
    _, binary = cv2.threshold(enhanced, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def preprocess_plate_variants(plate_image):
    """Táº¡o nhiá»u biáº¿n thá»ƒ áº£nh Ä‘á»ƒ tÄƒng Ä‘á»™ chÃ­nh xÃ¡c OCR (dÃ¹ng cho upload)."""
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
            base, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 2)
        variants.append(adaptive)
    except cv2.error:
        pass
    try:
        _, otsu = cv2.threshold(base, 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(otsu)
    except cv2.error:
        pass
    return variants

VALID_VN_PROVINCE_CODES = {
    '11', '12', '14', '15', '16', '17', '18', '19',
    '20', '21', '22', '23', '24', '25', '26', '27', '28',
    '29', '30', '31', '32', '33', '34', '35', '36', '37', '38',
    '40', '41', '43', '47', '48', '49',
    '50', '51', '52', '53', '54', '55', '56', '57', '58', '59',
    '60', '61', '62', '63', '64', '65', '66', '67', '68', '69',
    '70', '71', '72', '73', '74', '75', '76', '77', '78', '79',
    '80', '81', '82', '83', '84', '85', '86',
    '88', '89', '90', '92', '93', '94', '95', '97', '98', '99'
}

DIGIT_MAP = {
    # Chu cai bi OCR nham thanh so - chi giu cac mapping an toan
    'O': '0', 'Q': '0',
    'I': '1', 'L': '1', '|': '1',
    'S': '5',
    'B': '8',
    # KHONG map D->0, Z->2, G->6, T->7 vi D/Z/G/T la chu hop le trong bien so VN
}

LETTER_MAP = {
    # So bi OCR nham thanh chu - chi giu mapping an toan
    '0': 'O',
    '1': 'I',
    '5': 'S',
    '8': 'B',
}

# Cap ky tu de nham lan khi OCR doc phan so
DIGIT_CONFUSABLE = {
    '8': ['3', '6'],
    '3': ['8'],
    '0': ['6'],
    '6': ['0'],
    '1': ['7'],
    '7': ['1'],
    '9': ['4'],
    '4': ['9'],
}


def _to_digit(value):
    return ''.join(DIGIT_MAP.get(ch, ch) for ch in value)

def _to_letter(value):
    return ''.join(LETTER_MAP.get(ch, ch) for ch in value)

def is_valid_vn_plate(plate_text):
    if not plate_text:
        return False
    # Bien moi: 2so + 1-2chu + '-' + 3so + '.' + 2so  (vd 43A-272.08)
    match_new = re.match(r'^(\d{2})([A-Z]{1,2})-(\d{3})\.(\d{2})$', plate_text)
    # Bien cu:  2so + 1-2chu + '-' + 2so  + '.' + 2so  (vd 43A-27.08)
    match_old = re.match(r'^(\d{2})([A-Z]{1,2})-(\d{2})\.(\d{2})$', plate_text)
    match = match_new or match_old
    if not match:
        return False
    province = match.group(1)
    series   = match.group(2)
    if province not in VALID_VN_PROVINCE_CODES:
        return False
    # Series chi gom chu cai trong bo A-Z (khong co so)
    if not re.match(r'^[A-Z]{1,2}$', series):
        return False
    return True


def normalize_plate_text(text):
    """
    Chuan hoa chuoi OCR thanh dinh dang bien so VN: XXY-NNN.NN hoac XXY-NN.NN
    - 2 ky tu dau (tinh): ep ve so
    - 1-2 ky tu tiep (seri): ep ve chu
    - 4-5 ky tu cuoi (so thu tu): ep ve so
    """
    if not text:
        return ""
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    if len(cleaned) < 7:
        return ""

    def force_format(raw_str, series_len, number_len):
        prov = _to_digit(raw_str[:2])
        ser  = _to_letter(raw_str[2:2+series_len])
        nums = _to_digit(raw_str[2+series_len:2+series_len+number_len])
        return prov, ser, nums

    def try_fix_province(prov):
        alts = [prov]
        for i, ch in enumerate(prov):
            if ch in DIGIT_CONFUSABLE:
                for r in DIGIT_CONFUSABLE[ch]:
                    c = prov[:i] + r + prov[i+1:]
                    if c not in alts:
                        alts.append(c)
        return alts

    candidates = []
    for series_len in (1, 2):
        for number_len in (5, 4):
            total_len = 2 + series_len + number_len
            if len(cleaned) < total_len:
                continue
            for start in range(len(cleaned) - total_len + 1):
                token = cleaned[start:start + total_len]
                prov, ser, nums = force_format(token, series_len, number_len)
                if len(prov) != 2 or len(ser) != series_len or len(nums) != number_len:
                    continue
                # Series phai la chu cai hop le
                if not re.match(r'^[A-Z]{1,2}$', ser):
                    continue
                for fix_idx, prov_try in enumerate(try_fix_province(prov)):
                    if prov_try not in VALID_VN_PROVINCE_CODES:
                        continue
                    if number_len == 5:
                        formatted = f"{prov_try}{ser}-{nums[:3]}.{nums[3:]}"
                    else:
                        formatted = f"{prov_try}{ser}-{nums[:2]}.{nums[2:]}"
                    score = 5  # ma tinh hop le
                    score += 2 if number_len == 5 else 1
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
    prov_crop = plate_image_gray[:, :int(w * 0.32)]
    if prov_crop.size == 0:
        return None
    big = cv2.resize(prov_crop, None, fx=4.0, fy=4.0, interpolation=cv2.INTER_CUBIC)
    _, otsu = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    votes = []
    for img in [otsu, cv2.bitwise_not(otsu)]:
        try:
            with OCR_INFER_LOCK:
                res = reader.readtext(img, allowlist='0123456789',
                                      detail=0, paragraph=True)
            digits = re.sub(r'[^0-9]', '', ''.join(res))
            if len(digits) >= 2:
                votes.append(digits[:2])
        except Exception:
            pass
    if not votes:
        return None
    best = Counter(votes).most_common(1)[0][0]
    return best if best in VALID_VN_PROVINCE_CODES else None


def read_plate_text_with_confidence(plate_crop, reader):
    """
    Doc bien so tu crop anh.
    Fast path: 1 OCR call (preprocess_plate_fast) + 1 retry dao mau.
    Slow path: nhieu variants neu fast path that bai.
    """
    if plate_crop is None or plate_crop.size == 0:
        return "", "", 0.0

    ALLOW = '0123456789ABCDEFGHKLMNPRSTUVXYZ'
    OCR_KWARGS = dict(
        allowlist=ALLOW, detail=1, paragraph=False,
        text_threshold=0.5, width_ths=0.9, height_ths=0.9, slope_ths=0.3,
    )

    def _run_ocr(img):
        try:
            with OCR_INFER_LOCK:
                result = reader.readtext(img, **OCR_KWARGS)
        except Exception:
            return None
        if not result:
            return None
        result.sort(key=lambda x: (x[0][0][1] + x[0][2][1]) / 2)
        parts, confs = [], []
        for item in result:
            t = item[1].strip()
            if t:
                parts.append(t)
                confs.append(float(item[2]))
        raw = "".join(parts).replace(" ", "")
        avg_conf = sum(confs) / len(confs) if confs else 0.0
        text = normalize_plate_text(raw)
        if not text:
            return None
        score = min(1.0, avg_conf + (0.15 if is_valid_vn_plate(text) else 0.0))
        return text, raw, score

    # Fast path
    fast_img = preprocess_plate_fast(plate_crop)
    if fast_img is not None:
        hit = _run_ocr(fast_img)
        if hit and is_valid_vn_plate(hit[0]):
            return hit
        hit2 = _run_ocr(cv2.bitwise_not(fast_img))
        if hit2 and is_valid_vn_plate(hit2[0]):
            return hit2

    # Slow path
    variants = preprocess_plate_variants(plate_crop)
    if not variants:
        return "", "", 0.0
    all_results = [h for v in variants for h in [_run_ocr(v)] if h]
    if not all_results:
        return "", "", 0.0
    vote_count = Counter(r[0] for r in all_results)
    top = max(vote_count.values())
    candidates = sorted(
        [r for r in all_results if vote_count[r[0]] == top],
        key=lambda r: r[2], reverse=True
    )
    best_text, best_raw, best_score = candidates[0]
    unique_provs = {r[0][:2] for r in all_results if len(r[0]) >= 2}
    if len(unique_provs) > 1:
        confirmed = _ocr_province_crop(preprocess_plate(plate_crop), reader)
        if confirmed and confirmed != best_text[:2]:
            corrected = confirmed + best_text[2:]
            if is_valid_vn_plate(corrected):
                best_text = corrected
    return best_text, best_raw, best_score


def extract_province_code(plate_text):
    if not plate_text:
        return '51'
    m = re.match(r'^(\d{2})', plate_text)
    return m.group(1) if m else '51'


def detect_plates_from_frame(frame, reader):
    """Nhan dien bien so tu anh upload."""
    detections = []
    if frame is None or frame.size == 0:
        return detections
    h, w = frame.shape[:2]
    if max(h, w) < 640:
        scale = 640 / max(h, w)
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    elif max(h, w) > 1280:
        scale = 1280 / max(h, w)
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    h, w = frame.shape[:2]
    all_boxes = []
    for imgsz in [640, 1280]:
        try:
            results = model.predict(frame, imgsz=imgsz, conf=0.25, device=device, verbose=False)
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
            detections.append({'plate_text': plate_text, 'raw_text': raw_text,
                                'confidence': ocr_conf, 'box': [0, 0, w, h]})
        return detections
    for (x1, y1, x2, y2), box_conf in all_boxes:
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        plate_text, raw_text, ocr_conf = read_plate_text_with_confidence(crop, reader)
        if not plate_text or not is_valid_vn_plate(plate_text):
            continue
        detections.append({'plate_text': plate_text, 'raw_text': raw_text,
                            'confidence': min(1.0, (box_conf + ocr_conf) / 2),
                            'box': [int(x1), int(y1), int(x2), int(y2)]})
    dedup = {}
    for item in detections:
        k = item['plate_text']
        if k not in dedup or item['confidence'] > dedup[k]['confidence']:
            dedup[k] = item
    return list(dedup.values())


def save_plate_to_db(plate_text, province_code='51', vehicle_type='O to con', confidence=0.95):
    conn = None
    try:
        if not province_code:
            province_code = extract_province_code(plate_text)
        if not database.check_province_exists(province_code):
            province_name = database.get_province_name(province_code) or f"Tinh/TP {province_code}"
            database.add_or_update_province(province_code, province_name, region="Nam Bo")
        if not database.check_vehicle_type_exists(vehicle_type):
            database.add_or_update_vehicle_type(vehicle_type, "Loai xe chua xac dinh")
        conn = database.get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO plates (plate_text, province_code, vehicle_type, confidence)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                detection_count = detection_count + 1,
                province_code   = VALUES(province_code),
                vehicle_type    = VALUES(vehicle_type),
                confidence      = GREATEST(confidence, VALUES(confidence)),
                timestamp       = CURRENT_TIMESTAMP
        """, (plate_text, province_code, vehicle_type, confidence))
        conn.commit()
        database.upsert_vehicle(plate_text=plate_text, owner_name='Chua gan',
                                vehicle_type=vehicle_type, color='Chua xac dinh',
                                registration_date=None, status='Hoat dong',
                                province_code=province_code)
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
OCR_INTERVAL        = 0.8
VOTING_THRESHOLD    = 2
VOTING_BUFFER_SIZE  = 4
STALE_TRACK_SECONDS = 3.0
DUPLICATE_COOLDOWN  = 4
FAST_SAVE_OCR_CONF  = 0.80

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
                print(f"[OCR] Track {track_id}: '{raw}' -> '{text}' ({conf:.2f})", flush=True)
        except Exception as exc:
            print(f"[OCR] Worker loi track {track_id}: {exc}", flush=True)
        finally:
            ocr_queue.task_done()


def gen_frames(camera_source):
    PLATE_TRACKER       = {}
    RECENT_SAVED_PLATES = {}
    LAST_OCR_ENQUEUE    = 0.0
    FRAME_COUNT         = 0
    ocr_results         = {}
    source_name = str(camera_source)

    try:
        reader = get_shared_ocr_reader()
    except Exception as exc:
        print(f"[{source_name}] Khong lay duoc OCR reader: {exc}", flush=True)
        return

    ocr_queue  = Queue(maxsize=2)
    ocr_thread = Thread(target=_ocr_worker,
                        args=(ocr_queue, ocr_results, reader, source_name),
                        daemon=True)
    ocr_thread.start()

    cap = None
    try:
        if isinstance(camera_source, int):
            cap = init_webcam(camera_source)
        else:
            cap = cv2.VideoCapture(camera_source)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if cap is None or not cap.isOpened():
            ocr_queue.put(None)
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 75]

        while True:
            ret, frame = cap.read()
            if not ret:
                if isinstance(camera_source, str):
                    time.sleep(3)
                    cap.release()
                    cap = cv2.VideoCapture(camera_source)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    continue
                else:
                    break

            FRAME_COUNT += 1
            frame = cv2.resize(frame, TRACK_FRAME_SIZE, interpolation=cv2.INTER_AREA)
            current_time = time.time()

            try:
                with MODEL_TRACK_LOCK:
                    results = model.track(frame, persist=True, imgsz=320, conf=0.35,
                                          device=device, verbose=False,
                                          tracker="bytetrack.yaml")
            except Exception:
                try:
                    with MODEL_TRACK_LOCK:
                        results = model.predict(frame, imgsz=320, conf=0.35,
                                                device=device, verbose=False)
                except Exception:
                    ret2, buf = cv2.imencode('.jpg', frame, encode_params)
                    if ret2:
                        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
                               + buf.tobytes() + b'\r\n')
                    continue


            current_track_ids = set()
            boxes_for_drawing = []
            boxes_obj = results[0].boxes
            has_ids   = boxes_obj is not None and boxes_obj.id is not None

            if boxes_obj is not None and len(boxes_obj) > 0:
                xyxy   = boxes_obj.xyxy.cpu().numpy().astype(int)
                confs_ = boxes_obj.conf.cpu().numpy()
                ids_   = (boxes_obj.id.cpu().numpy().astype(int)
                          if has_ids else range(len(xyxy)))
                for box, conf_, tid in zip(xyxy, confs_, ids_):
                    x1, y1, x2, y2 = box
                    current_track_ids.add(tid)
                    if tid not in PLATE_TRACKER:
                        PLATE_TRACKER[tid] = {'buffer': [], 'stable_text': '',
                                              'confirmed_text': '',
                                              'last_seen': current_time,
                                              'box': (x1, y1, x2, y2)}
                    else:
                        PLATE_TRACKER[tid]['last_seen'] = current_time
                        PLATE_TRACKER[tid]['box']       = (x1, y1, x2, y2)
                    boxes_for_drawing.append({'box': (x1, y1, x2, y2),
                                              'conf': conf_, 'track_id': tid})

            if (current_time - LAST_OCR_ENQUEUE) >= OCR_INTERVAL and not ocr_queue.full():
                for item in boxes_for_drawing:
                    tid = item['track_id']
                    x1, y1, x2, y2 = item['box']
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
                tracker['buffer'].append(text)
                while len(tracker['buffer']) > VOTING_BUFFER_SIZE:
                    tracker['buffer'].pop(0)
                tally = Counter(tracker['buffer'])
                best  = tally.most_common(1)[0]
                tracker['stable_text'] = best[0]
                required = 1 if conf >= FAST_SAVE_OCR_CONF else VOTING_THRESHOLD
                if best[1] >= required and is_valid_vn_plate(best[0]):
                    tracker['confirmed_text'] = best[0]
                    last_saved = RECENT_SAVED_PLATES.get(best[0], 0)
                    if (current_time - last_saved) >= DUPLICATE_COOLDOWN:
                        prov = extract_province_code(best[0])
                        if save_plate_to_db(best[0], province_code=prov, vehicle_type='O to con'):
                            database.log_detection(plate_text=best[0], confidence=max(conf, 0.6),
                                                   camera_source=source_name,
                                                   frame_number=FRAME_COUNT, raw_text=raw or best[0])
                            
                            # Xử lý Giao dịch Đỗ xe (Check-In / Check-Out)
                            gate_type = 'in' if (source_name == '0' or 'webcam' in source_name.lower()) else 'out'
                            tx_res = database.process_parking_transaction(best[0], gate_type, camera_source=source_name)
                            print(f"[{source_name}] Giao dịch ({gate_type}): {best[0]} -> {tx_res}", flush=True)
                            
                            database.update_statistics(date.today())
                            print(f"[{source_name}] Luu: {best[0]}", flush=True)
                        RECENT_SAVED_PLATES[best[0]] = current_time
                del ocr_results[tid]

            for tid in [t for t, d in list(PLATE_TRACKER.items())
                        if (current_time - d['last_seen']) > STALE_TRACK_SECONDS
                        and t not in current_track_ids]:
                del PLATE_TRACKER[tid]
            for p in [k for k, v in list(RECENT_SAVED_PLATES.items())
                      if (current_time - v) > DUPLICATE_COOLDOWN]:
                del RECENT_SAVED_PLATES[p]

            for item in boxes_for_drawing:
                x1, y1, x2, y2 = item['box']
                tid       = item['track_id']
                confirmed = PLATE_TRACKER.get(tid, {}).get('confirmed_text', '')
                color = (0, 255, 0) if confirmed else (0, 200, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                if confirmed:
                    ts, _ = cv2.getTextSize(confirmed, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
                    tx, ty = x1, max(y1 - 12, 20)
                    cv2.rectangle(frame, (tx-2, ty-ts[1]-4), (tx+ts[0]+4, ty+4), (0,0,0), -1)
                    cv2.putText(frame, confirmed, (tx, ty),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2, cv2.LINE_AA)

            ret2, buffer = cv2.imencode('.jpg', frame, encode_params)
            if ret2:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
                       + buffer.tobytes() + b'\r\n')

    except GeneratorExit:
        pass
    except Exception as exc:
        print(f"[{source_name}] Loi gen_frames: {exc}", flush=True)
    finally:
        ocr_queue.put(None)
        if cap:
            cap.release()


# ================== ROUTES ==================
@app.route('/login')
def login():
    if session.get('user'):
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    payload  = request.get_json(silent=True) or {}
    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''
    if not username or not password:
        return jsonify({"error": "Thieu thong tin dang nhap"}), 400
    user = database.authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Sai tai khoan hoac mat khau"}), 401
    session['user'] = {'id': user['id'], 'username': user['username'],
                       'full_name': user.get('full_name') or user['username'],
                       'email': user.get('email') or '', 'role': user.get('role') or 'User'}
    return jsonify({"success": True, "user": session['user']})

@app.route('/register')
def register():
    if session.get('user'):
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    payload    = request.get_json(silent=True) or {}
    username   = (payload.get('username') or '').strip()
    password   = payload.get('password') or ''
    confirm    = payload.get('confirm_password') or ''
    full_name  = (payload.get('full_name') or '').strip()
    email      = (payload.get('email') or '').strip()

    if not username or not password or not full_name:
        return jsonify({"error": "Vui lòng điền đầy đủ thông tin bắt buộc"}), 400
    if len(username) < 3:
        return jsonify({"error": "Tên tài khoản phải có ít nhất 3 ký tự"}), 400
    if len(password) < 6:
        return jsonify({"error": "Mật khẩu phải có ít nhất 6 ký tự"}), 400
    if password != confirm:
        return jsonify({"error": "Mật khẩu xác nhận không khớp"}), 400

    new_user, error = database.register_user(username, password, full_name, email, role='User')
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Đăng ký thành công! Vui lòng đăng nhập."})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/api/session')
def api_session():
    user = session.get('user')
    if not user:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "user": user})

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/video_feed_webcam')
@login_required
def video_feed_webcam():
    return Response(gen_frames(WEBCAM_SOURCE),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_phone')
@login_required
def video_feed_phone():
    return Response(gen_frames(PHONE_CAMERA_URL),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_plates')
@login_required
def get_plates():
    try:
        plates = database.get_all_plates_with_details()
        result = []
        for p in plates:
            d = dict(p)
            if d.get('timestamp'):
                d['timestamp'] = str(d['timestamp'])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_plate_details/<plate_text>')
@login_required
def get_plate_details(plate_text):
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, pr.name as province_name
            FROM plates p
            LEFT JOIN provinces pr ON p.province_code = pr.code
            WHERE p.plate_text = %s
        """, (plate_text,))
        row = cursor.fetchone()
        cursor.close(); conn.close()
        if not row:
            return jsonify({"error": "Khong tim thay bien so"}), 404
        d = dict(row)
        if d.get('timestamp'):
            d['timestamp'] = str(d['timestamp'])
        return jsonify(d)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_plate_detections/<plate_text>')
@login_required
def get_plate_detections(plate_text):
    try:
        detections = database.get_plate_detections(plate_text)
        result = []
        for det in detections:
            d = dict(det)
            if d.get('detected_at'):
                d['detected_at'] = str(d['detected_at'])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_statistics')
@login_required
def get_statistics():
    try:
        date_from = request.args.get('date_from') or None
        date_to   = request.args.get('date_to')   or None
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        if date_from and date_to:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat BETWEEN %s AND %s ORDER BY date_stat DESC",
                (date_from, date_to)
            )
        elif date_from:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat >= %s ORDER BY date_stat DESC",
                (date_from,)
            )
        elif date_to:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat <= %s ORDER BY date_stat DESC LIMIT 30",
                (date_to,)
            )
        else:
            cursor.execute("SELECT * FROM statistics ORDER BY date_stat DESC LIMIT 30")
        results = cursor.fetchall()
        cursor.close(); conn.close()
        result = []
        for stat in results:
            d = dict(stat)
            if d.get('date_stat'):
                d['date_stat'] = str(d['date_stat'])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/report_export')
@login_required
def api_report_export():
    """Xuất báo cáo CSV theo khoảng thời gian."""
    try:
        date_from = request.args.get('date_from') or None
        date_to   = request.args.get('date_to')   or None
        fmt       = request.args.get('format', 'csv').lower()

        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Không thể kết nối database"}), 500
        cursor = conn.cursor(dictionary=True)

        # Lấy dữ liệu statistics
        if date_from and date_to:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat BETWEEN %s AND %s ORDER BY date_stat ASC",
                (date_from, date_to)
            )
        elif date_from:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat >= %s ORDER BY date_stat ASC",
                (date_from,)
            )
        elif date_to:
            cursor.execute(
                "SELECT * FROM statistics WHERE date_stat <= %s ORDER BY date_stat ASC LIMIT 60",
                (date_to,)
            )
        else:
            cursor.execute("SELECT * FROM statistics ORDER BY date_stat DESC LIMIT 30")

        stats = cursor.fetchall()

        # Lấy top biển số trong khoảng thời gian
        if date_from and date_to:
            cursor.execute("""
                SELECT plate_text, detection_count, confidence, province_code, vehicle_type, timestamp
                FROM plates
                WHERE DATE(timestamp) BETWEEN %s AND %s
                ORDER BY detection_count DESC LIMIT 50
            """, (date_from, date_to))
        else:
            cursor.execute("""
                SELECT plate_text, detection_count, confidence, province_code, vehicle_type, timestamp
                FROM plates ORDER BY timestamp DESC LIMIT 50
            """)
        plates = cursor.fetchall()
        cursor.close(); conn.close()

        output = io.StringIO()
        writer = csv.writer(output)

        # ---- Phần 1: Tiêu đề báo cáo ----
        writer.writerow(['BÁO CÁO HỆ THỐNG NHẬN DIỆN BIỂN SỐ XE'])
        from datetime import datetime
        writer.writerow([f'Xuất lúc: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'])
        if date_from or date_to:
            writer.writerow([f'Khoảng thời gian: {date_from or "---"} đến {date_to or "---"}'])
        writer.writerow([])

        # ---- Phần 2: Thống kê theo ngày ----
        writer.writerow(['THỐNG KÊ THEO NGÀY'])
        writer.writerow(['Ngày', 'Tổng biển số', 'Tổng lượt phát hiện', 'Độ tin cậy TB', 'Biển số phổ biến nhất'])
        for stat in stats:
            writer.writerow([
                stat.get('date_stat', ''),
                stat.get('total_plates', 0),
                stat.get('total_detections', 0),
                f"{float(stat.get('avg_confidence') or 0):.1%}",
                stat.get('top_plate', ''),
            ])

        total_plates_sum = sum(int(s.get('total_plates') or 0) for s in stats)
        total_det_sum    = sum(int(s.get('total_detections') or 0) for s in stats)
        avg_conf_vals    = [float(s.get('avg_confidence') or 0) for s in stats if s.get('avg_confidence')]
        avg_conf_summary = sum(avg_conf_vals) / len(avg_conf_vals) if avg_conf_vals else 0
        writer.writerow(['TỔNG CỘNG', total_plates_sum, total_det_sum, f'{avg_conf_summary:.1%}', ''])
        writer.writerow([])

        # ---- Phần 3: Danh sách biển số ----
        writer.writerow(['DANH SÁCH BIỂN SỐ'])
        writer.writerow(['Biển Số', 'Mã Tỉnh', 'Loại Xe', 'Số Lần Phát Hiện', 'Độ Tin Cậy', 'Thời Gian'])
        for p in plates:
            writer.writerow([
                p.get('plate_text', ''),
                p.get('province_code', ''),
                p.get('vehicle_type', ''),
                p.get('detection_count', 0),
                f"{float(p.get('confidence') or 0):.1%}",
                str(p.get('timestamp', '')),
            ])

        csv_content = '\ufeff' + output.getvalue()  # BOM cho Excel đọc được UTF-8

        # Tạo tên file
        suffix = ''
        if date_from and date_to:
            suffix = f'_{date_from}_den_{date_to}'
        elif date_from:
            suffix = f'_tu_{date_from}'
        filename = f'bao_cao_bien_so{suffix}.csv'

        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_stats_by_province')
@login_required
def get_stats_by_province():
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT pv.code, pv.name,
                   COUNT(pl.id) as total_plates,
                   SUM(pl.detection_count) as total_detections,
                   AVG(pl.confidence) as avg_confidence
            FROM provinces pv
            LEFT JOIN plates pl ON pl.province_code = pv.code
            GROUP BY pv.code, pv.name
            ORDER BY total_detections DESC
        """)
        results = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_stats_by_vehicle_type')
@login_required
def get_stats_by_vehicle_type():
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT vehicle_type, COUNT(*) as total_plates,
                   AVG(confidence) as avg_confidence,
                   MAX(detection_count) as max_detections
            FROM plates WHERE vehicle_type IS NOT NULL
            GROUP BY vehicle_type ORDER BY total_plates DESC
        """)
        results = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_dashboard_summary')
@login_required
def get_dashboard_summary():
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({"error": "Khong the ket noi database"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total_vehicles FROM vehicles")
        total_vehicles = cursor.fetchone()['total_vehicles']
        cursor.execute("SELECT COUNT(*) AS total_plates FROM plates")
        total_plates = cursor.fetchone()['total_plates']
        cursor.execute("SELECT COALESCE(SUM(total_detections),0) AS total_detections FROM statistics")
        total_detections = cursor.fetchone()['total_detections']
        cursor.execute("SELECT COALESCE(AVG(confidence),0) AS avg_conf FROM plates")
        avg_conf = cursor.fetchone()['avg_conf']
        success_rate = round((total_plates / total_detections * 100), 1) if total_detections > 0 else 0
        cursor.close(); conn.close()
        return jsonify({'total_vehicles': total_vehicles, 'total_plates': total_plates,
                        'total_detections': total_detections, 'avg_confidence': round(float(avg_conf or 0), 3),
                        'success_rate': success_rate})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/vehicles')
@login_required
def api_vehicles():
    try:
        vehicles = database.get_all_vehicles()
        result = []
        for v in vehicles:
            d = dict(v)
            if d.get('registration_date'):
                d['registration_date'] = str(d['registration_date'])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicles/save', methods=['POST'])
@login_required
def api_save_vehicle():
    try:
        payload = request.get_json(silent=True) or {}
        plate_text = (payload.get('plate_text') or '').strip().upper()
        if not plate_text:
            return jsonify({"error": "Thiếu biển số"}), 400

        owner_name        = (payload.get('owner_name') or '').strip() or 'Chưa gán'
        vehicle_type      = (payload.get('vehicle_type') or '').strip() or 'Ô tô con'
        color             = (payload.get('color') or '').strip() or 'Chưa xác định'
        registration_date = payload.get('registration_date') or None
        status            = (payload.get('status') or '').strip() or 'Hoạt động'
        province_code     = (payload.get('province_code') or '').strip() or extract_province_code(plate_text)

        group_type            = (payload.get('group_type') or 'Normal').strip()
        monthly_ticket_expiry = payload.get('monthly_ticket_expiry') or None
        if monthly_ticket_expiry == '':
            monthly_ticket_expiry = None

        # Đảm bảo vehicle_type tồn tại trong DB
        if not database.check_vehicle_type_exists(vehicle_type):
            database.add_or_update_vehicle_type(vehicle_type, "Loại xe")

        # Đảm bảo province tồn tại trong DB
        if not database.check_province_exists(province_code):
            province_name = database.get_province_name(province_code) or f"Tỉnh/TP {province_code}"
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
            monthly_ticket_expiry=monthly_ticket_expiry
        )

        if not success:
            return jsonify({"error": "Không thể lưu vào database"}), 500

        return jsonify({"success": True, "plate_text": plate_text})
    except Exception as e:
        print(f"[api_save_vehicle] Lỗi: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicles/delete/<plate_text>', methods=['DELETE'])
@login_required
def api_delete_vehicle(plate_text):
    try:
        database.delete_vehicle(plate_text)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recognize_image', methods=['POST'])
@login_required
def api_recognize_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "Khong co file anh"}), 400
        upload_file = request.files['image']
        if not upload_file or upload_file.filename == '':
            return jsonify({"error": "File anh khong hop le"}), 400
        
        gate = request.form.get('gate', 'in') # Nhận cổng từ form upload ('in' hoặc 'out')
        
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
            plate_text = item['plate_text']
            confidence = item['confidence']
            province_code = extract_province_code(plate_text)
            if save_plate_to_db(plate_text, province_code=province_code,
                                vehicle_type='O to con', confidence=confidence):
                database.log_detection(plate_text=plate_text, confidence=confidence,
                                       camera_source='upload-image', frame_number=None,
                                       raw_text=item.get('raw_text'))
                
                # Thực hiện Check-in / Check-out giao dịch đỗ xe
                tx_res = database.process_parking_transaction(plate_text, gate, camera_source='upload-image')
                item['transaction'] = tx_res
                
                saved_count += 1
                results_with_tx.append(item)
            else:
                results_with_tx.append(item)
                
        database.update_statistics(date.today())
        return jsonify({"success": True, "saved_count": saved_count, "detections": results_with_tx})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/parking/sessions')
@login_required
def api_parking_sessions():
    try:
        status      = request.args.get('status') or None
        date_from   = request.args.get('date_from') or None
        date_to     = request.args.get('date_to') or None
        search_term = request.args.get('search') or None
        
        sessions = database.get_parking_sessions(status, date_from, date_to, search_term)
        result = []
        for s in sessions:
            d = dict(s)
            if d.get('check_in_time'):
                d['check_in_time'] = str(d['check_in_time'])
            if d.get('check_out_time'):
                d['check_out_time'] = str(d['check_out_time'])
            if d.get('fee') is not None:
                d['fee'] = float(d['fee'])
            if d.get('monthly_ticket_expiry'):
                d['monthly_ticket_expiry'] = str(d['monthly_ticket_expiry'])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/parking/checkout/<int:session_id>', methods=['POST'])
@login_required
def api_parking_checkout_manual(session_id):
    try:
        success = database.checkout_session_manual(session_id)
        if success:
            return jsonify({"success": True})
        return jsonify({"error": "Không thể check-out phiên đỗ này."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/parking/checkin', methods=['POST'])
@login_required
def api_parking_checkin_manual():
    try:
        payload = request.get_json(silent=True) or {}
        plate_text = (payload.get('plate_text') or '').strip().upper()
        if not plate_text:
            return jsonify({"error": "Thiếu biển số"}), 400
            
        prov = extract_province_code(plate_text)
        save_plate_to_db(plate_text, province_code=prov, vehicle_type='Ô tô con')
        
        res = database.process_parking_transaction(plate_text, 'in', 'Manual-Dashboard')
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/revenue')
@login_required
def api_analytics_revenue():
    try:
        date_from = request.args.get('date_from') or None
        date_to   = request.args.get('date_to') or None
        
        stats = database.get_revenue_stats(date_from, date_to)
        result = []
        for s in stats:
            d = dict(s)
            if d.get('date_revenue'):
                d['date_revenue'] = str(d['date_revenue'])
            if d.get('total_fee') is not None:
                d['total_fee'] = float(d['total_fee'])
            result.append(d)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/peak-hours')
@login_required
def api_analytics_peak_hours():
    try:
        stats = database.get_peak_hours_stats()
        result = [dict(s) for s in stats]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================== CHAY UNG DUNG ==================
if __name__ == '__main__':
    database.init_db()
    print("===================================================")
    print("Server Flask dang khoi dong...")
    print("Truy cap: http://127.0.0.1:5000")
    print("===================================================")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)
