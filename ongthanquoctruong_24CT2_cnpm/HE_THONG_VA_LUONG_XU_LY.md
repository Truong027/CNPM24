# Äáº¶C Táº¢ KIáº¾N TRÃšC & CÃC LUá»’NG Xá»¬ LÃ Dá»® LIá»†U Cá»¦A Há»† THá»NG
# Há»† THá»NG NHáº¬N DIá»†N BIá»‚N Sá» XE & QUáº¢N LÃ BÃƒI XE THÃ”NG MINH (AI SMART PARKING)

> **MÃ´n há»c**: CÃ´ng nghá»‡ pháº§n má»m (CNPM24)  
> **Lá»›p**: 24CT2  
> **Sinh viÃªn thá»±c hiá»‡n**: Ã”ng ThÃ¢n Quá»‘c TrÆ°á»ng  
> **TrÆ°á»ng**: Äáº¡i há»c Kiáº¿n trÃºc ÄÃ  Náºµng (DAU)  
> **CÃ´ng nghá»‡ Ã¡p dá»¥ng**: Python (Flask) + YOLOv8 + CRNN/EasyOCR + MySQL + HTML5/CSS3/Vanilla JS (SPA)

---

## Má»¤C Lá»¤C CHI TIáº¾T
1. [Tá»•ng Quan Kiáº¿n TrÃºc Äa Táº§ng (Multi-tier Architecture)](#1-tá»•ng-quan-kiáº¿n-trÃºc-Ä‘a-táº§ng)
2. [SÆ¡ Äá»“ DÃ²ng Dá»¯ Liá»‡u Tá»•ng Thá»ƒ (System Architecture Flowchart)](#2-sÆ¡-Ä‘á»“-dÃ²ng-dá»¯-liá»‡u-tá»•ng-thá»ƒ)
3. [Luá»“ng 1: Nháº­n Diá»‡n Biá»ƒn Sá»‘ AI & Tá»± Äá»™ng Check-In / Check-Out Tá»« Camera Live](#3-luá»“ng-1-nháº­n-diá»‡n-biá»ƒn-sá»‘-ai--tá»±-Ä‘á»™ng-check-in--check-out-tá»«-camera-live)
4. [Luá»“ng 2: Nghiá»‡p Vá»¥ BÃ n Trá»±c Báº£o Vá»‡ (Äá»‘i Chiáº¿u Xe Ra, Cáº£nh BÃ¡o An Ninh, TÃ­nh PhÃ­ & Má»Ÿ Barrier)](#4-luá»“ng-2-nghiá»‡p-vá»¥-bÃ n-trá»±c-báº£o-vá»‡)
5. [Luá»“ng 3: Quáº£n LÃ½ TÃ i Khoáº£n NgÆ°á»i DÃ¹ng (Admin, CÆ° DÃ¢n, Báº£o Vá»‡ & Chá»‰nh Sá»­a Dá»¯ Liá»‡u)](#5-luá»“ng-3-quáº£n-lÃ½-tÃ i-khoáº£n-ngÆ°á»i-dÃ¹ng)
6. [Luá»“ng 4: Quáº£n LÃ½ Danh Má»¥c PhÆ°Æ¡ng Tiá»‡n & PhÃ¢n NhÃ³m Blacklist / Whitelist](#6-luá»“ng-4-quáº£n-lÃ½-danh-má»¥c-phÆ°Æ¡ng-tiá»‡n--phÃ¢n-nhÃ³m-blacklist--whitelist)
7. [Luá»“ng 5: ÄÄƒng KÃ½ & Quáº£n LÃ½ VÃ© ThÃ¡ng CÆ° DÃ¢n](#7-luá»“ng-5-Ä‘Äƒng-kÃ½--quáº£n-lÃ½-vÃ©-thÃ¡ng-cÆ°-dÃ¢n)
8. [Luá»“ng 6: Quy TrÃ¬nh CÆ° DÃ¢n Chuyá»ƒn NhÆ°á»£ng Xe & Admin PhÃª Duyá»‡t](#8-luá»“ng-6-quy-trÃ¬nh-cÆ°-dÃ¢n-chuyá»ƒn-nhÆ°á»£ng-xe--admin-phÃª-duyá»‡t)
9. [Luá»“ng 7: BÃ¡o CÃ¡o Thá»‘ng KÃª, Máº­t Äá»™ Giá» Cao Äiá»ƒm & Doanh Thu](#9-luá»“ng-7-bÃ¡o-cÃ¡o-thá»‘ng-kÃª-máº­t-Ä‘á»™-giá»-cao-Ä‘iá»ƒm--doanh-thu)
10. [Báº£ng Ãnh Xáº¡ CÆ¡ Sá»Ÿ Dá»¯ Liá»‡u & CÆ¡ Cháº¿ Äá»“ng Bá»™ KÃ©p (Dual-Sync Architecture)](#10-báº£ng-Ã¡nh-xáº¡-cÆ¡-sá»Ÿ-dá»¯-liá»‡u--cÆ¡-cháº¿-Ä‘á»“ng-bá»™-kÃ©p)

---

## 1. Tá»”NG QUAN KIáº¾N TRÃšC ÄA Táº¦NG

Há»‡ thá»‘ng Ä‘Æ°á»£c thiáº¿t káº¿ theo mÃ´ hÃ¬nh **Client - Server (Single Page Application + RESTful API)** káº¿t há»£p xá»­ lÃ½ thá»‹ giÃ¡c mÃ¡y tÃ­nh Computer Vision thá»i gian thá»±c:

```mermaid
graph TD
    subgraph Client_Layer [Táº§ng Giao Diá»‡n NgÆ°á»i DÃ¹ng (Client Layer - SPA)]
        UI_Admin[Giao diá»‡n Quáº£n trá»‹ Admin]
        UI_Guard[BÃ n trá»±c Báº£o vá»‡ Live]
        UI_Resident[Cá»•ng thÃ´ng tin CÆ° dÃ¢n]
    end

    subgraph App_Layer [Táº§ng á»¨ng Dá»¥ng & Äiá»u Phá»‘i (Application Layer - Flask)]
        API_Auth[Module XÃ¡c thá»±c & PhÃ¢n quyá»n Auth]
        API_Guard[Module Äiá»u hÃ nh BÃ n trá»±c & Barrier]
        API_Vehicles[Module Quáº£n lÃ½ Xe & PhÃ¢n nhÃ³m]
        API_Admin[Module Quáº£n lÃ½ User & Chuyá»ƒn nhÆ°á»£ng]
        Camera_Stream[Luá»“ng Streaming Video MJPEG gen_frames]
    end

    subgraph AI_Layer [Táº§ng Thá»‹ GiÃ¡c MÃ¡y TÃ­nh AI (Computer Vision Core)]
        YOLO[YOLOv8 Plate Detector]
        OCR[Bá»™ nháº­n diá»‡n kÃ½ tá»± kÃ©p CRNN-CTC + EasyOCR]
        Tracker[Thuáº­t toÃ¡n Tracking IOU & Voting 3-Frame]
    end

    subgraph Data_Layer [Táº§ng CÆ¡ Sá»Ÿ Dá»¯ Liá»‡u MySQL (Data Persistence)]
        DB_Engine[(Báº£ng AI Cá»‘t lÃµi: vehicles, parking_sessions, detections, plates)]
        DB_Admin[(Báº£ng Nghiá»‡p vá»¥ TÃ²a nhÃ : cu_dan, nhan_vien, phuong_tien, lich_su_ra_vao)]
    end

    Client_Layer <==>|HTTP REST API / JSON| App_Layer
    Camera_Stream <==>|Xá»­ lÃ½ tá»«ng Frame| AI_Layer
    App_Layer <==>|Äá»“ng bá»™ kÃ©p Dual Sync SQL| Data_Layer
```

- **Táº§ng AI & Computer Vision (Thá»‹ giÃ¡c mÃ¡y tÃ­nh)**:
  - **YOLOv8s**: MÃ´ hÃ¬nh Deep Learning phÃ¡t hiá»‡n vÃ  khoanh vÃ¹ng Bounding Box vá»‹ trÃ­ biá»ƒn sá»‘ trÃªn khung hÃ¬nh.
  - **CRNN-CTC & EasyOCR**: Pipeline nháº­n diá»‡n quang há»c kÃ©p (káº¿t há»£p nháº­n diá»‡n siÃªu tá»‘c báº±ng máº¡ng CRNN Ä‘Ã£ huáº¥n luyá»‡n táº­p kÃ½ tá»± biá»ƒn Viá»‡t Nam vÃ  EasyOCR dá»± phÃ²ng).
  - **Object Tracking & Voting Filter**: Bá»™ lá»c dá»‹ch chuyá»ƒn dá»±a trÃªn IOU vÃ  cÆ¡ cháº¿ Ä‘áº¿m sá»‘ láº§n xuáº¥t hiá»‡n liÃªn tiáº¿p (Hit counter $\ge 3$) giÃºp loáº¡i bá» nhiá»…u rung láº¯c camera trÆ°á»›c khi chá»‘t biá»ƒn sá»‘ xe.
- **Táº§ng á»¨ng dá»¥ng Backend (Python Flask)**:
  - Cung cáº¥p toÃ n bá»™ RESTful API, quáº£n lÃ½ `session` Ä‘Äƒng nháº­p, kiá»ƒm soÃ¡t quyá»n truy cáº­p theo vai trÃ² (`admin`, `resident`, `operator`).
  - Quáº£n lÃ½ Ä‘a luá»“ng camera Ä‘á»c tá»« Webcam/RTSP/IP Camera, táº¡o luá»“ng video feed chuáº©n MJPEG.
- **Táº§ng CÆ¡ sá»Ÿ dá»¯ liá»‡u (MySQL Database)**:
  - Thiáº¿t káº¿ **Kiáº¿n trÃºc Ä‘á»“ng bá»™ kÃ©p (Dual-Sync Database)**:
    - *NhÃ³m báº£ng tiáº¿ng Anh*: Phá»¥c vá»¥ AI Engine cháº¡y vá»›i Ä‘á»™ trá»… tháº¥p nháº¥t (`plates`, `detections`, `parking_sessions`, `vehicles`, `app_users`).
    - *NhÃ³m báº£ng tiáº¿ng Viá»‡t*: Phá»¥c vá»¥ bÃ¡o cÃ¡o hÃ nh chÃ­nh, quáº£n lÃ½ cÆ° dÃ¢n vÃ  cÄƒn há»™ theo chuáº©n Ä‘á»“ Ã¡n CNPM (`cu_dan`, `nhan_vien`, `phuong_tien`, `lich_su_ra_vao`, `chuyen_nhuong_xe`).

---

## 2. SÆ  Äá»’ DÃ’NG Dá»® LIá»†U Tá»”NG THá»‚

```mermaid
sequenceDiagram
    autonumber
    actor Driver as TÃ i xáº¿ xe
    participant Cam as Camera Cá»•ng
    participant AI as AI Engine (YOLOv8 + CRNN)
    participant Core as Backend (database.py)
    participant DB as MySQL Database
    participant Guard as Giao diá»‡n BÃ n Trá»±c Báº£o Vá»‡
    participant Barrier as Cá»•ng Tá»± Äá»™ng Barrier

    Driver->>Cam: LÃ¡i xe tiáº¿n vÃ o vÃ¹ng quÃ©t camera
    Cam->>AI: Luá»“ng khung hÃ¬nh video (Video Frames)
    AI->>AI: 1. YOLOv8 phÃ¡t hiá»‡n biá»ƒn sá»‘ (Bounding Box)<br/>2. Cáº¯t áº£nh con & CRNN nháº­n diá»‡n kÃ½ tá»±<br/>3. Tracking & Bá» phiáº¿u (Voting >= 3 frames)
    AI->>Core: Gá»­i biá»ƒn sá»‘ Ä‘Ã£ xÃ¡c thá»±c (e.g. 30F-557.75, cá»•ng in/out)
    
    rect rgb(240, 248, 255)
        note over Core, DB: BÆ°á»›c tra cá»©u & xá»­ lÃ½ giao dá»‹ch
        Core->>DB: Tra cá»©u nhÃ³m xe (SELECT group_type FROM vehicles)
        alt Xe thuá»™c nhÃ³m BLACKLIST (Danh sÃ¡ch Ä‘en)
            Core->>DB: Ghi nháº­n vi pháº¡m an ninh
            Core-->>Guard: Báº¯n cáº£nh bÃ¡o an ninh Äá»Ž Rá»°C (status: blacklist_alert)
            Guard->>Guard: KhÃ³a nÃºt má»Ÿ cá»•ng, phÃ¡t cÃ²i cáº£nh bÃ¡o
        else Xe Há»£p lá»‡ (Whitelist / VÃ© thÃ¡ng / VÃ£ng lai)
            alt Cá»•ng VÃ o (Gate IN)
                Core->>DB: INSERT parking_sessions (status: 'Parked')
                Core->>DB: INSERT lich_su_ra_vao (TrangThai: 'DangDo')
                Core->>Barrier: KÃ­ch hoáº¡t má»Ÿ Barrier tá»± Ä‘á»™ng
            else Cá»•ng Ra (Gate OUT)
                Core->>DB: SELECT check_in_time FROM parking_sessions WHERE status='Parked'
                Core->>Core: TÃ­nh thá»i lÆ°á»£ng Ä‘á»— (phÃºt) & Biá»ƒu phÃ­ gá»­i xe
                Core-->>Guard: Báº¯n sá»± kiá»‡n LATEST_GUARD_EVENT lÃªn BÃ n Trá»±c
                Guard->>Core: GET /api/guard/verification/<plate>
                Guard->>Guard: Hiá»ƒn thá»‹ áº£nh Ä‘á»‘i chiáº¿u VÃ o vs Ra + Sá»‘ tiá»n
                Guard->>Core: POST /api/guard/collect_fee (Báº£o vá»‡ báº¥m thu tiá»n)
                Core->>DB: UPDATE parking_sessions SET status='Completed'
                Core->>DB: UPDATE lich_su_ra_vao SET TrangThai='DaRa'
                Core->>Barrier: KÃ­ch hoáº¡t má»Ÿ Barrier cá»•ng ra
            end
        end
    end
```

---

## 3. LUá»’NG 1: NHáº¬N DIá»†N BIá»‚N Sá» AI & Tá»° Äá»˜NG CHECK-IN / CHECK-OUT Tá»ª CAMERA LIVE

### 3.1. Má»¥c Ä‘Ã­ch nghiá»‡p vá»¥
Tá»± Ä‘á»™ng giÃ¡m sÃ¡t luá»“ng xe vÃ o/ra 24/7 tá»« camera, tá»± Ä‘á»™ng phÃ¡t hiá»‡n vá»‹ trÃ­ biá»ƒn sá»‘ xe, Ä‘á»c chÃ­nh xÃ¡c kÃ½ tá»±, phÃ¢n loáº¡i nhÃ³m xe, lÆ°u trá»¯ áº£nh snapshot Ä‘á»‘i chiáº¿u vÃ  tá»± Ä‘á»™ng ghi nháº­n phiÃªn Ä‘á»— xe (Check-in/Check-out).

### 3.2. Vá»‹ trÃ­ mÃ£ nguá»“n
| ThÃ nh pháº§n | ÄÆ°á»ng dáº«n tá»‡p | HÃ m xá»­ lÃ½ | DÃ²ng mÃ£ |
| :--- | :--- | :--- | :--- |
| **VÃ²ng láº·p Ä‘á»c Camera** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `gen_frames(source_name)` | `680 - 1015` |
| **Nháº­n diá»‡n Bounding Box & OCR** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `detect_plates_from_frame(frame, reader)` | `540 - 650` |
| **Core OCR CRNN & EasyOCR** | [`ongthanquoctruong_24CT2_cnpm/plate_ocr_integration.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/plate_ocr_integration.py) | `recognize_plate(...)` | ToÃ n bá»™ file |
| **HÃ m Giao dá»‹ch CSDL** | [`ongthanquoctruong_24CT2_cnpm/database.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/database.py) | `process_parking_transaction(...)` | `1214 - 1410` |

### 3.3. DÃ²ng cháº£y dá»¯ liá»‡u chi tiáº¿t tá»«ng bÆ°á»›c
1. **Thu nháº­n Frame**: `cv2.VideoCapture` Ä‘á»c luá»“ng hÃ¬nh áº£nh tá»« Camera theo thá»i gian thá»±c (30 FPS).
2. **PhÃ¡t hiá»‡n Biá»ƒn sá»‘ (Plate Detection)**: MÃ´ hÃ¬nh `YOLOv8s` dá»± Ä‘oÃ¡n tá»a Ä‘á»™ hÃ¬nh chá»¯ nháº­t chá»©a biá»ƒn sá»‘ `[x1, y1, x2, y2]` kÃ¨m Ä‘á»™ tin cáº­y `confidence`.
3. **Tiá»n xá»­ lÃ½ áº£nh (Preprocessing)**:
   - Cáº¯t vÃ¹ng áº£nh con (Crop plate image).
   - Chuyá»ƒn áº£nh xÃ¡m (Grayscale), tÄƒng Ä‘á»™ tÆ°Æ¡ng pháº£n, khá»­ nhiá»…u.
4. **Nháº­n diá»‡n KÃ½ tá»± (OCR Recognition)**:
   - Cháº¡y mÃ´ hÃ¬nh máº¡ng nÆ¡-ron **CRNN-CTC** suy luáº­n kÃ½ tá»± chuá»—i.
   - Náº¿u Ä‘á»™ tin cáº­y tháº¥p hoáº·c áº£nh má», tá»± Ä‘á»™ng kÃ­ch hoáº¡t **EasyOCR** dá»± phÃ²ng.
   - Chuáº©n hÃ³a kÃ½ tá»± theo máº«u biá»ƒn sá»‘ Viá»‡t Nam (vÃ­ dá»¥: chuyá»ƒn Ä‘á»•i `O` thÃ nh `0`, `I` thÃ nh `1`, Ä‘á»‹nh dáº¡ng `XXY-ZZZ.ZZ` hoáº·c `XXY-ZZZZ`).
5. **Bá»™ lá»c Chá»‘ng nhiá»…u & Bá» phiáº¿u (Tracking & Voting Filter)**:
   - Thuáº­t toÃ¡n theo dÃµi Ä‘á»‘i tÆ°á»£ng `PLATE_TRACKER` tÃ­nh toÃ¡n Ä‘á»™ trÃ¹ng khá»›p IOU (Intersection over Union) giá»¯a cÃ¡c Bounding Box qua cÃ¡c frame liÃªn tiáº¿p.
   - Biá»ƒn sá»‘ chá»‰ Ä‘Æ°á»£c xÃ¡c nháº­n (`confirmed_text`) khi xuáº¥t hiá»‡n á»•n Ä‘á»‹nh $\ge 3$ láº§n trong cá»­a sá»• thá»i gian 2 giÃ¢y.
6. **Xá»­ lÃ½ Giao dá»‹ch BÃ£i xe (`database.process_parking_transaction`)**:
   - **BÆ°á»›c 6.1: Kiá»ƒm tra Blacklist**:
     - Tra cá»©u `group_type` trong báº£ng `vehicles`.
     - Náº¿u xe thuá»™c nhÃ³m `Blacklist` $\rightarrow$ Ngay láº­p tá»©c tá»« chá»‘i cho xe qua cá»•ng, kÃ­ch hoáº¡t tráº¡ng thÃ¡i `blacklist_alert`, khÃ´ng táº¡o phiÃªn Ä‘á»— há»£p lá»‡.
   - **BÆ°á»›c 6.2: Kiá»ƒm tra Tráº¡ng thÃ¡i phiÃªn Ä‘á»—**:
     - Náº¿u xe Ä‘ang cÃ³ phiÃªn `status = 'Parked'` trong bÃ£i: Tá»± Ä‘á»™ng chuyá»ƒn hÆ°á»›ng xá»­ lÃ½ sang **Cá»•ng Ra (Check-Out)**.
     - Náº¿u xe chÆ°a cÃ³ trong bÃ£i hoáº·c phiÃªn trÆ°á»›c Ä‘Ã£ hoÃ n thÃ nh: Tá»± Ä‘á»™ng xá»­ lÃ½ sang **Cá»•ng VÃ o (Check-In)**.
   - **BÆ°á»›c 6.3: Cá»•ng VÃ o (Check-In)**:
     - Táº¡o báº£n ghi má»›i trong báº£ng `parking_sessions` vá»›i tráº¡ng thÃ¡i `Parked`.
     - LÆ°u áº£nh chá»¥p xe vÃ o thÆ° má»¥c snapshot `artifacts/snapshots/`.
   - **BÆ°á»›c 6.4: Cá»•ng Ra (Check-Out)**:
     - TÃ­nh toÃ¡n sá»‘ phÃºt Ä‘á»— xe: `TIMESTAMPDIFF(MINUTE, check_in_time, NOW())`.
     - TÃ­nh phÃ­ gá»­i xe dá»±a trÃªn phÃ¢n nhÃ³m (Whitelist/VÃ© thÃ¡ng = 0 VNÄ, VÃ£ng lai = biá»ƒu phÃ­ lÅ©y tiáº¿n).
     - Cáº­p nháº­t phiÃªn sang `Completed`.
7. **Báº¯n thÃ´ng bÃ¡o BÃ n Trá»±c**:
   - Ghi thÃ´ng tin xe vá»«a quÃ©t vÃ o biáº¿n toÃ n cá»¥c luá»“ng an toÃ n `LATEST_GUARD_EVENT` Ä‘á»ƒ phá»¥c vá»¥ cÆ¡ cháº¿ Live Polling trÃªn giao diá»‡n báº£o vá»‡.

### 3.4. Dá»¯ liá»‡u lÆ°u vÃ o báº£ng nÃ o (Persistence)
- **Báº£ng `plates`**:
  ```sql
  INSERT INTO plates (plate_text, detection_count, first_detected, last_detected)
  VALUES (%s, 1, NOW(), NOW())
  ON DUPLICATE KEY UPDATE 
      detection_count = detection_count + 1, 
      last_detected = NOW();
  ```
- **Báº£ng `detections`**:
  ```sql
  INSERT INTO detections (plate_text, detected_at, confidence, camera_source, raw_text, image_path)
  VALUES (%s, NOW(), %s, %s, %s, %s);
  ```
- **Báº£ng `parking_sessions`**:
  - *LÃºc VÃ o*:
    ```sql
    INSERT INTO parking_sessions (plate_text, check_in_time, status, camera_in, image_in_path)
    VALUES (%s, NOW(), 'Parked', %s, %s);
    ```
  - *LÃºc Ra*:
    ```sql
    UPDATE parking_sessions 
    SET check_out_time = NOW(), duration_minutes = %s, fee = %s, status = 'Completed', camera_out = %s
    WHERE id = %s;
    ```
- **Báº£ng `lich_su_ra_vao`** (Äá»“ng bá»™ tiáº¿ng Viá»‡t):
  - *LÃºc VÃ o*: `INSERT INTO lich_su_ra_vao (BienSoXe, ThoiGianVao, TrangThai, LoaiKhach) VALUES (...)`
  - *LÃºc Ra*: `UPDATE lich_su_ra_vao SET ThoiGianRa = NOW(), TrangThai = 'DaRa', TienThu = %s WHERE ...`
- **Báº£ng `statistics`**: TÄƒng bá»™ Ä‘áº¿m `total_detections` theo ngÃ y hiá»‡n táº¡i.

### 3.5. Dá»¯ liá»‡u láº¥y ra nhÆ° tháº¿ nÃ o (Query)
- Tra cá»©u nhÃ³m xe & háº¡n vÃ© thÃ¡ng:
  ```sql
  SELECT group_type, vehicle_type, monthly_ticket_expiry, status 
  FROM vehicles WHERE plate_text = %s;
  ```
- Tra cá»©u phiÃªn Ä‘á»— chÆ°a hoÃ n thÃ nh:
  ```sql
  SELECT id, check_in_time, image_in_path 
  FROM parking_sessions 
  WHERE plate_text = %s AND status = 'Parked' 
  ORDER BY check_in_time DESC LIMIT 1;
  ```

---

## 4. LUá»’NG 2: NGHIá»†P Vá»¤ BÃ€N TRá»°C Báº¢O Vá»†

### 4.1. Má»¥c Ä‘Ã­ch nghiá»‡p vá»¥
Trang bá»‹ cho nhÃ¢n viÃªn báº£o vá»‡ giao diá»‡n Ä‘iá»u hÃ nh trá»±c tiáº¿p táº¡i bá»‘t gÃ¡c:
- Äá»‘i chiáº¿u song song áº£nh xe chá»¥p lÃºc vÃ o vÃ  áº£nh thá»±c táº¿ lÃºc ra (ngÄƒn cháº·n hÃ nh vi Ä‘Ã¡nh trÃ¡o biá»ƒn sá»‘, trá»™m cáº¯p xe).
- Tá»± Ä‘á»™ng hiá»ƒn thá»‹ tháº» xe, sá»‘ cÄƒn há»™, tÃªn chá»§ há»™ vÃ  sá»‘ Ä‘iá»‡n thoáº¡i liÃªn láº¡c.
- PhÃ¡t cÃ²i & hiá»ƒn thá»‹ cáº£nh bÃ¡o Ä‘á» kháº©n cáº¥p khi phÃ¡t hiá»‡n phÆ°Æ¡ng tiá»‡n náº±m trong **Danh sÃ¡ch Ä‘en (Blacklist)**.
- Tá»± Ä‘á»™ng tÃ­nh phÃ­ gá»­i xe vÃ  kÃ­ch hoáº¡t lá»‡nh má»Ÿ Barrier sau khi xÃ¡c nháº­n thu phÃ­.

### 4.2. Vá»‹ trÃ­ mÃ£ nguá»“n
| Chá»©c nÄƒng | ÄÆ°á»ng dáº«n tá»‡p | HÃ m / API Endpoint | DÃ²ng mÃ£ |
| :--- | :--- | :--- | :--- |
| **Láº¯ng nghe sá»± kiá»‡n Live (Polling)** | [`ongthanquoctruong_24CT2_cnpm/templates/index.html`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/templates/index.html) | `checkGuardLiveEvent()` (Má»—i 1.2s) | `~2640` |
| **API Láº¥y sá»± kiá»‡n má»›i nháº¥t** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `GET /api/guard/latest_event` | `2251` |
| **API Äá»‘i chiáº¿u xe** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `GET /api/guard/verification/<plate>` | `2280` |
| **HÃ m CSDL tra cá»©u Ä‘á»‘i chiáº¿u** | [`ongthanquoctruong_24CT2_cnpm/database.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/database.py) | `get_guard_verification_info(plate)` | `2074` |
| **TÃ­nh biá»ƒu phÃ­ gá»­i xe** | [`ongthanquoctruong_24CT2_cnpm/database.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/database.py) | `calculate_parking_fee(...)` | `1179` |
| **API Thu phÃ­ & In hÃ³a Ä‘Æ¡n** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `POST /api/guard/collect_fee` | `2350` |
| **API Äiá»u khiá»ƒn Barrier** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `POST /api/guard/barrier/trigger` | `2269` |

### 4.3. DÃ²ng cháº£y dá»¯ liá»‡u chi tiáº¿t
```text
Báº£o vá»‡ nháº­p biá»ƒn sá»‘ hoáº·c Camera AI tá»± Ä‘á»™ng quÃ©t báº¯t gáº·p biá»ƒn sá»‘ xe
   â”‚
   â–¼
Frontend gá»i: GET /api/guard/verification/<plate_text>
   â”‚
   â–¼
HÃ m database.get_guard_verification_info:
   1. JOIN vehicles + phuong_tien + cu_dan Ä‘á»ƒ tÃ¬m: Chá»§ xe, Sá»‘ cÄƒn há»™, SÄT.
   2. TÃ¬m phiÃªn 'Parked' gáº§n nháº¥t trong parking_sessions:
        duration_minutes = TIMESTAMPDIFF(MINUTE, check_in_time, NOW())
   3. Tra cá»©u Blacklist:
        Náº¿u group_type == 'Blacklist' â”€â”€â–º is_blacklist = True
   4. Tra cá»©u biá»ƒu phÃ­:
        Náº¿u vÃ© thÃ¡ng cÃ²n háº¡n hoáº·c Whitelist: PhÃ­ = 0 VNÄ
        Náº¿u vÃ£ng lai: Ãp dá»¥ng biá»ƒu phÃ­ lÅ©y tiáº¿n theo giá».
   â”‚
   â–¼
Frontend nháº­n JSON pháº£n há»“i:
   â”œâ”€â”€ Náº¿u is_blacklist == True:
   â”‚     - Báº­t há»™p cáº£nh bÃ¡o Äá»Ž Rá»°C: "ðŸš¨ Cáº¢NH BÃO AN NINH: XE BLACKLIST - Tá»ª CHá»I CHO QUA"
   â”‚     - Thay Ä‘á»•i badge sang "ðŸš¨ Blacklist (Cáº£nh bÃ¡o an ninh)"
   â”‚     - KhÃ³a nÃºt Má»Ÿ Barrier, hiá»ƒn thá»‹ yÃªu cáº§u xÃ¡c minh báº£o vá»‡.
   â””â”€â”€ Náº¿u xe Há»£p lá»‡:
         - Hiá»ƒn thá»‹ báº£ng Ä‘á»‘i chiáº¿u 2 cá»™t: [áº¢nh vÃ o + Giá» vÃ o] vs [áº¢nh ra + Giá» ra]
         - Hiá»ƒn thá»‹ thá»i lÆ°á»£ng Ä‘á»— vÃ  sá»‘ tiá»n cáº§n thu.
   â”‚
   â–¼
Báº£o vá»‡ báº¥m "XÃ¡c Nháº­n Thu PhÃ­ & Má»Ÿ Barrier":
   1. Gá»­i POST /api/guard/collect_fee
   2. CSDL cáº­p nháº­t parking_sessions.status = 'Completed'
   3. Táº¡o mÃ£ hÃ³a Ä‘Æ¡n Ä‘iá»‡n tá»­ HD-XXXXXX
   4. Gá»­i tÃ­n hiá»‡u kÃ­ch hoáº¡t má»Ÿ Barrier Cá»•ng Ra.
```

---

## 5. LUá»’NG 3: QUáº¢N LÃ TÃ€I KHOáº¢N NGÆ¯á»œI DÃ™NG

### 5.1. Má»¥c Ä‘Ã­ch nghiá»‡p vá»¥
Cho phÃ©p Quáº£n trá»‹ viÃªn (Admin) quáº£n lÃ½ toÃ n diá»‡n ngÆ°á»i dÃ¹ng trong há»‡ thá»‘ng:
- Cáº¥p tÃ i khoáº£n má»›i cho CÆ° dÃ¢n hoáº·c NhÃ¢n viÃªn báº£o vá»‡.
- KhÃ³a hoáº·c kÃ­ch hoáº¡t láº¡i tÃ i khoáº£n.
- Äáº·t láº¡i máº­t kháº©u tÃ i khoáº£n (Reset password).
- **Chá»‰nh sá»­a toÃ n diá»‡n thÃ´ng tin sau khi thÃªm**: Thay Ä‘á»•i Há» tÃªn, Sá»‘ Ä‘iá»‡n thoáº¡i, Email, CÄƒn há»™, Ca trá»±c, Vai trÃ² vÃ  Máº­t kháº©u má»›i vá»›i cÆ¡ cháº¿ **Äá»“ng bá»™ Ä‘a báº£ng tá»± Ä‘á»™ng**.

### 5.2. Vá»‹ trÃ­ mÃ£ nguá»“n
| Chá»©c nÄƒng | ÄÆ°á»ng dáº«n tá»‡p | HÃ m / API Endpoint | DÃ²ng mÃ£ |
| :--- | :--- | :--- | :--- |
| **Giao diá»‡n báº£ng tÃ i khoáº£n** | [`templates/index.html`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/templates/index.html) | `renderUsersTable()` | `~2231` |
| **Há»™p thoáº¡i Chá»‰nh sá»­a (Modal)** | [`templates/index.html`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/templates/index.html) | Modal `#editUserModal`, `openEditUserModal()` | `~2404` |
| **API Láº¥y danh sÃ¡ch tÃ i khoáº£n** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `GET /api/admin/users` | `2084` |
| **API Chá»‰nh sá»­a tÃ i khoáº£n** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `POST /api/admin/users/update` | `2114` |
| **API Äáº·t láº¡i máº­t kháº©u** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `POST /api/admin/users/reset_password` | `2094` |
| **API KhÃ³a / Má»Ÿ tÃ i khoáº£n** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `POST /api/admin/users/toggle_status` | `2099` |
| **HÃ m CSDL cáº­p nháº­t Ä‘á»“ng bá»™** | [`ongthanquoctruong_24CT2_cnpm/database.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/database.py) | `admin_update_user_info(...)` | `1749` |

### 5.3. DÃ²ng cháº£y dá»¯ liá»‡u & Äá»“ng bá»™ CSDL Ä‘a báº£ng (Multi-table Sync)
Khi Admin chá»‰nh sá»­a thÃ´ng tin ngÆ°á»i dÃ¹ng `cudan1`, há»‡ thá»‘ng thá»±c thi giao dá»‹ch SQL Ä‘á»“ng bá»™ trÃªn nhiá»u báº£ng:

```mermaid
flowchart TD
    Admin[Admin báº¥m LÆ°u thay Ä‘á»•i] --> API[POST /api/admin/users/update]
    API --> DB_Func[database.admin_update_user_info]
    
    DB_Func --> Step1[1. UPDATE app_users:<br/>Cáº­p nháº­t full_name, email, role, is_active]
    
    DB_Func --> CondRole{Vai trÃ² ngÆ°á»i dÃ¹ng?}
    
    CondRole -->|Resident / CÆ° dÃ¢n| Step2A[2. UPDATE cu_dan:<br/>Cáº­p nháº­t HoTen, MaCanHo, SoDienThoai, Email]
    Step2A --> Step2B[3. UPDATE vehicles v INNER JOIN phuong_tien p:<br/>Äá»“ng bá»™ v.owner_name = HoTen má»›i]
    
    CondRole -->|Operator / Báº£o vá»‡| Step3A[2. UPDATE nhan_vien:<br/>Cáº­p nháº­t HoTen, CaTruc, SoDienThoai, Email]
    
    DB_Func --> CondPass{CÃ³ nháº­p máº­t kháº©u má»›i?}
    CondPass -->|CÃ³| Step4[MÃ£ hÃ³a generate_password_hash & cáº­p nháº­t Ä‘á»“ng bá»™ máº­t kháº©u]
    CondPass -->|KhÃ´ng| Step5[Giá»¯ nguyÃªn máº­t kháº©u cÅ©]
    
    Step4 --> Result[HoÃ n thÃ nh giao dá»‹ch & Tá»± Ä‘á»™ng Refresh báº£ng giao diá»‡n]
    Step5 --> Result
```

---

## 6. LUá»’NG 4: QUáº¢N LÃ DANH Má»¤C PHÆ¯Æ NG TIá»†N & PHÃ‚N NHÃ“M BLACKLIST / WHITELIST

### 6.1. Má»¥c Ä‘Ã­ch nghiá»‡p vá»¥
Quáº£n lÃ½ danh sÃ¡ch phÆ°Æ¡ng tiá»‡n Ä‘Æ°á»£c phÃ©p hoáº¡t Ä‘á»™ng trong tÃ²a nhÃ , gÃ¡n nhÃ£n phÃ¢n loáº¡i:
- **Normal (Xe thÆ°á»ng)**: TÃ­nh phÃ­ gá»­i xe theo giá» theo biá»ƒu phÃ­ tiÃªu chuáº©n.
- **Whitelist (Xe Æ°u tiÃªn)**: Xe lÃ£nh Ä‘áº¡o, cÆ° dÃ¢n Ä‘Äƒng kÃ½ vÃ© thÃ¡ng, tá»± Ä‘á»™ng miá»…n phÃ­ 0 VNÄ khi qua cá»•ng.
- **Blacklist (Danh sÃ¡ch Ä‘en)**: Xe cÃ³ nguy cÆ¡ máº¥t an toÃ n, xe vi pháº¡m quy cháº¿ hoáº·c bá»‹ nghi váº¥n trá»™m cáº¯p. **Tá»± Ä‘á»™ng tá»« chá»‘i cho xe qua cá»•ng á»Ÿ cáº£ hai chiá»u vÃ o/ra**, phÃ¡t chuÃ´ng bÃ¡o Ä‘á»™ng Ä‘á» kháº©n cáº¥p táº¡i BÃ n Trá»±c Báº£o Vá»‡.

### 6.2. Vá»‹ trÃ­ mÃ£ nguá»“n
| Chá»©c nÄƒng | ÄÆ°á»ng dáº«n tá»‡p | HÃ m / API Endpoint | DÃ²ng mÃ£ |
| :--- | :--- | :--- | :--- |
| **Giao diá»‡n Quáº£n lÃ½ Xe** | [`templates/index.html`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/templates/index.html) | Page `#vehicles-page`, Modal `#vehicleModal` | `~1840` |
| **API Láº¥y danh sÃ¡ch xe** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `GET /api/vehicles` | `2445` |
| **API ThÃªm / Sá»­a thÃ´ng tin xe** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `POST /api/vehicles/save` | `2464` |
| **API XÃ³a xe khá»i danh má»¥c** | [`ongthanquoctruong_24CT2_cnpm/app.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py) | `DELETE /api/vehicles/delete/<plate>` | `2530` |
| **HÃ m CSDL láº¥y danh sÃ¡ch xe** | [`ongthanquoctruong_24CT2_cnpm/database.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/database.py) | `get_all_vehicles()` | `851` |
| **HÃ m CSDL lÆ°u thÃ´ng tin xe** | [`ongthanquoctruong_24CT2_cnpm/database.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/database.py) | `upsert_vehicle(...)` | `718` |

### 6.3. Truy váº¥n SQL láº¥y kÃ¨m sá»‘ lÆ°á»£ng phÃ¡t hiá»‡n (Detection Count)
Äá»ƒ hiá»ƒn thá»‹ chÃ­nh xÃ¡c sá»‘ láº§n camera AI Ä‘Ã£ quÃ©t tháº¥y tá»«ng xe, há»‡ thá»‘ng thá»±c hiá»‡n `LEFT JOIN` giá»¯a báº£ng phÆ°Æ¡ng tiá»‡n `vehicles` vÃ  báº£ng thá»‘ng kÃª phÃ¡t hiá»‡n `plates`:
```sql
SELECT 
    v.plate_text, 
    v.owner_name, 
    v.vehicle_type, 
    v.color, 
    v.registration_date, 
    v.status, 
    v.province_code, 
    v.group_type, 
    v.monthly_ticket_expiry,
    COALESCE(p.detection_count, 0) AS detection_count
FROM vehicles v
LEFT JOIN plates p ON v.plate_text = p.plate_text
ORDER BY COALESCE(p.detection_count, 0) DESC, v.created_at DESC;
```

---

## 7. LUá»’NG 5: ÄÄ‚NG KÃ & QUáº¢N LÃ VÃ‰ THÃNG CÆ¯ DÃ‚N

### 7.1. Má»¥c Ä‘Ã­ch nghiá»‡p vá»¥
Tá»± Ä‘á»™ng hÃ³a quyá»n lá»£i gá»­i xe cá»§a cÆ° dÃ¢n tÃ²a nhÃ :
1. CÆ° dÃ¢n Ä‘Äƒng kÃ½ vÃ© gá»­i xe Ä‘á»‹nh ká»³ theo thÃ¡ng (1 thÃ¡ng, 3 thÃ¡ng, 6 thÃ¡ng).
2. Khi xe Ä‘i qua camera Cá»•ng Ra, há»‡ thá»‘ng kiá»ƒm tra trÆ°á»ng `monthly_ticket_expiry`:
   - Náº¿u `NOW() <= monthly_ticket_expiry`: Sá»‘ tiá»n thanh toÃ¡n tá»± Ä‘á»™ng hiá»ƒn thá»‹ **0 VNÄ**, lÃ½ do: *"Xe vÃ© thÃ¡ng cÆ° dÃ¢n cÃ²n hiá»‡u lá»±c"*.
   - Náº¿u `NOW() > monthly_ticket_expiry`: Tá»± Ä‘á»™ng chuyá»ƒn sang tÃ­nh phÃ­ lÆ°á»£t thÃ´ng thÆ°á»ng kÃ¨m thÃ´ng bÃ¡o vÃ© thÃ¡ng háº¿t háº¡n.

### 7.2. Vá»‹ trÃ­ mÃ£ nguá»“n
- **Kiá»ƒm tra hiá»‡u lá»±c vÃ© thÃ¡ng**: HÃ m `database.get_guard_verification_info` ([`database.py` dÃ²ng 2125](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/database.py#L2125)) vÃ  `database.calculate_parking_fee` ([`database.py` dÃ²ng 1185](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/database.py#L1185)).
- **Cáº­p nháº­t háº¡n vÃ© thÃ¡ng**: Khi lÆ°u thÃ´ng tin xe qua API `POST /api/vehicles/save`, trÆ°á»ng `monthly_ticket_expiry` Ä‘Æ°á»£c ghi Ä‘á»“ng thá»i vÃ o `vehicles.monthly_ticket_expiry` vÃ  `phuong_tien.NgayHetHan`.

---

## 8. LUá»’NG 6: QUY TRÃŒNH CÆ¯ DÃ‚N CHUYá»‚N NHÆ¯á»¢NG XE & ADMIN PHÃŠ DUYá»†T

### 8.1. Má»¥c Ä‘Ã­ch nghiá»‡p vá»¥
Giáº£i quyáº¿t bÃ i toÃ¡n thá»±c táº¿ trong chung cÆ°: Khi CÆ° dÃ¢n A chuyá»ƒn nhÆ°á»£ng/bÃ¡n cÄƒn há»™ hoáº·c chuyá»ƒn quyá»n sá»­ dá»¥ng phÆ°Æ¡ng tiá»‡n cho CÆ° dÃ¢n B, viá»‡c thay Ä‘á»•i pháº£i Ä‘Æ°á»£c quáº£n lÃ½ minh báº¡ch, cÃ³ phÃª duyá»‡t cá»§a Ban Quáº£n LÃ½ (Admin).

```mermaid
sequenceDiagram
    autonumber
    actor ResA as CÆ° DÃ¢n A (Chá»§ cÅ©)
    participant Client as Web Portal CÆ° DÃ¢n
    participant Server as Flask Backend (app.py)
    participant DB as MySQL Database
    actor Admin as Ban Quáº£n Trá»‹ (Admin)

    ResA->>Client: Äiá»n Ä‘Æ¡n chuyá»ƒn nhÆ°á»£ng (Chá»n Biá»ƒn sá»‘ + MÃ£ CÄƒn há»™ nháº­n)
    Client->>Server: POST /api/resident/transfer_vehicle
    Server->>DB: INSERT INTO chuyen_nhuong_xe (TrangThai = 'Pending')
    Server-->>Client: ThÃ´ng bÃ¡o: "ÄÆ¡n chuyá»ƒn nhÆ°á»£ng Ä‘Ã£ gá»­i, chá» BQL duyá»‡t"
    
    Admin->>Client: Má»Ÿ tab "YÃªu Cáº§u Chuyá»ƒn NhÆ°á»£ng"
    Client->>Server: GET /api/admin/transfer_requests
    Server->>DB: SELECT * FROM chuyen_nhuong_xe WHERE TrangThai = 'Pending'
    Server-->>Client: Tráº£ vá» danh sÃ¡ch cÃ¡c Ä‘Æ¡n Ä‘ang chá»
    
    Admin->>Client: Báº¥m "PhÃª Duyá»‡t" (Approve)
    Client->>Server: POST /api/admin/transfer_requests/<id>/action (action: 'approve')
    Server->>DB: 1. UPDATE chuyen_nhuong_xe SET TrangThai='Approved', NgayDuyet=NOW()<br/>2. UPDATE phuong_tien SET MaCuDan = MaCuDanNhan<br/>3. UPDATE vehicles SET owner_name = TenCuDanNhan
    Server-->>Client: ThÃ´ng bÃ¡o: "Chuyá»ƒn nhÆ°á»£ng phÆ°Æ¡ng tiá»‡n thÃ nh cÃ´ng"
```

### 8.2. Vá»‹ trÃ­ mÃ£ nguá»“n
- **CÆ° dÃ¢n táº¡o Ä‘Æ¡n**: `POST /api/resident/transfer_vehicle` ([`ongthanquoctruong_24CT2_cnpm/app.py` dÃ²ng 2031](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py#L2031)).
- **Admin láº¥y danh sÃ¡ch Ä‘Æ¡n**: `GET /api/admin/transfer_requests` ([`ongthanquoctruong_24CT2_cnpm/app.py` dÃ²ng 2224](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py#L2224)).
- **Admin xá»­ lÃ½ Ä‘Æ¡n**: `POST /api/admin/transfer_requests/<id>/action` ([`ongthanquoctruong_24CT2_cnpm/app.py` dÃ²ng 2232](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py#L2232)) gá»i hÃ m `database.process_transfer_request_action` ([`ongthanquoctruong_24CT2_cnpm/database.py` dÃ²ng 1980](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/database.py#L1980)).

---

## 9. LUá»’NG 7: BÃO CÃO THá»NG KÃŠ, Máº¬T Äá»˜ GIá»œ CAO ÄIá»‚M & DOANH THU

### 9.1. Má»¥c Ä‘Ã­ch nghiá»‡p vá»¥
Cung cáº¥p cho Ban Quáº£n Trá»‹ cÃ¡c bÃ¡o cÃ¡o trá»±c quan dáº¡ng biá»ƒu Ä‘á»“ (Chart.js) Ä‘á»ƒ ra quyáº¿t Ä‘á»‹nh Ä‘iá»u phá»‘i bÃ£i xe:
- Tá»•ng doanh thu theo tá»«ng ngÃ y vÃ  lÅ©y káº¿ theo thÃ¡ng.
- Thá»‘ng kÃª máº­t Ä‘á»™ phÆ°Æ¡ng tiá»‡n vÃ o bÃ£i theo tá»«ng khung giá» trong ngÃ y (0h - 23h) Ä‘á»ƒ phÃ¡t hiá»‡n giá» cao Ä‘iá»ƒm.
- Tá»· lá»‡ láº¥p Ä‘áº§y bÃ£i xe thá»i gian thá»±c (Occupancy Rate).

### 9.2. Vá»‹ trÃ­ mÃ£ nguá»“n & CÃ¢u lá»‡nh SQL
| BÃ¡o cÃ¡o | API Endpoint | Vá»‹ trÃ­ mÃ£ nguá»“n | CÃ¢u lá»‡nh SQL tá»•ng há»£p |
| :--- | :--- | :--- | :--- |
| **Doanh thu theo ngÃ y** | `GET /api/analytics/revenue` | [`app.py` L2664](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py#L2664) | `SELECT DATE(check_out_time) AS d, SUM(fee) AS total_fee, COUNT(*) AS sessions FROM parking_sessions WHERE status='Completed' GROUP BY DATE(check_out_time) ORDER BY d DESC LIMIT 30;` |
| **PhÃ¢n tÃ­ch giá» cao Ä‘iá»ƒm** | `GET /api/analytics/peak-hours` | [`app.py` L2685](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py#L2685) | `SELECT HOUR(check_in_time) AS h, COUNT(*) AS count FROM parking_sessions GROUP BY HOUR(check_in_time) ORDER BY h ASC;` |
| **Tá»•ng quan Dashboard** | `GET /get_dashboard_summary` | [`app.py` L2389](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py#L2389) | TÃ­nh tá»•ng xe trong bÃ£i (`status='Parked'`), sá»‘ lÆ°á»£t quÃ©t hÃ´m nay, sá»‘ lÆ°á»£ng xe Blacklist Ä‘Ã£ phÃ¡t hiá»‡n. |

---

## 10. Báº¢NG ÃNH Xáº  CÆ  Sá»ž Dá»® LIá»†U & CÆ  CHáº¾ Äá»’NG Bá»˜ KÃ‰P

Äá»ƒ tá»‘i Æ°u hÃ³a hiá»‡u nÄƒng tÃ­nh toÃ¡n AI thá»i gian thá»±c mÃ  váº«n Ä‘Ã¡p á»©ng Ä‘áº§y Ä‘á»§ yÃªu cáº§u quáº£n lÃ½ hÃ nh chÃ­nh cá»§a mÃ´n há»c CÃ´ng nghá»‡ pháº§n má»m, há»‡ thá»‘ng Ã¡p dá»¥ng mÃ´ hÃ¬nh **Äá»“ng bá»™ kÃ©p (Dual-Sync Database)** giá»¯a 2 nhÃ³m báº£ng:

| Nghiá»‡p Vá»¥ Quáº£n LÃ½ | Báº£ng AI Cá»‘t LÃµi (Engine) | Báº£ng Nghiá»‡p Vá»¥ HÃ nh ChÃ­nh | KhÃ³a / TrÆ°á»ng LiÃªn Káº¿t Äá»“ng Bá»™ | Ã NghÄ©a Ká»¹ Thuáº­t |
| :--- | :--- | :--- | :--- | :--- |
| **Nháº­n diá»‡n biá»ƒn sá»‘** | `plates`<br>`detections` | `lich_su_ra_vao` | `plates.plate_text` $\Leftrightarrow$ `lich_su_ra_vao.BienSoXe`<br>`detections.detected_at` $\Leftrightarrow$ `lich_su_ra_vao.ThoiGianVao` | Báº£ng `plates` vÃ  `detections` lÆ°u trá»¯ dá»¯ liá»‡u AI chi tiáº¿t (tá»a Ä‘á»™ BBox, confidence, camera_source). Báº£ng `lich_su_ra_vao` lÆ°u lá»‹ch sá»­ hÃ nh chÃ­nh cho báº£o vá»‡ tra cá»©u. |
| **Danh má»¥c xe** | `vehicles` | `phuong_tien` | `vehicles.plate_text` $\Leftrightarrow$ `phuong_tien.BienSoXe`<br>`vehicles.owner_name` $\Leftrightarrow$ `cu_dan.HoTen`<br>`vehicles.monthly_ticket_expiry` $\Leftrightarrow$ `phuong_tien.NgayHetHan` | Äá»“ng bá»™ thÃ´ng tin loáº¡i xe, mÃ u sáº¯c, thá»i háº¡n vÃ© thÃ¡ng vÃ  phÃ¢n nhÃ³m (Blacklist / Whitelist / Normal). |
| **PhiÃªn gá»­i xe** | `parking_sessions` | `lich_su_ra_vao` | `parking_sessions.plate_text` $\Leftrightarrow$ `lich_su_ra_vao.BienSoXe`<br>`parking_sessions.status` = 'Completed' $\Leftrightarrow$ `lich_su_ra_vao.TrangThai` = 'DaRa' | Quáº£n lÃ½ vÃ²ng Ä‘á»i lÆ°á»£t Ä‘á»— xe: tá»« lÃºc quÃ©t vÃ o (`Parked`), tÃ­nh toÃ¡n thá»i lÆ°á»£ng vÃ  thu phÃ­, cho Ä‘áº¿n khi quÃ©t ra (`Completed`). |
| **TÃ i khoáº£n ngÆ°á»i dÃ¹ng** | `app_users` | `cu_dan` (CÆ° dÃ¢n)<br>`nhan_vien` (Báº£o vá»‡) | `app_users.username` $\Leftrightarrow$ `TaiKhoan`<br>`app_users.full_name` $\Leftrightarrow$ `HoTen`<br>`app_users.password_hash` $\Leftrightarrow$ `MatKhau`<br>`app_users.is_active` $\Leftrightarrow$ `TrangThai` | Khi Admin táº¡o hoáº·c chá»‰nh sá»­a tÃ i khoáº£n ngÆ°á»i dÃ¹ng, hÃ m `admin_update_user_info` tá»± Ä‘á»™ng Ä‘á»“ng bá»™ sang báº£ng CÆ° dÃ¢n hoáº·c NhÃ¢n viÃªn tÆ°Æ¡ng á»©ng. |
| **Chuyá»ƒn nhÆ°á»£ng xe** | `vehicles` (cáº­p nháº­t chá»§ sá»Ÿ há»¯u má»›i) | `chuyen_nhuong_xe`<br>`phuong_tien` | `chuyen_nhuong_xe.MaCuDanNhan` $\rightarrow$ `phuong_tien.MaCuDan`<br>`cu_dan.HoTen` $\rightarrow$ `vehicles.owner_name` | Äáº£m báº£o tÃ­nh toÃ n váº¹n dá»¯ liá»‡u khi cÃ³ giao dá»‹ch chuyá»ƒn giao xe giá»¯a 2 cÄƒn há»™ trong chung cÆ°. |

---
*TÃ i liá»‡u Ä‘áº·c táº£ kiáº¿n trÃºc Ä‘Æ°á»£c biÃªn soáº¡n hoÃ n chá»‰nh phá»¥c vá»¥ bÃ¡o cÃ¡o vÃ  báº£o vá»‡ Ä‘á»“ Ã¡n mÃ´n há»c CÃ´ng Nghá»‡ Pháº§n Má»m (CNPM24).*
