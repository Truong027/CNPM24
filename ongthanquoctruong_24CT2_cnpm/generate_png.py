import base64
import zlib
import urllib.request
import os

plantuml_code = """
@startuml
skinparam shadowing false
skinparam defaultFontName Arial
skinparam usecase {
    BackgroundColor #F0F8FF
    BorderColor #4682B4
    ArrowColor #4682B4
}
skinparam actor {
    BackgroundColor #FFD700
    BorderColor #DAA520
}

actor "Quản Trị Viên (Admin)" as Admin
actor "Bảo Vệ (Guard)" as Guard
actor "Cư Dân (User)" as User

package "Quản Lý Hệ Thống" {
    usecase "Quản lý Người Dùng & Cấp Tài Khoản" as UC_Admin1
    usecase "Quản lý Danh mục Phương Tiện\\n(Whitelist/Blacklist)" as UC_Admin2
    usecase "Phân bổ Sơ Đồ Bãi Đỗ Xe Cinema" as UC_Admin3
    usecase "Phê Duyệt Đơn Chuyển Nhượng" as UC_Admin4
    usecase "Xem Báo Cáo Thống Kê & Doanh Thu" as UC_Admin5
}

package "Nghiệp Vụ Bàn Trực" {
    usecase "Giám Sát Camera Live & Nhận Diện AI" as UC_Guard1
    usecase "Kiểm Soát Xe Vào / Ra (Check-in/Check-out)" as UC_Guard2
    usecase "Xử Lý Xe Vi Phạm / Cảnh Báo Blacklist" as UC_Guard3
    usecase "Tra Cứu Cước Phí & Thu Tiền" as UC_Guard4
    usecase "Điều Khiển Đóng/Mở Barrier" as UC_Guard5
}

package "Tiện Ích Cư Dân" {
    usecase "Đăng Ký & Quản Lý Xe Căn Hộ" as UC_User1
    usecase "Mua & Gia Hạn Vé Tháng" as UC_User2
    usecase "Chọn & Đổi Vị Trí Đỗ Xe Cinema" as UC_User3
    usecase "Tra Cứu Lịch Sử Vào/Ra Của Mình" as UC_User4
    usecase "Tạo Đơn Yêu Cầu Chuyển Nhượng Xe" as UC_User5
}

Admin -down-> UC_Admin1
Admin -down-> UC_Admin2
Admin -down-> UC_Admin3
Admin -down-> UC_Admin4
Admin -down-> UC_Admin5

Guard -down-> UC_Guard1
Guard -down-> UC_Guard2
Guard -down-> UC_Guard3
Guard -down-> UC_Guard4
Guard -down-> UC_Guard5

User -down-> UC_User1
User -down-> UC_User2
User -down-> UC_User3
User -down-> UC_User4
User -down-> UC_User5

@enduml
"""

# Compress and encode
compressed = zlib.compress(plantuml_code.encode('utf-8'))
encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')

# Kroki URL
url = f"https://kroki.io/plantuml/png/{encoded}"

print(f"Fetching from {url}")

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        with open(r"d:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\docs\diagram.png", "wb") as f:
            f.write(response.read())
    print("Thanh cong")
except Exception as e:
    print(e)
