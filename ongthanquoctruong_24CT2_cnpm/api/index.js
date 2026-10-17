// ==============================================================================
// VERCEL SERVERLESS API ENGINE FOR PARKING AI
// Hỗ trợ trọn vẹn toàn bộ API cho Frontend trên Vercel:
// - /api/public/dashboard (Thống kê live real-time)
// - /api/login & /api/session & /api/logout
// - /api/register
// - /api/summary, /api/vehicles, /api/analytics/...
// - /api/admin/transfers, /api/admin/transfers/approve, /api/admin/transfers/reject
// - /api/admin/users, /api/admin/users/update
// - /api/resident/vehicles, /api/resident/history, /api/resident/...
// - /api/barrier/...
// ==============================================================================

// In-memory demo data store
let mockStats = {
  total_slots: 100,
  available_slots: 94,
  occupied_slots: 6,
  occupancy_rate: 6.0,
  ham_b1: { total: 50, available: 46, occupied: 4, pct: 8.0 },
  ham_b2: { total: 50, available: 48, occupied: 2, pct: 4.0 },
  total_vehicles: 116,
  total_plates: 42,
  total_detections: 363,
  avg_confidence: 98.5,
  total_sessions: 363,
  active_parked: 6,
  peak_hours: [
    { hour_label: "07h", count: 18, height_pct: 40 },
    { hour_label: "08h", count: 42, height_pct: 95 },
    { hour_label: "11h", count: 26, height_pct: 58 },
    { hour_label: "14h", count: 38, height_pct: 85 },
    { hour_label: "17h", count: 45, height_pct: 100 },
    { hour_label: "19h", count: 22, height_pct: 50 }
  ],
  recent_sessions: [
    { plate_text: "51F-889.99", status: "Parked", status_label: "Đang trong bãi", time_str: "09:30 15/10" },
    { plate_text: "29A-678.90", status: "Completed", status_label: "Đã hoàn tất", time_str: "14:15 14/10" }
  ]
};

let mockTransfers = [
  {
    id: "TRF-089",
    plate_text: "51F-889.99",
    vehicle_type: "Ô tô 4 chỗ (Mercedes C200)",
    from_owner: "Nguyễn Văn A",
    from_phone: "0901234567",
    from_apartment: "12.04",
    to_owner: "Trần Thị B",
    to_phone: "0912345678",
    to_apartment: "08.02",
    created_at: "15/10/2026 09:30",
    status: "Pending",
    status_label: "Chờ BQT Duyệt",
    note: "Bàn giao căn hộ chuyển quyền gửi ô tô"
  },
  {
    id: "TRF-088",
    plate_text: "29A-678.90",
    vehicle_type: "Xe máy (Honda SH 150i)",
    from_owner: "Lê Hoàng C",
    from_phone: "0934567890",
    from_apartment: "05.11",
    to_owner: "Phạm Minh D",
    to_phone: "0945678901",
    to_apartment: "05.11",
    created_at: "14/10/2026 14:15",
    status: "Pending",
    status_label: "Chờ BQT Duyệt",
    note: "Chuyển nhượng trong cùng căn hộ"
  },
  {
    id: "TRF-085",
    plate_text: "30E-123.45",
    vehicle_type: "Ô tô 5 chỗ (Mazda CX-5)",
    from_owner: "Hoàng Văn E",
    from_phone: "0966778899",
    from_apartment: "03.01",
    to_owner: "Đỗ Thị G",
    to_phone: "0977889900",
    to_apartment: "09.05",
    created_at: "12/10/2026 16:00",
    status: "Approved",
    status_label: "Đã Duyệt",
    note: "Đã xác thực hợp đồng chuyển nhượng"
  }
];

let mockUsers = [
  {
    phone: "0901234567",
    username: "cudan_1204",
    full_name: "Nguyễn Văn A",
    email: "nguyenvana@gmail.com",
    role: "Resident",
    status: "Active",
    apartment: "12.04",
    shift: "",
    created_at: "10/01/2026"
  },
  {
    phone: "0987654321",
    username: "bv_truongca",
    full_name: "Trần Bảo Vệ",
    email: "tranbaove@parking.vn",
    role: "Operator",
    status: "Active",
    apartment: "",
    shift: "Ca 1 (06h - 14h) - Cổng chính",
    created_at: "15/12/2025"
  },
  {
    phone: "0988888888",
    username: "admin_bqt",
    full_name: "Ban Quản Trị Tòa Nhà",
    email: "bqt@building.com",
    role: "Admin",
    status: "Active",
    apartment: "",
    shift: "Văn phòng BQT Tầng 1",
    created_at: "01/10/2025"
  }
];

let mockVehicles = [
  { id: 1, plate_text: "51F-889.99", vehicle_type: "Ô tô", owner_name: "Nguyễn Văn A", apartment: "12.04", slot_code: "B1-05", status: "Active", expiry: "31/12/2026" },
  { id: 2, plate_text: "29A-678.90", vehicle_type: "Xe máy", owner_name: "Lê Hoàng C", apartment: "05.11", slot_code: "B2-12", status: "Active", expiry: "15/11/2026" },
  { id: 3, plate_text: "30E-123.45", vehicle_type: "Ô tô", owner_name: "Đỗ Thị G", apartment: "09.05", slot_code: "B1-18", status: "Active", expiry: "28/02/2027" }
];

// Helper parse body
async function getRequestBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string" && req.body.length > 0) {
    try { return JSON.parse(req.body); } catch (_) {}
  }
  return new Promise((resolve) => {
    let data = "";
    req.on("data", chunk => { data += chunk; });
    req.on("end", () => {
      try { resolve(JSON.parse(data)); } catch (_) { resolve({}); }
    });
  });
}

// Main handler
export default async function handler(req, res) {
  // CORS Headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    res.status(200).end();
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  let pathname = url.pathname;

  // Chuẩn hóa path
  if (!pathname.startsWith("/api")) {
    pathname = "/api" + pathname;
  }

  // 1. PUBLIC DASHBOARD STATS
  if (pathname === "/api/public/dashboard" || pathname === "/api/public/stats") {
    return res.status(200).json({ success: true, stats: mockStats });
  }

  // 2. AUTHENTICATION (LOGIN, SESSION, LOGOUT)
  if (pathname === "/api/login" && req.method === "POST") {
    const body = await getRequestBody(req);
    const phone = (body.phone || body.username || "").trim();
    const password = body.password || "";

    if (!phone || !password) {
      return res.status(400).json({ error: "Vui lòng nhập số điện thoại và mật khẩu" });
    }

    // Phân loại role theo tài khoản
    let role = "Admin";
    let fullName = "Ban Quản Trị Admin";
    let redirectUrl = "/operations-dashboard";

    if (phone.toLowerCase().includes("cudan") || phone === "0901234567") {
      role = "Resident";
      fullName = "Cư Dân Nguyễn Văn A";
      redirectUrl = "/resident-dashboard";
    } else if (phone.toLowerCase().includes("bv") || phone === "0987654321") {
      role = "Operator";
      fullName = "Trần Bảo Vệ (Ca 1)";
      redirectUrl = "/operations-dashboard";
    }

    const userObj = {
      id: 1,
      username: phone,
      full_name: fullName,
      phone: phone,
      role: role,
      email: `${phone}@parking.vn`
    };

    // Set cookie
    res.setHeader("Set-Cookie", `auth_user=${encodeURIComponent(JSON.stringify(userObj))}; Path=/; HttpOnly; SameSite=Lax`);
    return res.status(200).json({ success: true, user: userObj, redirect: redirectUrl });
  }

  if (pathname === "/api/session") {
    // Mặc định trả về Admin để demo đầy đủ tính năng nếu chưa đăng nhập
    return res.status(200).json({
      authenticated: true,
      user: {
        id: 1,
        username: "admin_bqt",
        full_name: "Ban Quản Trị Tòa Nhà",
        role: "Admin",
        email: "admin@parking.vn"
      }
    });
  }

  if (pathname === "/api/logout") {
    res.setHeader("Set-Cookie", "auth_user=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT");
    return res.status(200).json({ success: true, message: "Đã đăng xuất" });
  }

  // 3. REGISTER
  if (pathname === "/api/register" && req.method === "POST") {
    const body = await getRequestBody(req);
    if (!body.phone || !body.password) {
      return res.status(400).json({ error: "Vui lòng điền đầy đủ số điện thoại và mật khẩu" });
    }
    return res.status(200).json({
      success: true,
      message: "Đăng ký tài khoản thành công!",
      redirect: "/login"
    });
  }

  // 4. ADMIN: CHUYỂN NHƯỢNG XE (TRANSFER REQUESTS)
  if (pathname === "/api/admin/transfers" || pathname === "/api/admin/transfer-requests") {
    return res.status(200).json({ success: true, transfers: mockTransfers });
  }

  if (pathname === "/api/admin/transfers/approve" && req.method === "POST") {
    const body = await getRequestBody(req);
    const id = body.id || body.transfer_id || "TRF-089";
    const target = mockTransfers.find(t => t.id === id);
    if (target) {
      target.status = "Approved";
      target.status_label = "Đã Duyệt";
    }
    return res.status(200).json({
      success: true,
      message: `Đã phê duyệt thành công đơn chuyển nhượng #${id}!`,
      transfer: target
    });
  }

  if (pathname === "/api/admin/transfers/reject" && req.method === "POST") {
    const body = await getRequestBody(req);
    const id = body.id || body.transfer_id || "TRF-088";
    const target = mockTransfers.find(t => t.id === id);
    if (target) {
      target.status = "Rejected";
      target.status_label = "Đã Từ Chối";
      target.reject_reason = body.reason || "Hồ sơ chưa hợp lệ";
    }
    return res.status(200).json({
      success: true,
      message: `Đã từ chối đơn chuyển nhượng #${id}`,
      transfer: target
    });
  }

  // 5. ADMIN: QUẢN LÝ NGƯỜI DÙNG & PHÂN QUYỀN (USERS & PERMISSIONS)
  if (pathname === "/api/admin/users") {
    if (req.method === "POST" || req.method === "PUT") {
      const body = await getRequestBody(req);
      const phone = body.phone || body.so_dien_thoai;
      const user = mockUsers.find(u => u.phone === phone);
      if (user) {
        if (body.role) user.role = body.role;
        if (body.status) user.status = body.status;
        if (body.full_name) user.full_name = body.full_name;
        if (body.shift) user.shift = body.shift;
        if (body.apartment) user.apartment = body.apartment;
      }
      return res.status(200).json({ success: true, message: "Cập nhật tài khoản & phân quyền thành công!", user });
    }
    return res.status(200).json({ success: true, users: mockUsers });
  }

  // 6. OPERATIONS & VEHICLES
  if (pathname === "/api/summary") {
    return res.status(200).json({
      total_vehicles: 116,
      parked_vehicles: 6,
      today_revenue: "1.450.000 đ",
      total_slots: 100,
      free_slots: 94
    });
  }

  if (pathname === "/api/vehicles") {
    return res.status(200).json(mockVehicles);
  }

  if (pathname === "/get_plates") {
    return res.status(200).json([
      { id: 1, plate_text: "51F-889.99", vehicle_type: "Ô tô", confidence: 0.988, timestamp: new Date().toISOString(), gate: "In" },
      { id: 2, plate_text: "29A-678.90", vehicle_type: "Xe máy", confidence: 0.975, timestamp: new Date().toISOString(), gate: "Out" },
      { id: 3, plate_text: "30E-123.45", vehicle_type: "Ô tô", confidence: 0.992, timestamp: new Date().toISOString(), gate: "In" }
    ]);
  }

  // 7. ANALYTICS (CHARTS)
  if (pathname === "/api/analytics/revenue") {
    return res.status(200).json([
      { date_revenue: "11/10", total_fee: 1200000 },
      { date_revenue: "12/10", total_fee: 1450000 },
      { date_revenue: "13/10", total_fee: 1300000 },
      { date_revenue: "14/10", total_fee: 1600000 },
      { date_revenue: "15/10", total_fee: 1850000 },
      { date_revenue: "16/10", total_fee: 1400000 },
      { date_revenue: "17/10", total_fee: 1550000 }
    ]);
  }

  if (pathname === "/api/analytics/peak-hours") {
    return res.status(200).json([
      { scan_hour: 7, scan_count: 24 },
      { scan_hour: 8, scan_count: 52 },
      { scan_hour: 11, scan_count: 31 },
      { scan_hour: 14, scan_count: 40 },
      { scan_hour: 17, scan_count: 65 },
      { scan_hour: 19, scan_count: 28 }
    ]);
  }

  // 8. RESIDENT APIs
  if (pathname.startsWith("/api/resident/vehicles")) {
    return res.status(200).json({
      success: true,
      vehicles: [
        { plate_text: "51F-889.99", vehicle_type: "Ô tô 4 chỗ", slot_code: "B1-05", expiry: "31/12/2026", status: "Active" }
      ]
    });
  }

  if (pathname === "/api/resident/history") {
    return res.status(200).json({
      success: true,
      history: [
        { plate_text: "51F-889.99", check_in: "08:15 17/10", check_out: "Đang đỗ", gate: "Cổng Vào #1", status: "Parked" },
        { plate_text: "51F-889.99", check_in: "07:30 16/10", check_out: "18:45 16/10", gate: "Cổng Ra #1", status: "Completed" }
      ]
    });
  }

  if (pathname === "/api/resident/transfer-request" && req.method === "POST") {
    const body = await getRequestBody(req);
    const newId = `TRF-${Math.floor(100 + Math.random() * 900)}`;
    const newTransfer = {
      id: newId,
      plate_text: body.plate_text || "51F-889.99",
      from_owner: "Nguyễn Văn A (Căn 12.04)",
      to_owner: body.to_owner || "Trần Thị B",
      to_phone: body.to_phone || "0912345678",
      to_apartment: body.to_apartment || "08.02",
      created_at: new Date().toLocaleString("vi-VN"),
      status: "Pending",
      status_label: "Chờ BQT Duyệt"
    };
    mockTransfers.unshift(newTransfer);
    return res.status(200).json({ success: true, message: "Đã gửi đơn chuyển nhượng tới Ban Quản Trị!", transfer_id: newId });
  }

  if (pathname === "/api/resident/renew_ticket" && req.method === "POST") {
    const body = await getRequestBody(req);
    return res.status(200).json({
      success: true,
      message: "Gia hạn vé tháng thành công!",
      new_expiry: "30/06/2027"
    });
  }

  // 9. BARRIER CONTROL
  if (pathname.startsWith("/api/barrier/")) {
    return res.status(200).json({ success: true, message: "Lệnh điều khiển barrier đã thực thi thành công" });
  }

  // Default fallback for any other API
  return res.status(200).json({ success: true, message: "Parking AI Vercel API is running" });
}
