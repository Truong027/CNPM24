# SƠ ĐỒ CHỨC NĂNG (USE CASE) - ADMIN VÀ BẢO VỆ

Sơ đồ ERD trên GitDiagram chỉ hiển thị **Cơ Sở Dữ Liệu (các bảng lưu trữ)**. Để xem chi tiết **"Tác nhân Admin và Bảo vệ được làm những gì"**, chúng ta sử dụng sơ đồ **Use Case** dưới đây.

```mermaid
flowchart LR
    %% Định nghĩa Tác nhân
    Admin((QUẢN TRỊ VIÊN\nADMIN))
    Guard((NHÂN VIÊN\nBẢO VỆ))

    %% Nhóm chức năng Admin
    subgraph ADMIN_FUNC [HỆ THỐNG CHỨC NĂNG CỦA QUẢN TRỊ VIÊN]
        direction TB
        
        subgraph ADM_AUTH [1. Xác thực & Hồ sơ]
            direction TB
            A_A1([Đăng nhập hệ thống])
            A_A2([Đổi mật khẩu & Xem hồ sơ])
        end
        
        subgraph ADM_USERS [2. Quản lý Người dùng]
            direction TB
            A_U1([Xem danh sách tài khoản])
            A_U2([Cấp tài khoản mới Bảo vệ/Cư dân])
            A_U3([Chỉnh sửa thông tin người dùng])
            A_U4([Khóa / Mở khóa tài khoản])
            A_U5([Đặt lại mật khẩu Reset Password])
        end

        subgraph ADM_VEHICLES [3. Quản lý Phương tiện]
            direction TB
            A_V1([Xem danh mục phương tiện])
            A_V2([Thêm / Sửa / Xóa thông tin xe])
            A_V3([Phân nhóm xe Whitelist / Blacklist])
        end

        subgraph ADM_PARKING [4. Sơ đồ bãi đỗ & Chuyển nhượng]
            direction TB
            A_P1([Quản lý sơ đồ bãi đỗ Cinema 100 ô])
            A_P2([Phân bổ / Thu hồi ô đỗ xe])
            A_P3([Theo dõi đơn chuyển nhượng])
            A_P4([Phê duyệt / Từ chối đơn chuyển nhượng])
        end

        subgraph ADM_STATS [5. Báo cáo & Thống kê AI]
            direction TB
            A_S1([Xem Dashboard KPI vận hành])
            A_S2([Thống kê doanh thu theo ngày/tháng])
            A_S3([Phân tích mật độ lưu lượng & Giờ cao điểm])
            A_S4([Thống kê tỷ lệ nhận diện & Loại xe])
            A_S5([Xuất dữ liệu báo cáo Excel/CSV])
            A_S6([Tải ảnh thử nghiệm nhận diện AI])
        end
    end

    %% Nhóm chức năng Bảo vệ
    subgraph GUARD_FUNC [HỆ THỐNG CHỨC NĂNG CỦA BẢO VỆ]
        direction TB
        
        subgraph GUA_AUTH [1. Xác thực ca trực]
            direction TB
            G_A1([Đăng nhập ca trực])
            G_A2([Giám sát luồng Camera Live Stream])
        end

        subgraph GUA_CONTROL [2. Kiểm soát xe Vào / Ra]
            direction TB
            G_C1([Kiểm soát xe vào Check-In])
            G_C2([Kiểm soát xe ra Check-Out])
            G_C3([Đối chiếu hình ảnh Vào - Ra Side-by-Side])
            G_C4([Sửa lỗi nhận diện / Nhập biển số thủ công])
        end

        subgraph GUA_SECURITY [3. An ninh & Xử lý sự cố]
            direction TB
            G_S1([Tiếp nhận cảnh báo xe Blacklist])
            G_S2([Từ chối mở cổng & Giữ xe nghi vấn])
            G_S3([Tra cứu lịch sử xe & danh mục bãi])
        end

        subgraph GUA_FEE [4. Thu phí & Barrier]
            direction TB
            G_F1([Tra cứu cước phí tự động])
            G_F2([Xác nhận thu tiền & Xuất hóa đơn])
            G_F3([Điều khiển mở / đóng Barrier thủ công])
        end
    end

    %% Liên kết Admin
    Admin ===> ADM_AUTH
    Admin ===> ADM_USERS
    Admin ===> ADM_VEHICLES
    Admin ===> ADM_PARKING
    Admin ===> ADM_STATS

    %% Liên kết Bảo vệ
    Guard ===> GUA_AUTH
    Guard ===> GUA_CONTROL
    Guard ===> GUA_SECURITY
    Guard ===> GUA_FEE

    %% Định dạng màu sắc
    classDef adminClass fill:#fee2e2,stroke:#dc2626,stroke-width:3px,color:#7f1d1d,font-weight:bold;
    classDef guardClass fill:#fef3c7,stroke:#d97706,stroke-width:3px,color:#78350f,font-weight:bold;
    classDef funcClass fill:#ffffff,stroke:#475569,stroke-width:2px,color:#1e293b;

    class Admin adminClass;
    class Guard guardClass;
    
    class A_A1,A_A2,A_U1,A_U2,A_U3,A_U4,A_U5,A_V1,A_V2,A_V3,A_P1,A_P2,A_P3,A_P4,A_S1,A_S2,A_S3,A_S4,A_S5,A_S6 funcClass;
    class G_A1,G_A2,G_C1,G_C2,G_C3,G_C4,G_S1,G_S2,G_S3,G_F1,G_F2,G_F3 funcClass;
    
    style ADMIN_FUNC fill:#f8fafc,stroke:#cbd5e1,stroke-width:2px
    style GUARD_FUNC fill:#f8fafc,stroke:#cbd5e1,stroke-width:2px
    style ADM_AUTH fill:#e0e7ff,stroke:#6366f1,stroke-dasharray: 5 5
    style ADM_USERS fill:#e0e7ff,stroke:#6366f1,stroke-dasharray: 5 5
    style ADM_VEHICLES fill:#e0e7ff,stroke:#6366f1,stroke-dasharray: 5 5
    style ADM_PARKING fill:#e0e7ff,stroke:#6366f1,stroke-dasharray: 5 5
    style ADM_STATS fill:#e0e7ff,stroke:#6366f1,stroke-dasharray: 5 5
    
    style GUA_AUTH fill:#ffedd5,stroke:#f97316,stroke-dasharray: 5 5
    style GUA_CONTROL fill:#ffedd5,stroke:#f97316,stroke-dasharray: 5 5
    style GUA_SECURITY fill:#ffedd5,stroke:#f97316,stroke-dasharray: 5 5
    style GUA_FEE fill:#ffedd5,stroke:#f97316,stroke-dasharray: 5 5
```
