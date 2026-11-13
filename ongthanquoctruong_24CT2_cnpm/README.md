# Hệ Thống Quản Lý Bãi Đỗ Xe Thông Minh Ứng Dụng AI Nhận Diện Biển Số Xe (Smart Parking AI)

- **Đề tài**: Hệ thống Nhận diện Biển số xe & Quản lý Bãi đỗ xe Thông minh ứng dụng AI
- **Môn học**: Công nghệ phần mềm (CNPM24) — **Lớp**: `24CT2`
- **Sinh viên thực hiện**: Ông Thân Quốc Trường
- **Đơn vị**: Khoa Công nghệ thông tin — Trường Đại học Kiến trúc Đà Nẵng (DAU)

> Xem tài liệu tổng quan cấp repository tại [`../README.md`](../README.md).

---

## 🏛️ Kiến Trúc 3 Quyền Tách Biệt Độc Lập (3 Isolated Roles — Không Dính Dáng Nhau)

```mermaid
flowchart TB
    subgraph Lane1["PHÂN HỆ 1: ADMIN (be/roles/admin_user.py — Độc lập)"]
        direction TB
        A1(["Role 1: Quản Trị Viên (Admin)"])
        A2["Quyền Admin (quyen_admin):<br/>• Tạo/Sửa/Khóa/Xóa User & Đổi Role<br/>• Duyệt/Từ chối đơn chuyển nhượng xe<br/>• Thêm/Sửa/Xóa xe & Gán Blacklist/Whitelist<br/>• Xem chi tiết 100 ô đỗ B1/B2<br/>• Thống kê doanh thu, Xuất CSV & Test AI"]
        A3["UI & API Riêng:<br/>/operations-dashboard (Full Admin)<br/>/api/admin/*, /api/vehicles/save, /delete, /api/analytics/*"]
        A4[("DB Admin:<br/>quyen_admin, phan_quyen_admin<br/>app_users, nhan_vien, vehicles<br/>chuyen_nhuong_xe, statistics")]
        A1 --> A2 --> A3 --> A4
    end

    subgraph Lane2["PHÂN HỆ 2: GUARD / OPERATOR (be/roles/guard_user.py — Độc lập)"]
        direction TB
        G1(["Role 2: Bảo Vệ (Operator / Security)"])
        G2["Quyền Bảo Vệ (quyen_baove):<br/>• Xem 2 Camera Live & Đổi AI Auto/In/Out<br/>• Check-in/Check-out & Nhập biển số tay<br/>• Đối chiếu ảnh Vào-Ra & Tra cứu xe (Chỉ xem)<br/>• Cảnh báo chặn xe Blacklist<br/>• Thu phí, Xuất hóa đơn & Mở/Đóng Barrier"]
        G3["Trạm Trực, AI & API Riêng:<br/>Bàn trực Cổng (ẩn tab User/Duyệt đơn/Báo cáo)<br/>YOLOv8s + CRNN-CTC + EasyOCR<br/>/video_feed_*, /api/guard/*, /api/parking/checkin, checkout"]
        G4[("DB Bảo Vệ & Cổng:<br/>quyen_baove, phan_quyen_bao_ve<br/>plates, detections, bang_gia<br/>parking_sessions, lich_su_ra_vao, hoa_don")]
        G1 --> G2 --> G3 --> G4
    end

    subgraph Lane3["PHÂN HỆ 3: RESIDENT (be/roles/resident_user.py — Độc lập)"]
        direction TB
        R1(["Role 3: Cư Dân (Resident / User)"])
        R2["Quyền Cư Dân (quyen_user):<br/>• Đăng ký & Khôi phục MK OTP<br/>• Sửa hồ sơ & Đổi mật khẩu<br/>• Thêm/Sửa/Xóa xe căn hộ mình<br/>• Chọn/Đổi ô đỗ Cinema B1/B2<br/>• Gia hạn vé tháng<br/>• Lập đơn chuyển nhượng & Xem lịch sử cá nhân"]
        R3["Cổng Cư Dân & API Riêng:<br/>/resident-dashboard, /register, /forgot-password<br/>/api/resident/*, /api/parking/map"]
        R4[("DB Cư Dân:<br/>quyen_user, cu_dan, quan_ly_otp_token<br/>phuong_tien, bai_do, chuyen_nhuong_xe")]
        R1 --> R2 --> R3 --> R4
    end

    style Lane1 fill:#fff1f2,stroke:#dc2626,stroke-width:2px
    style Lane2 fill:#eff6ff,stroke:#2563eb,stroke-width:2px
    style Lane3 fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
```

---

## 👥 Chi Tiết 3 Vai Trò Trong Đề Tài

1. **Role 1 — Quản trị viên (`Admin` | `be/roles/admin_user.py` -> `/operations-dashboard`)**:
   - Quản lý tài khoản & phân quyền (`app_users`, `nhan_vien`, `cu_dan`, `quyen_admin`, `phan_quyen_admin`): tạo Bảo vệ (`/api/admin/guards/create`), tạo Cư dân (`/api/admin/residents/create`), sửa thông tin & đổi vai trò (`/api/admin/users/update`), khóa/mở tài khoản (`/api/admin/users/toggle_status`), đặt lại mật khẩu (`/api/admin/users/reset_password`), xóa người dùng.
   - Phê duyệt đơn chuyển nhượng xe (`/api/admin/transfer_requests`, `/api/admin/transfer_requests/<id>/action`, `/update_doc` -> `chuyen_nhuong_xe`).
   - Quản lý danh mục phương tiện & phân nhóm `Normal / Whitelist / Blacklist` (`/api/vehicles`, `/api/vehicles/save`, `/api/vehicles/delete/<plate>` -> `vehicles`, `plates`).
   - Quản lý sơ đồ 100 ô đỗ Cinema (`Ham_B1`, `Ham_B2`: `/api/parking/map` -> `bai_do`).
   - Xem thống kê KPI, doanh thu, giờ cao điểm, xuất CSV & test AI ảnh tĩnh (`/get_dashboard_summary`, `/api/analytics/revenue`, `/api/analytics/peak-hours`, `/api/report_export`, `/api/recognize_image`).

2. **Role 2 — Nhân viên Bảo vệ (`Operator` / `Security` | `be/roles/guard_user.py` -> `/operations-dashboard`)**:
   - Giám sát Camera Live Stream (`/video_feed_webcam`, `/video_feed_phone`) & chuyển đổi chế độ camera (`/api/guard/camera_mode`, `/api/guard/latest_event`).
   - Kiểm soát xe vào/ra, đối chiếu ảnh chụp lúc vào và lúc ra (`/api/guard/verification/<plate>`, `/api/guard/manual_entry`, `/api/parking/checkin`, `/api/parking/checkout/<id>`).
   - Tiếp nhận cảnh báo đỏ xe `Blacklist`, từ chối mở cổng.
   - Tra cứu cước phí gửi xe, thu tiền & kích hoạt mở/đóng Barrier (`/api/guard/collect_fee`, `/api/guard/barrier/trigger` -> `bang_gia`, `hoa_don`, `lich_su_ra_vao`, `quyen_baove`, `phan_quyen_bao_ve`).

3. **Role 3 — Cư dân (`Resident` / `User` | `be/roles/resident_user.py` -> `/resident-dashboard`)**:
   - Đăng ký tài khoản cư dân (`/register`, `/api/register`), Đăng nhập (`/login`, `/api/login`), Quên & Đặt lại mật khẩu qua OTP (`/forgot-password`, `/reset-password` -> `quan_ly_otp_token`).
   - Cập nhật hồ sơ & đổi mật khẩu (`/api/resident/profile`, `/api/resident/update_profile`, `/api/resident/change_password`).
   - Quản lý xe căn hộ (`/api/resident/vehicles`, `/api/resident/add_vehicle`, `PUT/DELETE /api/resident/vehicles/<plate>` -> `phuong_tien`, `vehicles`).
   - Xem sơ đồ bãi đỗ xe Cinema `Ham_B1` & `Ham_B2`, chọn / đổi vị trí đỗ (`/api/parking/map`, `/api/resident/change_slot` -> `bai_do`).
   - Gia hạn vé tháng, lập/theo dõi đơn chuyển nhượng xe & xem lịch sử ra/vào cá nhân (`/api/resident/renew_ticket`, `/api/resident/transfer_vehicle`, `/api/resident/transfer_requests`, `/api/resident/history`).

---

## 🏗️ Cấu Trúc Dự Án

```text
ongthanquoctruong_24CT2_cnpm/
├── api/                              # Vercel Serverless API (index.js, [...slug].js)
├── public/                           # Giao diện tĩnh cho Vercel SPA deployment
├── fe/                               # Frontend Jinja2 Templates & Static assets (Local Flask)
├── be/                               # Backend Flask + YOLOv8 + CRNN/EasyOCR + MySQL + roles/ + sql/ + scripts/
├── tests/                            # Bộ kiểm thử tự động (test_full_features.py, test_user_management.py, ...)
├── docs/                             # Tuần Tự/, LUONGXULY/, PERT/, Wireframe/, Word báo cáo/, drawio/
├── doc_images/                       # Ảnh sơ đồ & UI demo dùng cho báo cáo
├── schema.dbml                       # Lược đồ quan hệ DBML phục vụ GitDiagram
├── vercel.json                       # Cấu hình định tuyến Vercel
├── package.json                      # Thông tin package phục vụ Vercel/static serve
├── requirements.txt                  # Thư viện Python cho Backend & AI
└── .env.example                      # Mẫu biến môi trường MySQL & SECRET_KEY
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy Local

1. **Kích hoạt môi trường ảo:**
   ```powershell
   .venv\Scripts\activate
   ```
2. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Cấu hình MySQL (tạo `.env` từ `.env.example`):**
   ```env
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=HTTT_QuanLyBaiXe_AI
   MYSQL_PORT=3306
   APP_SECRET_KEY=dev-secret-change-me
   ```
   Khởi tạo bảng và dữ liệu 100 chỗ đỗ:
   ```powershell
   python be/setup_bai_do.py
   ```
4. **Khởi chạy Server Flask:**
   ```powershell
   python be/app.py
   ```
   Truy cập: **http://127.0.0.1:5000**

---

## 🧪 Chạy Kiểm Thử (Run Tests)

```powershell
python -m unittest discover -s tests -p "test_*.py"
```
