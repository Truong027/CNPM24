# BÀI TẬP TÌM ĐƯỜNG GĂNG - SƠ ĐỒ MẠNG PERT (ĐỀ 1)

- **Họ và tên:** Trần Quốc Trung
- **Lớp:** 24CT1
- **Đề bài:** Đề 1. Em hãy tìm đường găng và thời gian hoàn thành dự án theo sơ đồ Pert
- **Tệp sơ đồ Draw.io:** [`SO_DO_PERT_DE_1.drawio`](SO_DO_PERT_DE_1.drawio)
- **Hình ảnh kết xuất PNG:** [`SO_DO_PERT_DE_1.drawio.png`](SO_DO_PERT_DE_1.drawio.png)

---

## 1. Bảng số liệu đầu vào (Đề 1 - Trích từ Slide bài tập)

| STT | Viết tắt | Tên công việc | Thời gian ($t$) | Công việc tiên quyết |
|:---:|:---:|:---|:---:|:---:|
| 1 | **A** | $t_A$ | 8 | - |
| 2 | **B** | $t_B$ | 9 | - |
| 3 | **C** | $t_C$ | 12 | - |
| 4 | **D** | $t_D$ | 6 | A |
| 5 | **E** | $t_E$ | 9 | B |
| 6 | **F** | $t_F$ | 7 | B, C |
| 7 | **G** | $t_G$ | 15 | B, D |
| 8 | **H** | $t_H$ | 4 | E, G |
| 9 | **I** | $t_I$ | 6 | F |
| 10 | **J** | $t_J$ | 9 | G, I, F |

> **Quy ước công việc giả (Dummy Activities - Nét đứt, thời gian $t_{cv} = 0$):**
> - $t'_B$ từ sự kiện $2 \to 4$ (phục vụ ràng buộc $G$ sau $B, D$).
> - $t'_B$ từ sự kiện $2 \to 3$ (phục vụ ràng buộc $F$ sau $B, C$).
> - $t'_G$ từ sự kiện $7 \to 5$ (phục vụ ràng buộc $H$ sau $E, G$ — sửa lỗi không vẽ lặp $t_G (15)$ 2 lần).
> - $t'_G$ từ sự kiện $7 \to 8$ (phục vụ ràng buộc $J$ sau $G, I, F$ — chuyển về sau khi $G$ kết thúc tại sự kiện $7$).
> - $t'_F$ từ sự kiện $3 \to 8$ (phục vụ ràng buộc $J$ sau $G, I, F$).

---

## 2. Các bước tính toán chi tiết (Theo giáo trình CNPM - trang 8 & 9)

### a. Tính thời gian sớm nhất của mỗi đỉnh $t_s(i)$ (Trang 8 - Chiều xuôi)
Công thức: $t_s(0) = 0$; $\quad t_s(\text{đỉnh } i) = \max\{t_s(\text{đỉnh đầu cv}) + t_{cv}\}$ (đối với mọi công việc đi vào đỉnh $i$).

- $t_s(0) = \mathbf{0}$
- $t_s(1) = \max\{t_s(0) + t_A\} = \max\{0 + 8\} = \mathbf{8}$
- $t_s(2) = \max\{t_s(0) + t_B\} = \max\{0 + 9\} = \mathbf{9}$
- $t_s(3) = \max\{t_s(0) + t_C \,;\, t_s(2) + t'_B\} = \max\{0 + 12 \,;\, 9 + 0\} = \mathbf{12}$
- $t_s(4) = \max\{t_s(1) + t_D \,;\, t_s(2) + t'_B\} = \max\{8 + 6 \,;\, 9 + 0\} = \mathbf{14}$
- **$t_s(7) = \max\{t_s(4) + t_G\} = \max\{14 + 15\} = \mathbf{29}$** *(đỉnh kết thúc công việc $G$)*
- $t_s(5) = \max\{t_s(2) + t_E \,;\, t_s(7) + t'_G\} = \max\{9 + 9 \,;\, 29 + 0\} = \max\{18 \,;\, 29\} = \mathbf{29}$
- $t_s(6) = \max\{t_s(3) + t_F\} = \max\{12 + 7\} = \mathbf{19}$
- $t_s(8) = \max\{t_s(6) + t_I \,;\, t_s(3) + t'_F \,;\, t_s(7) + t'_G\} = \max\{19 + 6 \,;\, 12 + 0 \,;\, 29 + 0\} = \max\{25 \,;\, 12 \,;\, 29\} = \mathbf{29}$
- $t_s(9) = \max\{t_s(5) + t_H \,;\, t_s(8) + t_J\} = \max\{29 + 4 \,;\, 29 + 9\} = \max\{33 \,;\, 38\} = \mathbf{38}$

### b. Tính thời gian muộn nhất của mỗi đỉnh $t_m(i)$ (Trang 8 - Chiều ngược)
Công thức: $t_m(n) = t_s(n)$; $\quad t_m(\text{đỉnh } i) = \min\{t_m(\text{đỉnh cuối cv}) - t_{cv}\}$ (đối với mọi công việc đi ra khỏi đỉnh $i$).

- $t_m(9) = t_s(9) = \mathbf{38}$
- $t_m(8) = \min\{t_m(9) - t_J\} = 38 - 9 = \mathbf{29}$
- $t_m(6) = \min\{t_m(8) - t_I\} = 29 - 6 = \mathbf{23}$
- $t_m(5) = \min\{t_m(9) - t_H\} = 38 - 4 = \mathbf{34}$
- **$t_m(7) = \min\{t_m(5) - t'_G \,;\, t_m(8) - t'_G\} = \min\{34 - 0 \,;\, 29 - 0\} = \mathbf{29}$** *(nằm trên đường găng)*
- $t_m(4) = \min\{t_m(7) - t_G\} = 29 - 15 = \mathbf{14}$
- $t_m(3) = \min\{t_m(6) - t_F \,;\, t_m(8) - t'_F\} = \min\{23 - 7 \,;\, 29 - 0\} = \min\{16 \,;\, 29\} = \mathbf{16}$
- $t_m(2) = \min\{t_m(4) - t'_B \,;\, t_m(5) - t_E \,;\, t_m(3) - t'_B\} = \min\{14 - 0 \,;\, 34 - 9 \,;\, 16 - 0\} = \mathbf{14}$
- $t_m(1) = \min\{t_m(4) - t_D\} = 14 - 6 = \mathbf{8}$
- $t_m(0) = \min\{t_m(1) - t_A \,;\, t_m(2) - t_B \,;\, t_m(3) - t_C\} = \min\{8 - 8 \,;\, 14 - 9 \,;\, 16 - 12\} = \mathbf{0}$

### c. Tính thời gian dự phòng của mỗi công việc $t_{df}(cv)$ (Trang 9)
Công thức: $t_{df}(cv) = t_m(\text{đỉnh cuối cv}) - t_s(\text{đỉnh đầu cv}) - t_{cv}$. Công việc găng là công việc có $t_{df}(cv) = 0$.

| Công việc ($cv$) | Cung ($i \to j$) | Thời gian ($t_{cv}$) | $t_s(\text{đỉnh đầu})$ | $t_m(\text{đỉnh cuối})$ | Dự phòng $t_{df}(cv)$ | Công việc găng |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$t_A$** | $0 \to 1$ | 8 | 0 | 8 | $8 - 0 - 8 = \mathbf{0}$ | **GĂNG** |
| $t_B$ | $0 \to 2$ | 9 | 0 | 14 | $14 - 0 - 9 = 5$ | Không |
| $t_C$ | $0 \to 3$ | 12 | 0 | 16 | $16 - 0 - 12 = 4$ | Không |
| **$t_D$** | $1 \to 4$ | 6 | 8 | 14 | $14 - 8 - 6 = \mathbf{0}$ | **GĂNG** |
| $t'_B$ *(giả)* | $2 \to 4$ | 0 | 9 | 14 | $14 - 9 - 0 = 5$ | Không |
| $t'_B$ *(giả)* | $2 \to 3$ | 0 | 9 | 16 | $16 - 9 - 0 = 7$ | Không |
| $t_E$ | $2 \to 5$ | 9 | 9 | 34 | $34 - 9 - 9 = 16$ | Không |
| $t_F$ | $3 \to 6$ | 7 | 12 | 23 | $23 - 12 - 7 = 4$ | Không |
| $t'_F$ *(giả)* | $3 \to 8$ | 0 | 12 | 29 | $29 - 12 - 0 = 17$ | Không |
| **$t_G$** | $4 \to 7$ | 15 | 14 | 29 | $29 - 14 - 15 = \mathbf{0}$ | **GĂNG** |
| $t'_G$ *(giả)* | $7 \to 5$ | 0 | 29 | 34 | $34 - 29 - 0 = 5$ | Không |
| **$t'_G$ *(giả)*** | $7 \to 8$ | 0 | 29 | 29 | $29 - 29 - 0 = \mathbf{0}$ | **GĂNG *(nối đường găng)*** |
| $t_H$ | $5 \to 9$ | 4 | 29 | 38 | $38 - 29 - 4 = 5$ | Không |
| $t_I$ | $6 \to 8$ | 6 | 19 | 29 | $29 - 19 - 6 = 4$ | Không |
| **$t_J$** | $8 \to 9$ | 9 | 29 | 38 | $38 - 29 - 9 = \mathbf{0}$ | **GĂNG** |

---

## 3. Bảng tổng hợp tham số các đỉnh (Sự kiện)

| Đỉnh $(i)$ | $t_s(i)$ (Sớm nhất) | $t_m(i)$ (Muộn nhất) | Dự trữ đỉnh ($t_m - t_s$) | Thuộc đường găng |
|:---:|:---:|:---:|:---:|:---:|
| **[ 0 ]** | **0** | **0** | **0** | **GĂNG (BẮT ĐẦU)** |
| **( 1 )** | **8** | **8** | **0** | **GĂNG** |
| ( 2 ) | 9 | 14 | 5 | Không |
| ( 3 ) | 12 | 16 | 4 | Không |
| **( 4 )** | **14** | **14** | **0** | **GĂNG** |
| ( 5 ) | 29 | 34 | 5 | Không |
| ( 6 ) | 19 | 23 | 4 | Không |
| **( 7 )** | **29** | **29** | **0** | **GĂNG** |
| **( 8 )** | **29** | **29** | **0** | **GĂNG** |
| **[ 9 ]** | **38** | **38** | **0** | **GĂNG (KẾT THÚC)** |

---

## 4. Kết luận

- **Đường găng (Critical Path):**
  $$A \rightarrow D \rightarrow G \rightarrow J \quad (\text{qua cung giả } t'_G: 7 \to 8)$$
- **Chuỗi sự kiện (đỉnh) nằm trên đường găng:**
  $$[0] \rightarrow (1) \rightarrow (4) \rightarrow (7) \xrightarrow{t'_G} (8) \rightarrow [9]$$
- **Độ dài đường găng / Thời gian hoàn thành dự án ngắn nhất ($T_{max}$):**
  $$T_{max} = t_A + t_D + t_G + t'_G + t_J = 8 + 6 + 15 + 0 + 9 = \mathbf{38} \text{ (ngày)}$$
