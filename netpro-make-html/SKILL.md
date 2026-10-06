---
name: netpro-make-html
description: "Tạo file HTML giải thích kiến trúc/khái niệm kỹ thuật trực quan chuẩn phong cách Netpro: giao diện Dark mode công nghệ hiện đại, chữ to rõ ràng, ít chữ nhiều sơ đồ khối, animation chuyển động sống động (particle stream, glowing flow), bảng mô phỏng tương tác (interactive simulation/benchmark), không lỗi LaTeX, tự động đặt tên file và lưu vào thư mục chỉ định."
---

# Netpro Make HTML Skill

## 1. Tổng quan (Overview)
Skill này chuyên trách việc tạo ra các trang HTML giải thích kiến thức kỹ thuật, hệ thống phân tán, kiến trúc cơ sở dữ liệu và công nghệ phần mềm theo **tiêu chuẩn thiết kế Netpro**:
- **Trực quan hóa tối đa**: Ít chữ, nhiều sơ đồ khối (Block Architecture Diagrams).
- **Chữ to, rõ ràng**: Cỡ chữ lớn (17px - 18px), không dùng chữ li ti gây mỏi mắt.
- **Có Animation chuyển động sống động**: Mô phỏng dòng dữ liệu chạy trên đường ống (Particle Stream), luồng sáng phát quang (Glow effect), hạt trôi mượt mà 60 FPS.
- **Mô phỏng tương tác trực tiếp (Interactive Simulation / Benchmark)**: Có các nút bấm thử nghiệm các chế độ, đo lường CPU/FPS, số liệu nhảy theo thời gian thực.
- **Không bao giờ lỗi hiển thị ký tự**: Tuyệt đối không dùng cú pháp LaTeX thô (`$\rightarrow$`). 100% dùng Unicode (`→`) hoặc FontAwesome icons.

---

## 2. Đầu vào (Inputs) & Tự Động Đặt Tên File

Khi người dùng kích hoạt skill hoặc yêu cầu giải thích một chủ đề:
1. **Nội dung / Chủ đề (`content`)**: Khái niệm kỹ thuật, kiến trúc, cơ chế cần giải thích (ví dụ: WAL, Realtime 1M Ops, LRU Cache, CDC, Kafka Partitioning, Sharding...).
2. **Thư mục lưu file (`output_dir`)**: Đường dẫn thư mục đích (ví dụ: `htmls/Bai01/`, `htmls/Bai02/`, `docs/visuals/`...). Nếu người dùng chưa chỉ định, mặc định lưu vào thư mục hiện tại hoặc `htmls/Bai01/`.
3. **Tên file HTML (`filename`)**: **Skill tự động đặt tên file** dựa theo nội dung chủ đề:
   - Dùng tiếng Việt rõ nghĩa, dễ hiểu (ví dụ: `Cập nhật bảng Realtime triệu thay đổi mỗi giây.html`, `Giải thích về WAL.html`, `Cơ chế bộ nhớ đệm LRU Cache.html`).
   - Đảm bảo có đuôi `.html`.

---

## 3. Quy chuẩn Thiết kế Bắt buộc (Design System Standards)

### 3.1. Thư viện & Fonts (Dùng CDN, độc lập 100% không cần build tool)
- **Tailwind CSS**: `<script src="https://cdn.tailwindcss.com"></script>`
- **Google Fonts**: `Plus Jakarta Sans` (weights 500, 600, 700, 800, 900) cho tiêu đề và nội dung; `JetBrains Mono` (weights 600, 800) cho số liệu, code và trạng thái.
- **Font Awesome 6.5.1**: `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">`

### 3.2. Bảng màu chuẩn (Dark Tech Palette)
- **Nền chính**: `#070b14` (Deep Space Dark)
- **Khối bề mặt (Panel / Card)**: `#0f172a` hoặc `#0e1626` với `border: 1px solid rgba(255, 255, 255, 0.1)` và hiệu ứng Glassmorphism (`backdrop-filter: blur(12px)`).
- **Màu nhấn trạng thái**:
  - `Rose / Red (#f43f5e)`: Điểm nghẽn, cách cũ, nguy hiểm, quá tải, sập nguồn.
  - `Amber / Orange (#f59e0b)`: Bộ lọc, quá trình trung gian, xử lý, chú ý.
  - `Cyan / Blue (#06b6d4, #38bdf8)`: Đường truyền, mạng, giao thức, tốc độ.
  - `Emerald / Green (#10b981)`: Cách chuẩn, tối ưu, thành công, 60 FPS, mượt mà.
  - `Violet / Purple (#8b5cf6)`: Bộ nhớ RAM, cấu trúc dữ liệu.

### 3.3. Quy tắc Cỡ Chữ & Khoảng Cách Đệm (Padding & Line-Height Bắt Buộc)
- **Khoảng cách đệm (Padding) & Giãn dòng (Line-height)**:
  - Thẻ `body`: Bắt buộc có `line-height: 1.75;` hoặc `leading-relaxed`.
  - Tiêu đề (`h1`, `h2`, `h3`): Bắt buộc dùng `leading-normal` hoặc `leading-snug`, TUYỆT ĐỐI KHÔNG dùng `leading-tight` gây dính chữ sát nhau giữa 2 dòng.
  - Khoảng cách giữa Tiêu đề và Mô tả bên dưới: Tối thiểu `space-y-6` hoặc `my-6`, có khoảng thở rộng rãi.
  - Padding trong các khối/card: Dùng `p-8 md:p-10` hoặc `p-8 md:p-12`. Khoảng cách giữa các card: `gap-8`.
  - Khoảng cách giữa các phần lớn: `space-y-20` và `py-14`.
- **Cỡ chữ**:
  - Body / Đoạn văn bản trong thẻ: Tối thiểu `17px - 18px` (`text-base md:text-lg`).
  - Tiêu đề mục (Section Heading): `text-2xl md:text-4xl font-black`.
  - Tiêu đề chính (Page Title): `text-3xl md:text-5xl font-black`.
  - Chỉ số số liệu (Metrics / Numbers): `text-2xl` đến `text-4xl font-mono font-bold`.

### 3.4. Quy tắc BẮT BUỘC về Ký tự và Mũi tên (Zero LaTeX Error)
- **TUYỆT ĐỐI KHÔNG DÙNG**: `$\rightarrow$`, `$\Rightarrow$`, `$\dots$`, `$1000$`.
- **BẮT BUỘC DÙNG**:
  - Mũi tên Unicode: `→`, `⇒`, `↔`
  - FontAwesome icon: `<i class="fa-solid fa-arrow-right text-cyan-400 mx-1"></i>`
  - Ký hiệu tiền tệ: `$1000` viết trực tiếp không dùng escape latex.

### 3.5. Quy tắc BẮT BUỘC Viết Rõ Thuật Ngữ Tiếng Anh Viết Tắt (Acronym Expansion)
- **Tuyệt đối không để từ viết tắt cộc lốc** khi độc giả tiếp cận kiến thức (như `RDB`, `TPS`, `AOF`, `RESP`, `IOPS`, `OOM`, `TTL`, `LRU`, `LFU`, `WAL`, `COW`...).
- **BẮT BUỘC viết đầy đủ tên tiếng Anh kèm giải thích tiếng Việt** rõ ràng ngay tại tiêu đề, nhãn hoặc đoạn mở đầu:
  - Ví dụ:
    - `RDB` → **RDB (Redis Database - Sao lưu ảnh chụp snapshot định kỳ)**
    - `TPS` → **TPS (Transactions Per Second - Số giao dịch xử lý mỗi giây)**
    - `AOF` → **AOF (Append-Only File - Tệp ghi nhật ký nối tiếp)**
    - `RESP` → **RESP (REdis Serialization Protocol - Giao thức tuần tự hóa dữ liệu Redis)**
    - `IOPS` → **IOPS (Input/Output Operations Per Second - Số tác vụ đọc/ghi đĩa mỗi giây)**
    - `TTL` → **TTL (Time To Live - Thời gian sống của dữ liệu)**
    - `OOM` → **OOM (Out Of Memory - Tràn bộ nhớ)**
    - `LRU / LFU` → **LRU (Least Recently Used - Lâu nhất không dùng) / LFU (Least Frequently Used - Ít tần suất sử dụng nhất)**

### 3.6. Quy tắc BẮT BUỘC về Công Thức Giao Thức & Cấu Trúc Dữ Liệu (Protocol & Serialization Formula)
- Khi giải thích các câu lệnh ghi tệp, gói tin mạng, hoặc giao thức tuần tự hóa (ví dụ: RESP của Redis, binary format, packet header):
  - **Phải có công thức tổng quát và quy ước ký hiệu**:
    - `*<N>`: Mảng gồm `<N>` phần tử / tham số (Array).
    - `$<Len>`: Độ dài chuỗi (Bulk String) có độ dài `<Len>` ký tự/bytes.
    - `\r\n`: Dấu ngắt dòng chuẩn CRLF (Carriage Return + Line Feed).
  - **Phải có sơ đồ bóc tách trực quan từng thành phần của câu lệnh mẫu**:
    - Ví dụ lệnh tăng: `*2\r\n$4\r\nINCR\r\n$10\r\nview_count\r\n` (bóc tách: `*2` là 2 tham số, `$4` độ dài lệnh, `INCR` tên lệnh, `$10` độ dài key, `view_count` tên key).
    - Ví dụ lệnh gán: `*3\r\n$3\r\nSET\r\n$10\r\nview_count\r\n$7\r\n1000000\r\n`.
  - Thiết kế thành các khối thẻ trực quan dạng giải phẫu (dissected blocks) với màu sắc neon phân biệt rõ từng phần.

---

## 4. Bố Cục Trang HTML Mẫu (Page Blueprint)

Mỗi file HTML sinh ra PHẢI tuân thủ cấu trúc 5 phần chuẩn sau:

1. **Header**:
   - Icon logo nổi bật có bóng đổ neon (`shadow-xl shadow-cyan-500/25`).
   - Tên chủ đề rõ ràng kèm nhãn badge công nghệ.
2. **Phần 1: Bài Toán Cốt Lõi / Bản Chất Vấn Đề**:
   - 3 Card lớn song song trình bày nguyên nhân vì sao cách thông thường thất bại và chìa khóa giải quyết.
3. **Phần 2: Sơ Đồ Khối Toàn Cảnh (The Big Picture Architecture)**:
   - 3 đến 4 khối kiến trúc lớn được đóng khung màu tương ứng.
   - **Thanh Animation dòng chảy hạt (Animated Pipeline Track)**:
     - Phía đầu vào: Hạt đỏ bay dồn dập (tượng trưng cho tải lớn).
     - Ở giữa: Phễu lọc/Khối xử lý hấp thụ (Conflation / Buffer).
     - Phía đầu ra: Hạt xanh ngọc lướt êm ái, nhịp nhàng (60 FPS mượt mà).
4. **Phần 3: Bảng Đối Chiếu "Cách Cũ vs Cách Chuẩn Tải Cao"**:
   - 4 cặp so sánh trực diện (Giao thức, Định dạng dữ liệu, Cách gửi, Cách render UI).
   - Dùng icon dấu chéo đỏ `<i class="fa-solid fa-circle-xmark">` và dấu tích xanh `<i class="fa-solid fa-circle-check">`.
5. **Phần 4: Bảng Demo Thử Nghiệm Mô Phỏng Tương Tác**:
   - Viết JavaScript thuần mô phỏng chạy thời gian thực.
   - Có ít nhất 2 nút bấm: **"Chế độ Cũ"** (gây quá tải, lag, cảnh báo đỏ) và **"Chế độ Chuẩn"** (chạy êm 60 FPS, CPU thấp).
   - Có bảng số liệu hoặc đồ thị nhảy số liên tục.
6. **Phần 5: Tóm Gọn 3 Bước Hành Động Cụ Thể**:
   - 3 bước xúc tích để áp dụng ngay vào dự án thật.

---

## 5. Quy Trình Thực Thi Của Agent (Step-by-Step Execution)

Khi nhận yêu cầu:
1. **Phân tích yêu cầu**: Xác định chủ đề, các tầng kiến trúc cốt lõi và thư mục đích `output_dir`.
2. **Đặt tên file**: Tạo tên file tiếng Việt ngắn gọn, giàu ý nghĩa, có đuôi `.html` (ví dụ: `Cập nhật bảng Realtime triệu thay đổi mỗi giây.html`).
3. **Tạo thư mục**: Dùng lệnh shell tạo thư mục nếu chưa tồn tại (`mkdir -p "<output_dir>"`).
4. **Soạn thảo code HTML**:
   - Tích hợp đầy đủ CSS, animations, JavaScript tương tác trực tiếp theo chuẩn thiết kế Netpro ở trên.
   - Kiểm tra kỹ không chứa bất kỳ chuỗi `$\rightarrow$` hay ký hiệu LaTeX nào.
5. **Ghi file**: Dùng `write_to_file` để ghi file vào đúng đường dẫn `<output_dir>/<filename>`.
6. **Báo cáo kết quả**: Cung cấp link markdown trực tiếp đến file (`[Tên File](file:///đường_dẫn_tuyệt_đối)`) và tóm tắt ngắn gọn các điểm trực quan hóa nổi bật.
