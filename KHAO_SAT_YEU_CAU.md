# BÃO CÃO KHáº¢O SÃT & Äáº¶C Táº¢ YÃŠU Cáº¦U Há»† THá»NG
## 3.1. GIAI ÄOáº N Láº¬P Káº¾ HOáº CH â€“ KHáº¢O SÃT YÃŠU Cáº¦U
### Äá»€ TÃ€I: Há»† THá»NG NHáº¬N DIá»†N BIá»‚N Sá» XE & QUáº¢N LÃ BÃƒI XE THÃ”NG MINH (AI SMART PARKING SYSTEM)

---

> **MÃ´n há»c**: CÃ´ng nghá»‡ pháº§n má»m (CNPM24)  
> **Lá»›p**: 24CT2  
> **Sinh viÃªn thá»±c hiá»‡n**: Ã”ng ThÃ¢n Quá»‘c TrÆ°á»ng  
> **TrÆ°á»ng**: Äáº¡i há»c Kiáº¿n trÃºc ÄÃ  Náºµng (DAU)  
> **Giáº£ng viÃªn hÆ°á»›ng dáº«n**: ThS. Pháº¡m Thá»‹ Dung  
> **CÃ´ng nghá»‡ Ã¡p dá»¥ng**: Python (Flask) + YOLOv8 + CRNN-CTC/EasyOCR + MySQL + HTML5/CSS3/Vanilla JS (SPA)  
> **CÃ¡c giáº£i phÃ¡p/sáº£n pháº©m máº«u tham kháº£o (Benchmark Links)**:
> 1. **Sighthound ALPR Demo**: [https://www.sighthound.com/products/alpr/demo](https://www.sighthound.com/products/alpr/demo)
> 2. **Plate Recognizer**: [https://platerecognizer.com/](https://platerecognizer.com/)
> 3. **VietANPR - Viscom Solution**: [https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)

---

## I. NGUYÃŠN Táº®C VIáº¾T YÃŠU Cáº¦U RÃ• RÃ€NG (Má»¤C 3.1)

Trong giai Ä‘oáº¡n kháº£o sÃ¡t yÃªu cáº§u pháº§n má»m, viá»‡c phÃ¢n Ä‘á»‹nh má»©c Ä‘á»™ Æ°u tiÃªn vÃ  viáº¿t tiÃªu chÃ­ nghiá»‡m thu Ä‘Æ°á»£c chuáº©n hÃ³a nhÆ° sau:
1. **YÃªu cáº§u Chá»©c nÄƒng (Functional Requirements - FR)**: LÃ  cÃ¡c chá»©c nÄƒng nghiá»‡p vá»¥ báº¯t buá»™c pháº£i cÃ³ Ä‘á»ƒ há»‡ thá»‘ng váº­n hÃ nh $\rightarrow$ **Má»©c Ä‘á»™ Æ°u tiÃªn luÃ´n luÃ´n lÃ  CAO**, Ä‘Ã¡nh sá»‘ tÄƒng dáº§n liÃªn tá»¥c (`FR-01`, `FR-02`, `FR-03`, ...).
2. **YÃªu cáº§u Phi Chá»©c nÄƒng (Non-Functional Requirements - NFR)**: LÃ  cÃ¡c chá»‰ tiÃªu ká»¹ thuáº­t vá» cháº¥t lÆ°á»£ng, hiá»‡u nÄƒng, Ä‘á»™ tin cáº­y vÃ  báº£o máº­t $\rightarrow$ **Má»©c Ä‘á»™ Æ°u tiÃªn luÃ´n luÃ´n lÃ  TRUNG BÃŒNH**, Ä‘Ã¡nh sá»‘ tÄƒng dáº§n liÃªn tá»¥c (`NFR-01`, `NFR-02`, `NFR-03`, ...).
3. **Cáº¥u trÃºc báº£ng Ä‘áº·c táº£ chuáº©n 7 cá»™t**:
   - Cá»™t 1: **MÃ£** (MÃ£ Ä‘á»‹nh danh yÃªu cáº§u tÄƒng dáº§n)
   - Cá»™t 2: **TÃªn yÃªu cáº§u** (Ngáº¯n gá»n, sÃºc tÃ­ch)
   - Cá»™t 3: **MÃ´ táº£ yÃªu cáº§u** (Diá»…n Ä‘áº¡t rÃµ tÃ¡c nhÃ¢n vÃ  hÃ nh vi há»‡ thá»‘ng: *"NgÆ°á»i dÃ¹ng/Há»‡ thá»‘ng cÃ³ thá»ƒ..."*)
   - Cá»™t 4: **Æ¯u tiÃªn** (Quy chuáº©n: FR luÃ´n lÃ  **Cao**, NFR luÃ´n lÃ  **Trung bÃ¬nh**)
   - Cá»™t 5: **TiÃªu chÃ­ nghiá»‡m thu (Acceptance Criteria)** (Äiá»u kiá»‡n kiá»ƒm thá»­ ÄÃºng/Sai Ä‘o lÆ°á»ng Ä‘Æ°á»£c)
   - Cá»™t 6: **Link máº«u** (LiÃªn káº¿t giáº£i phÃ¡p thá»±c táº¿ Ä‘Æ°á»£c kháº£o sÃ¡t: *Sighthound ALPR*, *Plate Recognizer*, *VietANPR* vÃ  giao diá»‡n thá»±c táº¿ cá»§a Ä‘á»“ Ã¡n)
   - Cá»™t 7: **ÄÃ£ hoÃ n thÃ nh** (Cá»™t kiá»ƒm tra tiáº¿n Ä‘á»™ hiá»‡n thá»±c hÃ³a vÃ  nghiá»‡m thu tÃ­nh nÄƒng trong mÃ£ nguá»“n dá»± Ã¡n)

---

## II. Báº¢NG Äáº¶C Táº¢ YÃŠU Cáº¦U CHá»¨C NÄ‚NG (FUNCTIONAL REQUIREMENTS - FR)

> **Quy chuáº©n**: ToÃ n bá»™ yÃªu cáº§u chá»©c nÄƒng (FR) cÃ³ má»©c Æ°u tiÃªn luÃ´n lÃ  **Cao**, Ä‘Ã¡nh sá»‘ thá»© tá»± tÄƒng dáº§n tá»« `FR-01` Ä‘áº¿n `FR-15`, tÃªn yÃªu cáº§u ngáº¯n gá»n, chuáº©n má»±c cÃ´ng nghá»‡ pháº§n má»m, tÃ¡ch báº¡ch rÃµ rÃ ng giá»¯a Ä‘Äƒng nháº­p há»‡ thá»‘ng, Ä‘Äƒng kÃ½ tÃ i khoáº£n, Ä‘Äƒng kÃ½ phÆ°Æ¡ng tiá»‡n, chá»n bÃ£i Ä‘á»— xe Ä‘áº¿n cÃ¡c quy trÃ¬nh kiá»ƒm soÃ¡t AI vÃ  quáº£n trá»‹.

| MÃ£ | TÃªn yÃªu cáº§u | MÃ´ táº£ yÃªu cáº§u | Æ¯u tiÃªn | TiÃªu chÃ­ nghiá»‡m thu (Acceptance Criteria) | Link máº«u (Tham kháº£o & Giao diá»‡n) | ÄÃ£ hoÃ n thÃ nh |
| :---: | :--- | :--- | :---: | :--- | :--- | :---: |
| **FR-01** | ÄÄƒng nháº­p há»‡ thá»‘ng | NgÆ°á»i dÃ¹ng (Quáº£n trá»‹ viÃªn, NhÃ¢n viÃªn báº£o vá»‡, CÆ° dÃ¢n) Ä‘Äƒng nháº­p vÃ o há»‡ thá»‘ng báº±ng tÃ i khoáº£n vÃ  máº­t kháº©u Ä‘á»ƒ truy cáº­p theo Ä‘Ãºng phÃ¢n quyá»n. | **Cao** | - ÄÄƒng nháº­p Ä‘Ãºng $\rightarrow$ Äiá»u hÆ°á»›ng vÃ o Ä‘Ãºng trang lÃ m viá»‡c theo vai trÃ² (`/` cho Admin/Báº£o vá»‡, `/resident-dashboard` cho CÆ° dÃ¢n).<br>- ÄÄƒng nháº­p sai hoáº·c tÃ i khoáº£n bá»‹ khÃ³a $\rightarrow$ Hiá»ƒn thá»‹ thÃ´ng bÃ¡o lá»—i rÃµ rÃ ng, giá»¯ láº¡i tÃªn tÃ i khoáº£n. | â€¢ [VietANPR - PhÃ¢n quyá»n ngÆ°á»i dÃ¹ng](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [Giao diá»‡n ÄÄƒng nháº­p](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/login.html) (`/login`) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-02** | ÄÄƒng kÃ½ tÃ i khoáº£n | Cho phÃ©p cÆ° dÃ¢n má»›i tá»± Ä‘Äƒng kÃ½ tÃ i khoáº£n trá»±c tuyáº¿n trÃªn há»‡ thá»‘ng vá»›i thÃ´ng tin cÄƒn há»™, há» tÃªn, sá»‘ Ä‘iá»‡n thoáº¡i vÃ  máº­t kháº©u. | **Cao** | - Nháº­p Ä‘áº§y Ä‘á»§ thÃ´ng tin há»£p lá»‡ $\rightarrow$ Táº¡o tÃ i khoáº£n thÃ nh cÃ´ng, máº­t kháº©u mÃ£ hÃ³a an toÃ n PBKDF2/SHA-256, tá»± Ä‘á»™ng gÃ¡n quyá»n `Resident`.<br>- Kiá»ƒm tra vÃ  cáº£nh bÃ¡o náº¿u tÃªn tÃ i khoáº£n (username) hoáº·c sá»‘ Ä‘iá»‡n thoáº¡i Ä‘Ã£ tá»“n táº¡i.<br>- ÄÄƒng kÃ½ thÃ nh cÃ´ng $\rightarrow$ CÃ³ thá»ƒ Ä‘Äƒng nháº­p ngay vÃ o Cá»•ng Dá»‹ch Vá»¥ CÆ° DÃ¢n. | â€¢ [VietANPR - Quáº£n lÃ½ tÃ i khoáº£n khÃ¡ch hÃ ng](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [Form ÄÄƒng KÃ½ TÃ i Khoáº£n](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/login.html) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-03** | ÄÄƒng kÃ½ phÆ°Æ¡ng tiá»‡n | CÆ° dÃ¢n cÃ³ thá»ƒ Ä‘Äƒng kÃ½ phÆ°Æ¡ng tiá»‡n Ã´ tÃ´ má»›i cho cÄƒn há»™, khai bÃ¡o biá»ƒn sá»‘, chá»§ xe, sá»‘ Ä‘iá»‡n thoáº¡i vÃ  Ä‘Äƒng kÃ½ gÃ³i vÃ© thÃ¡ng Ä‘á»‹nh ká»³. | **Cao** | - Biá»ƒn sá»‘ xe Ä‘Æ°á»£c tá»± Ä‘á»™ng chuáº©n hÃ³a Ä‘á»‹nh dáº¡ng xe cÆ¡ giá»›i Viá»‡t Nam (VD: `30A-123.45`).<br>- Kiá»ƒm tra vÃ  ngÄƒn cháº·n Ä‘Äƒng kÃ½ trÃ¹ng biá»ƒn sá»‘ Ä‘ang hoáº¡t Ä‘á»™ng trong há»‡ thá»‘ng.<br>- PhÆ°Æ¡ng tiá»‡n sau khi Ä‘Äƒng kÃ½ hiá»ƒn thá»‹ ngay trÃªn tháº» xe 3D táº¡i Cá»•ng CÆ° DÃ¢n. | â€¢ [VietANPR - Quáº£n lÃ½ xe cÆ° dÃ¢n](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [Cá»•ng Dá»‹ch Vá»¥ CÆ° DÃ¢n](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/resident_dashboard.html#vehiclesSection) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-04** | Chá»n vá»‹ trÃ­ bÃ£i Ä‘á»— xe | Hiá»ƒn thá»‹ sÆ¡ Ä‘á»“ bÃ£i xe mÃ´ phá»ng ráº¡p chiáº¿u phim (Cinema Seat Style) vá»›i 100 Ã´ Ä‘á»— 2 táº§ng háº§m; cho phÃ©p cÆ° dÃ¢n chá»n vá»‹ trÃ­ trá»‘ng khi Ä‘Äƒng kÃ½ xe vÃ  Ä‘á»•i vá»‹ trÃ­ linh hoáº¡t. | **Cao** | - Hiá»ƒn thá»‹ trá»±c quan 100 vá»‹ trÃ­ Ä‘á»— Ã´ tÃ´ táº¡i 2 táº§ng háº§m (Háº§m B1 vÃ  Háº§m B2: DÃ£y A, B, C, D, E, F, VIP).<br>- Tráº¡ng thÃ¡i mÃ u sáº¯c theo chuáº©n ráº¡p phim: Xanh lÃ¡ (Trá»‘ng), Äá» (ÄÃ£ cÃ³ xe), Xanh dÆ°Æ¡ng (Äang chá»n), VÃ ng (VIP), Cyan (Xe cá»§a báº¡n).<br>- Chá»‘ng chá»n trÃ¹ng vá»‹ trÃ­ Ä‘á»— (Conflict 400); há»— trá»£ Ä‘á»•i vá»‹ trÃ­ Ä‘á»— tá»©c thá»i trÃªn giao diá»‡n.<br>- Vá»‹ trÃ­ sá»‘ 01 luÃ´n hiá»ƒn thá»‹ Ä‘áº§u hÃ ng, khÃ´ng bá»‹ che khuáº¥t; tá»± Ä‘á»™ng cuá»™n (scrollIntoView) mÆ°á»£t mÃ  Ä‘áº¿n Ã´ Ä‘ang chá»n. | â€¢ [CGV / Cinema Seat Booking Layout](https://www.cgv.vn/)<br>â€¢ [SÆ¡ Ä‘á»“ BÃ£i Xe Cinema](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/resident_dashboard.html#cinemaModal) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-05** | Nháº­n diá»‡n biá»ƒn sá»‘ tá»« camera | Há»‡ thá»‘ng camera tá»± Ä‘á»™ng phÃ¡t hiá»‡n vá»‹ trÃ­ biá»ƒn sá»‘ (YOLOv8) vÃ  nháº­n dáº¡ng kÃ½ tá»± quang há»c (CRNN/EasyOCR) theo thá»i gian thá»±c khi xe Ä‘áº¿n cá»•ng. | **Cao** | - Tá»± Ä‘á»™ng váº½ khung chá»¯ nháº­t nháº­n diá»‡n (Bounding Box) mÃ u xanh lÃ¡ trÃªn khung hÃ¬nh video.<br>- Äá»c vÃ  chuáº©n hÃ³a chuá»—i kÃ½ tá»± biá»ƒn sá»‘ theo máº«u biá»ƒn Viá»‡t Nam vá»›i Ä‘á»™ tin cáº­y $confidence \ge 0.5$. | â€¢ [Plate Recognizer - Live Camera ANPR](https://platerecognizer.com/)<br>â€¢ [Sighthound ALPR Demo](https://www.sighthound.com/products/alpr/demo)<br>â€¢ [Tab Nháº­n Diá»‡n Biá»ƒn Sá»‘](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#recognition-page) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-06** | Nháº­n diá»‡n biá»ƒn sá»‘ tá»« hÃ¬nh áº£nh | Cho phÃ©p ngÆ°á»i dÃ¹ng hoáº·c ká»¹ thuáº­t viÃªn táº£i áº£nh chá»¥p xe (.jpg, .png) lÃªn há»‡ thá»‘ng Ä‘á»ƒ kiá»ƒm tra kháº£ nÄƒng nháº­n diá»‡n cá»§a mÃ´ hÃ¬nh AI. | **Cao** | - Táº£i áº£nh lÃªn $\rightarrow$ tráº£ vá» áº£nh káº¿t quáº£ Ä‘Ã£ khoanh vÃ¹ng biá»ƒn sá»‘, chuá»—i kÃ½ tá»± nháº­n diá»‡n, Ä‘á»™ tin cáº­y vÃ  thá»i gian xá»­ lÃ½ $< 1$ giÃ¢y.<br>- Hiá»ƒn thá»‹ káº¿t quáº£ trá»±c quan trÃªn giao diá»‡n thá»­ nghiá»‡m. | â€¢ [Sighthound ALPR Demo - Image Test](https://www.sighthound.com/products/alpr/demo)<br>â€¢ [Plate Recognizer Snapshot API](https://platerecognizer.com/)<br>â€¢ [Khu Vá»±c Táº£i áº¢nh Thá»­ Nghiá»‡m](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#test-image-section) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-07** | Kiá»ƒm soÃ¡t xe vÃ o (Check-In) | Khi xe tiáº¿n vÃ o cá»•ng vÃ o, há»‡ thá»‘ng tá»± Ä‘á»™ng nháº­n diá»‡n biá»ƒn sá»‘, chá»¥p áº£nh snapshot lÆ°u trá»¯ vÃ  táº¡o phiÃªn gá»­i xe má»›i. | **Cao** | - Tá»± Ä‘á»™ng táº¡o báº£n ghi má»›i trong báº£ng `parking_sessions` vá»›i tráº¡ng thÃ¡i `Parked`.<br>- LÆ°u áº£nh chá»¥p xe vÃ o thÆ° má»¥c snapshot `artifacts/snapshots/`.<br>- Äá»“ng bá»™ tá»©c thá»i sang báº£ng `lich_su_ra_vao` vá»›i tráº¡ng thÃ¡i `DangDo`. | â€¢ [VietANPR - Quáº£n lÃ½ xe vÃ o cá»•ng](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [Trang LÆ°á»£t Xe Ra/VÃ o](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#sessions-page) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-08** | Kiá»ƒm soÃ¡t xe ra (Check-Out) | Khi xe tiáº¿n vÃ o cá»•ng ra, há»‡ thá»‘ng tá»± Ä‘á»™ng tÃ¬m phiÃªn Ä‘á»— xe Ä‘ang má»Ÿ, tÃ­nh toÃ¡n chÃ­nh xÃ¡c thá»i gian Ä‘á»— theo phÃºt. | **Cao** | - Truy váº¥n tÃ¬m phiÃªn `status = 'Parked'` gáº§n nháº¥t cá»§a biá»ƒn sá»‘ xe.<br>- TÃ­nh chÃ­nh xÃ¡c khoáº£ng thá»i gian: `TIMESTAMPDIFF(MINUTE, check_in_time, NOW())`.<br>- Hiá»ƒn thá»‹ thá»i lÆ°á»£ng Ä‘á»— Ä‘á»‹nh dáº¡ng `X giá» Y phÃºt` lÃªn mÃ n hÃ¬nh Ä‘á»‘i soÃ¡t. | â€¢ [VietANPR - Kiá»ƒm soÃ¡t lÃ n ra bÃ£i xe](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [BÃ n Trá»±c Äá»‘i SoÃ¡t Ra/VÃ o](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#guard-station-page) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-09** | Äá»‘i chiáº¿u hÃ¬nh áº£nh vÃ o - ra | Khi xe ra, mÃ n hÃ¬nh nhÃ¢n viÃªn trá»±c hiá»ƒn thá»‹ song song áº£nh chá»¥p lÃºc vÃ o vÃ  áº£nh thá»±c táº¿ lÃºc ra Ä‘á»ƒ kiá»ƒm tra tÃ­nh toÃ n váº¹n (chá»‘ng Ä‘á»•i biá»ƒn/trá»™m xe). | **Cao** | - Hiá»ƒn thá»‹ bá»‘ cá»¥c 2 cá»™t side-by-side: Cá»™t trÃ¡i [áº¢nh vÃ o + Giá» vÃ o + Camera vÃ o], Cá»™t pháº£i [áº¢nh ra + Giá» ra + Biá»ƒn sá»‘ quÃ©t Ä‘Æ°á»£c].<br>- Hiá»ƒn thá»‹ tÃªn chá»§ xe, sá»‘ Ä‘iá»‡n thoáº¡i, mÃ£ cÄƒn há»™ náº¿u lÃ  xe cÆ° dÃ¢n. | â€¢ [VietANPR - BÃ n trá»±c Ä‘á»‘i chiáº¿u áº£nh vÃ o ra](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [Khung Äá»‘i Chiáº¿u Side-by-Side](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#verify-card-grid) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-10** | TÃ­nh cÆ°á»›c phÃ­ tá»± Ä‘á»™ng | Há»‡ thá»‘ng tá»± Ä‘á»™ng tÃ­nh sá»‘ tiá»n cáº§n thu dá»±a trÃªn thá»i lÆ°á»£ng Ä‘á»— vÃ  phÃ¢n loáº¡i phÆ°Æ¡ng tiá»‡n (VÃ© thÃ¡ng cÆ° dÃ¢n = 0 VNÄ, VÃ£ng lai = theo biá»ƒu phÃ­). | **Cao** | - Xe Whitelist / VÃ© thÃ¡ng cÃ²n háº¡n $\rightarrow$ CÆ°á»›c phÃ­ hiá»ƒn thá»‹: **0 VNÄ** (LÃ½ do: *"VÃ© thÃ¡ng cÆ° dÃ¢n cÃ²n hiá»‡u lá»±c"*).<br>- Xe vÃ£ng lai $\rightarrow$ TÃ­nh tiá»n lÅ©y tiáº¿n theo block giá» quy Ä‘á»‹nh.<br>- Xe vÃ© thÃ¡ng háº¿t háº¡n $\rightarrow$ Cáº£nh bÃ¡o vÃ© háº¿t háº¡n vÃ  tá»± Ä‘á»™ng tÃ­nh cÆ°á»›c lÆ°á»£t. | â€¢ [VietANPR - TÃ­nh phÃ­ gá»­i xe tá»± Ä‘á»™ng](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [Há»™p TÃ­nh PhÃ­ BÃ n Trá»±c](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#guardFeeBox) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-11** | Cáº£nh bÃ¡o an ninh xe Blacklist | Tá»± Ä‘á»™ng phÃ¡t hiá»‡n vÃ  báº­t cáº£nh bÃ¡o kháº©n cáº¥p khi xe thuá»™c Danh sÃ¡ch Ä‘en (Blacklist / Xe vi pháº¡m / Nghi váº¥n trá»™m cáº¯p) xuáº¥t hiá»‡n. | **Cao** | - Báº­t há»™p cáº£nh bÃ¡o Äá»Ž Rá»°C chá»›p nhÃ¡y: *"ðŸš¨ Cáº¢NH BÃO AN NINH: XE BLACKLIST - Tá»ª CHá»I CHO QUA"*; phÃ¡t chuÃ´ng cÃ²i bÃ¡o Ä‘á»™ng.<br>- Tá»± Ä‘á»™ng vÃ´ hiá»‡u hÃ³a nÃºt má»Ÿ barrier, yÃªu cáº§u báº£o vá»‡ giá»¯ xe kiá»ƒm tra an ninh. | â€¢ [Plate Recognizer - Blacklist & Alert](https://platerecognizer.com/)<br>â€¢ [VietANPR - Cáº£nh bÃ¡o xe vi pháº¡m](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [Há»™p Cáº£nh BÃ¡o An Ninh Blacklist](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#guardBlacklistAlert) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-12** | XÃ¡c nháº­n thu phÃ­ & Má»Ÿ Barrier | NhÃ¢n viÃªn báº£o vá»‡ xÃ¡c nháº­n thu tiá»n $\rightarrow$ há»‡ thá»‘ng hoÃ n táº¥t phiÃªn gá»­i xe, táº¡o mÃ£ hÃ³a Ä‘Æ¡n Ä‘iá»‡n tá»­ vÃ  phÃ¡t xung má»Ÿ barrier tá»± Ä‘á»™ng. | **Cao** | - Báº¥m "XÃ¡c Nháº­n Thu PhÃ­ & Má»Ÿ Barrier": Tráº¡ng thÃ¡i phiÃªn chuyá»ƒn thÃ nh `Completed`, lÆ°u sá»‘ tiá»n Ä‘Ã£ thu.<br>- Tá»± Ä‘á»™ng táº¡o mÃ£ hÃ³a Ä‘Æ¡n Ä‘iá»‡n tá»­ Ä‘á»‹nh dáº¡ng `HD-XXXXXX`.<br>- KÃ­ch hoáº¡t lá»‡nh má»Ÿ Barrier cá»•ng ra vÃ  thÃ´ng bÃ¡o cho xe qua cá»•ng an toÃ n. | â€¢ [VietANPR - Äiá»u khiá»ƒn Barrier & In hÃ³a Ä‘Æ¡n](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [NÃºt Thu PhÃ­ & KÃ­ch Hoáº¡t Barrier](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#guardConfirmActionBtn) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-13** | Quáº£n lÃ½ danh má»¥c phÆ°Æ¡ng tiá»‡n | Quáº£n trá»‹ viÃªn vÃ  báº£o vá»‡ cÃ³ thá»ƒ xem danh sÃ¡ch toÃ n bá»™ xe, tÃ¬m kiáº¿m, thÃªm má»›i, chá»‰nh sá»­a thÃ´ng tin xe, gÃ¡n nhÃ£n phÃ¢n nhÃ³m vÃ  phÃ¢n bá»• Ã´ Ä‘á»—. | **Cao** | - Báº£ng dá»¯ liá»‡u hiá»ƒn thá»‹ biá»ƒn sá»‘, chá»§ xe, loáº¡i xe, mÃ u sáº¯c, háº¡n vÃ© thÃ¡ng, sá»‘ láº§n phÃ¡t hiá»‡n, vá»‹ trÃ­ Ã´ Ä‘á»— cá»‘ Ä‘á»‹nh (`bai_do`).<br>- GÃ¡n nhÃ£n phÃ¢n nhÃ³m: Normal (ThÆ°á»ng), Whitelist (Æ¯u tiÃªn), Blacklist (Cáº¥m).<br>- Thao tÃ¡c ThÃªm/Sá»­a/XÃ³a cÃ³ xÃ¡c nháº­n vÃ  Ä‘á»“ng bá»™ tá»©c thá»i vÃ o CSDL. | â€¢ [Plate Recognizer - Vehicle Management](https://platerecognizer.com/)<br>â€¢ [Trang Quáº£n LÃ½ Danh Má»¥c Xe](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#vehicles-page) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-14** | Quáº£n lÃ½ vÃ© thÃ¡ng & Lá»‹ch sá»­ xe | CÆ° dÃ¢n Ä‘Äƒng nháº­p cÃ³ thá»ƒ xem danh sÃ¡ch xe cá»§a cÄƒn há»™, tra cá»©u lá»‹ch sá»­ vÃ o/ra, gia háº¡n vÃ© thÃ¡ng Ä‘á»‹nh ká»³ vÃ  gá»­i yÃªu cáº§u chuyá»ƒn nhÆ°á»£ng xe. | **Cao** | - Hiá»ƒn thá»‹ tháº» xe dáº¡ng 3D mÃ´ phá»ng biá»ƒn sá»‘ chuáº©n Viá»‡t Nam, tráº¡ng thÃ¡i Ä‘ang Ä‘á»— vÃ  háº¡n vÃ© thÃ¡ng.<br>- CÆ° dÃ¢n chá»n gÃ³i gia háº¡n (1, 3, 6 thÃ¡ng) $\rightarrow$ há»‡ thá»‘ng tá»± Ä‘á»™ng cá»™ng dá»“n ngÃ y háº¿t háº¡n vÃ  cáº­p nháº­t CSDL.<br>- Báº£ng tra cá»©u lá»‹ch sá»­ hiá»ƒn thá»‹ Ä‘áº§y Ä‘á»§ má»‘c thá»i gian vÃ o/ra vÃ  áº£nh chá»¥p Ä‘á»‘i chiáº¿u. | â€¢ [VietANPR - Quáº£n lÃ½ khÃ¡ch hÃ ng cÆ° dÃ¢n & VÃ© thÃ¡ng](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [Cá»•ng Dá»‹ch Vá»¥ CÆ° DÃ¢n](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/resident_dashboard.html) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **FR-15** | BÃ¡o cÃ¡o & Thá»‘ng kÃª doanh thu | Cung cáº¥p mÃ n hÃ¬nh Dashboard trá»±c quan hiá»ƒn thá»‹ cÃ¡c chá»‰ sá»‘ váº­n hÃ nh vÃ  biá»ƒu Ä‘á»“ phÃ¢n tÃ­ch doanh thu, giá» cao Ä‘iá»ƒm. | **Cao** | - 4 tháº» KPI cáº­p nháº­t tá»± Ä‘á»™ng: Tá»•ng lÆ°á»£t quÃ©t AI, Xe Ä‘ang trong bÃ£i, Tá»•ng sá»‘ xe Ä‘Ã£ Ä‘Äƒng kÃ½, Sá»‘ xe vi pháº¡m Blacklist.<br>- Biá»ƒu Ä‘á»“ cá»™t: Thá»‘ng kÃª doanh thu theo tá»«ng ngÃ y trong thÃ¡ng.<br>- Biá»ƒu Ä‘á»“ Ä‘Æ°á»ng: PhÃ¢n tÃ­ch lÆ°u lÆ°á»£ng xe theo 24 khung giá» xÃ¡c Ä‘á»‹nh giá» cao Ä‘iá»ƒm.<br>- Há»— trá»£ xuáº¥t dá»¯ liá»‡u ra file CSV chuáº©n UTF-8. | â€¢ [Plate Recognizer - Dashboard & Analytics](https://platerecognizer.com/)<br>â€¢ [Sighthound ALPR - Reporting](https://www.sighthound.com/products/alpr/demo)<br>â€¢ [Trang BÃ¡o CÃ¡o & Thá»‘ng KÃª](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html#reports-page) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |

---

## III. Báº¢NG Äáº¶C Táº¢ YÃŠU Cáº¦U PHI CHá»¨C NÄ‚NG (NON-FUNCTIONAL REQUIREMENTS - NFR)

> **Quy chuáº©n**: ToÃ n bá»™ yÃªu cáº§u phi chá»©c nÄƒng (NFR) cÃ³ má»©c Æ°u tiÃªn luÃ´n lÃ  **Trung bÃ¬nh**, Ä‘Ã¡nh sá»‘ thá»© tá»± tÄƒng dáº§n tá»« `NFR-01` Ä‘áº¿n `NFR-05`, bao quÃ¡t cÃ¡c chuáº©n má»±c ká»¹ thuáº­t vá» hiá»‡u nÄƒng, Ä‘á»™ chÃ­nh xÃ¡c AI, thá»i gian pháº£n há»“i, Ä‘á»™ á»•n Ä‘á»‹nh vÃ  báº£o máº­t.

| MÃ£ | TÃªn yÃªu cáº§u | MÃ´ táº£ yÃªu cáº§u | Æ¯u tiÃªn | TiÃªu chÃ­ nghiá»‡m thu (Acceptance Criteria) | Link máº«u (Tham kháº£o & Ká»¹ thuáº­t) | ÄÃ£ hoÃ n thÃ nh |
| :---: | :--- | :--- | :---: | :--- | :--- | :---: |
| **NFR-01** | Tá»‘c Ä‘á»™ nháº­n diá»‡n AI thá»i gian thá»±c | Thá»i gian há»‡ thá»‘ng phÃ¡t hiá»‡n biá»ƒn sá»‘ (YOLOv8) vÃ  nháº­n dáº¡ng kÃ½ tá»± (CRNN) pháº£i Ä‘á»§ nhanh Ä‘á»ƒ phÆ°Æ¡ng tiá»‡n khÃ´ng bá»‹ Ã¹n á»© táº¡i lÃ n xe. | **Trung bÃ¬nh** | - Tá»•ng thá»i gian suy luáº­n (Inference Time) trÃªn mÃ¡y tÃ­nh CPU thÃ´ng thÆ°á»ng $\le 0.8$ giÃ¢y/frame.<br>- Tá»‘c Ä‘á»™ khung hÃ¬nh luá»“ng video camera duy trÃ¬ á»•n Ä‘á»‹nh $\ge 15$ FPS khi giÃ¡m sÃ¡t trá»±c tiáº¿p. | â€¢ [Sighthound ALPR - Real-time Performance Benchmark](https://www.sighthound.com/products/alpr/demo)<br>â€¢ [Plate Recognizer - Speed Optimization](https://platerecognizer.com/)<br>â€¢ [Module Tá»‘i Æ¯u HÃ³a OCR](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/crnn_ocr_wrapper.py) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **NFR-02** | Äá»™ chÃ­nh xÃ¡c nháº­n dáº¡ng biá»ƒn sá»‘ xe | MÃ´ hÃ¬nh AI pháº£i Ä‘áº£m báº£o Ä‘á»™ chÃ­nh xÃ¡c cao trong nháº­n diá»‡n biá»ƒn sá»‘ cÆ¡ giá»›i theo tiÃªu chuáº©n kÃ½ tá»± biá»ƒn Viá»‡t Nam. | **Trung bÃ¬nh** | - Tá»· lá»‡ phÃ¡t hiá»‡n vá»‹ trÃ­ biá»ƒn sá»‘ (Detection Accuracy) Ä‘áº¡t $\ge 98\%$.<br>- Tá»· lá»‡ nháº­n diá»‡n Ä‘Ãºng toÃ n bá»™ chuá»—i kÃ½ tá»± (Full-plate Accuracy) Ä‘áº¡t $\ge 92\%$ trong Ä‘iá»u kiá»‡n Ã¡nh sÃ¡ng chuáº©n.<br>- Tá»± Ä‘á»™ng kÃ­ch hoáº¡t EasyOCR dá»± phÃ²ng khi Ä‘á»™ tin cáº­y CRNN tháº¥p. | â€¢ [Plate Recognizer - Accuracy Benchmark 98%](https://platerecognizer.com/)<br>â€¢ [VietANPR - Äá»™ chÃ­nh xÃ¡c nháº­n dáº¡ng biá»ƒn sá»‘ VN](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [BÃ¡o CÃ¡o Huáº¥n Luyá»‡n OCR](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/README_CRNN_OCR.md) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **NFR-03** | Thá»i gian pháº£n há»“i giao diá»‡n & API | ToÃ n bá»™ cÃ¡c thao tÃ¡c tÆ°Æ¡ng tÃ¡c ngÆ°á»i dÃ¹ng trÃªn web vÃ  API truy váº¥n cÆ¡ sá»Ÿ dá»¯ liá»‡u pháº£i pháº£n há»“i tá»©c thÃ¬. | **Trung bÃ¬nh** | - Thá»i gian táº£i trang ban Ä‘áº§u $< 1.5$ giÃ¢y.<br>- Thá»i gian pháº£n há»“i API tra cá»©u, chuyá»ƒn tab, má»Ÿ modal hoáº·c cáº­p nháº­t dá»¯ liá»‡u $\le 300$ms trÃªn mÃ´i trÆ°á»ng máº¡ng ná»™i bá»™ bÃ£i xe. | â€¢ [Plate Recognizer - Fast REST API Specification](https://platerecognizer.com/)<br>â€¢ [Kiáº¿n TrÃºc Tá»‘i Æ¯u SPA](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/fe/templates/index.html) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **NFR-04** | TÃ­nh sáºµn sÃ ng & á»”n Ä‘á»‹nh há»‡ thá»‘ng (24/7) | Pháº§n má»m quáº£n lÃ½ bÃ£i xe pháº£i váº­n hÃ nh liÃªn tá»¥c 24/7 táº¡i cá»•ng kiá»ƒm soÃ¡t, cÃ³ kháº£ nÄƒng tá»± phá»¥c há»“i khi máº¥t káº¿t ná»‘i camera. | **Trung bÃ¬nh** | - Tá»± Ä‘á»™ng káº¿t ná»‘i láº¡i (Auto-reconnect) khi camera máº¥t tÃ­n hiá»‡u táº¡m thá»i.<br>- Bá»c toÃ n bá»™ cÃ¡c hÃ m CSDL vÃ  camera trong khá»‘i `try...except`, ghi log chi tiáº¿t mÃ  khÃ´ng lÃ m crash tiáº¿n trÃ¬nh mÃ¡y chá»§.<br>- Tá»· lá»‡ kháº£ dá»¥ng há»‡ thá»‘ng (Uptime) $\ge 99.5\%$. | â€¢ [VietANPR - Giáº£i phÃ¡p bÃ£i xe hoáº¡t Ä‘á»™ng 24/7 liÃªn tá»¥c](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [Luá»“ng Äá»c Camera An ToÃ n](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py#L680) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |
| **NFR-05** | An toÃ n thÃ´ng tin & PhÃ¢n quyá»n báº£o máº­t | Dá»¯ liá»‡u cÃ¡ nhÃ¢n cá»§a cÆ° dÃ¢n, lá»‹ch sá»­ ra vÃ o vÃ  máº­t kháº©u pháº£i Ä‘Æ°á»£c báº£o vá»‡ nghiÃªm ngáº·t chá»‘ng truy cáº­p trÃ¡i phÃ©p. | **Trung bÃ¬nh** | - ToÃ n bá»™ máº­t kháº©u lÆ°u trong CSDL MySQL Ä‘Æ°á»£c bÄƒm báº£o máº­t báº±ng thuáº­t toÃ¡n PBKDF2/SHA-256 (`generate_password_hash`).<br>- Má»i API quáº£n trá»‹ Ä‘á»u kiá»ƒm tra `@login_required` vÃ  xÃ¡c thá»±c quyá»n `Admin`/`Operator` trÆ°á»›c khi xá»­ lÃ½. | â€¢ [Plate Recognizer - On-Premise Data Security](https://platerecognizer.com/)<br>â€¢ [VietANPR - TiÃªu chuáº©n báº£o máº­t CSDL](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)<br>â€¢ [HÃ m MÃ£ HÃ³a & PhÃ¢n Quyá»n Auth](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/app.py#L28) | **[âœ”] ÄÃ£ hoÃ n thÃ nh** |

---

## IV. SÆ  Äá»’ USE CASE Há»† THá»NG (USE CASE DIAGRAM)

```mermaid
graph TD
    %% TÃ¡c nhÃ¢n
    Admin((Quáº£n Trá»‹ ViÃªn))
    Guard((NhÃ¢n ViÃªn Báº£o Vá»‡))
    Resident((CÆ° DÃ¢n))
    AI_Camera((Há»‡ Thá»‘ng Camera AI))

    subgraph Core_System [Há»† THá»NG QUáº¢N LÃ BÃƒI XE THÃ”NG MINH - AI SMART PARKING]
        UC_01[FR-01: ÄÄƒng nháº­p há»‡ thá»‘ng]
        UC_02[FR-02: ÄÄƒng kÃ½ tÃ i khoáº£n]
        UC_03[FR-03: ÄÄƒng kÃ½ phÆ°Æ¡ng tiá»‡n]
        UC_04[FR-04: Chá»n vá»‹ trÃ­ bÃ£i Ä‘á»— xe]
        UC_05[FR-05, 06: Nháº­n diá»‡n Biá»ƒn sá»‘ Live & áº¢nh]
        UC_06[FR-07: Ghi nháº­n xe vÃ o Check-In]
        UC_07[FR-08, 09: Äá»‘i soÃ¡t xe ra & Äá»‘i chiáº¿u áº£nh]
        UC_08[FR-10: TÃ­nh cÆ°á»›c phÃ­ tá»± Ä‘á»™ng]
        UC_09[FR-11: Cáº£nh bÃ¡o an ninh xe Blacklist]
        UC_10[FR-12: XÃ¡c nháº­n thu phÃ­ & Má»Ÿ Barrier]
        UC_11[FR-13: Quáº£n lÃ½ danh má»¥c phÆ°Æ¡ng tiá»‡n]
        UC_12[FR-14: Quáº£n lÃ½ vÃ© thÃ¡ng & Lá»‹ch sá»­ xe]
        UC_13[FR-15: BÃ¡o cÃ¡o & Thá»‘ng kÃª doanh thu]
    end

    Resident --> UC_01
    Resident --> UC_02
    Resident --> UC_03
    Resident --> UC_04
    Resident --> UC_12

    Guard --> UC_01
    Guard --> UC_06
    Guard --> UC_07
    Guard --> UC_08
    Guard --> UC_09
    Guard --> UC_10
    Guard --> UC_11

    Admin --> UC_01
    Admin --> UC_04
    Admin --> UC_11
    Admin --> UC_13

    AI_Camera --> UC_05
    AI_Camera --> UC_06
    AI_Camera --> UC_07
    AI_Camera --> UC_09
```

---

## V. Äá»I SÃNH TÃNH NÄ‚NG Vá»šI CÃC Sáº¢N PHáº¨M MáºªU TRÃŠN THá»Š TRÆ¯á»œNG (BENCHMARK ANALYSIS)

Báº£ng phÃ¢n tÃ­ch Ä‘á»‘i sÃ¡nh giá»¯a Ä‘á» tÃ i Ä‘á»“ Ã¡n mÃ´n há»c vÃ  3 giáº£i phÃ¡p thÆ°Æ¡ng máº¡i Ä‘Æ°á»£c kháº£o sÃ¡t:

| TÃ­nh NÄƒng Nghiá»‡p Vá»¥ | Äá» TÃ i Cá»§a Sinh ViÃªn (AI Smart Parking) | Sighthound ALPR ([Link máº«u](https://www.sighthound.com/products/alpr/demo)) | Plate Recognizer ([Link máº«u](https://platerecognizer.com/)) | VietANPR - Viscom ([Link máº«u](https://viscomsolution.com/vietanpr-phan-mem-nhan-dien-bien-so-xe/)) |
| :--- | :---: | :---: | :---: | :---: |
| **Nháº­n diá»‡n biá»ƒn sá»‘ thá»i gian thá»±c** | âœ… CÃ³ (YOLOv8 + CRNN) | âœ… CÃ³ | âœ… CÃ³ | âœ… CÃ³ |
| **Há»— trá»£ Ä‘á»‹nh dáº¡ng biá»ƒn sá»‘ Viá»‡t Nam** | âœ… ChuyÃªn sÃ¢u biá»ƒn sá»‘ VN | âš ï¸ Háº¡n cháº¿ (chá»§ yáº¿u US/EU) | âœ… CÃ³ há»— trá»£ biá»ƒn VN | âœ… ChuyÃªn sÃ¢u biá»ƒn sá»‘ VN |
| **BÃ n trá»±c Ä‘á»‘i chiáº¿u áº£nh VÃ o/Ra** | âœ… Bá»‘ cá»¥c side-by-side | âŒ KhÃ´ng cÃ³ (chá»‰ cÃ³ API) | âš ï¸ CÃ³ trÃªn ParkPow | âœ… CÃ³ Ä‘áº§y Ä‘á»§ |
| **Cáº£nh bÃ¡o an ninh xe Blacklist** | âœ… Cáº£nh bÃ¡o Ä‘á» + ChuÃ´ng | âš ï¸ CÃ³ qua Webhook | âœ… CÃ³ qua giao diá»‡n | âœ… CÃ³ Ä‘áº§y Ä‘á»§ |
| **Tá»± Ä‘á»™ng tÃ­nh phÃ­ & Má»Ÿ Barrier** | âœ… CÃ³ (Relay Barrier) | âŒ KhÃ´ng cÃ³ (chá»‰ cÃ³ API) | âš ï¸ TÃ­ch há»£p bÃªn thá»© 3 | âœ… CÃ³ há»— trá»£ Barrier |
| **Cá»•ng dá»‹ch vá»¥ cÆ° dÃ¢n & ÄÄƒng kÃ½ xe** | âœ… CÃ³ (Web Portal) | âŒ KhÃ´ng cÃ³ | âŒ KhÃ´ng cÃ³ | âœ… CÃ³ |
| **SÆ¡ Ä‘á»“ chá»n vá»‹ trÃ­ bÃ£i Ä‘á»— (Cinema Map)** | âœ… CÃ³ (100 Ã´ / 2 táº§ng háº§m) | âŒ KhÃ´ng cÃ³ | âŒ KhÃ´ng cÃ³ | âš ï¸ Danh sÃ¡ch Ã´ cÆ¡ báº£n |
| **BÃ¡o cÃ¡o doanh thu & Giá» cao Ä‘iá»ƒm** | âœ… Chart.js + Xuáº¥t CSV | âš ï¸ BÃ¡o cÃ¡o lÆ°á»£t gá»i API | âœ… BÃ¡o cÃ¡o lÆ°u lÆ°á»£ng xe | âœ… BÃ¡o cÃ¡o doanh thu |
| **MÃ´i trÆ°á»ng triá»ƒn khai thá»±c táº¿** | âœ… MÃ¡y tÃ­nh ná»™i bá»™ (On-premise) | â˜ï¸ Cloud / On-premise | â˜ï¸ Cloud / On-premise | ðŸ–¥ï¸ On-premise táº¡i bá»‘t gÃ¡c |

---

*TÃ i liá»‡u Ä‘áº·c táº£ kháº£o sÃ¡t yÃªu cáº§u chuáº©n 7 cá»™t (cÃ³ cá»™t kiá»ƒm tra ÄÃ£ hoÃ n thÃ nh) Ä‘Æ°á»£c cáº­p nháº­t hoÃ n chá»‰nh phá»¥c vá»¥ bÃ¡o cÃ¡o vÃ  Ä‘Ã¡nh giÃ¡ nghiá»‡m thu Ä‘á»“ Ã¡n mÃ´n há»c CÃ´ng Nghá»‡ Pháº§n Má»m (CNPM24).*
