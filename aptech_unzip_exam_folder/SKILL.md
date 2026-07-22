---
name: aptech_unzip_exam_folder
description: "Dọn dẹp và làm phẳng cấu trúc thư mục bài thi. Nếu một thư mục thí sinh (Ti) chỉ chứa duy nhất một thư mục con (X), nó sẽ di chuyển toàn bộ nội dung của X ra ngoài Ti và xóa thư mục X trống."
---

# Aptech Unzip Exam Folder (Làm phẳng cấu trúc thư mục bài thi)

## Overview
Skill này được sử dụng khi người dùng cung cấp một thư mục chứa nhiều bài làm của thí sinh (ví dụ: `C:\Users\nguye\Downloads\Bài làm`). Đôi khi bài làm bị nén trong một thư mục lồng nhau (một thư mục con duy nhất bên trong thư mục bài làm). Skill này sẽ giúp loại bỏ thư mục lồng đó bằng cách chuyển toàn bộ file/folder ra ngoài và xóa thư mục rỗng.

## Hướng dẫn các bước cho Agent

Khi skill này được gọi (ví dụ: "/aptech_unzip_exam_folder thư mục C:\..."), bạn hãy thực hiện theo trình tự sau:

### Bước 1: Xác định thư mục gốc
- Đọc tham số đường dẫn thư mục mà người dùng cung cấp. Đảm bảo đường dẫn này tồn tại.

### Bước 2: Chạy script xử lý
Gọi đoạn script PowerShell được tích hợp sẵn trong skill này để tự động làm phẳng cấu trúc thư mục.

Lệnh chạy:
```powershell
powershell -ExecutionPolicy Bypass -File "C:\code\skills\aptech_unzip_exam_folder\scripts\flatten.ps1" -TargetDir "ĐƯỜNG_DẪN_THƯ_MỤC_CỦA_USER"
```

### Bước 3: Xử lý lỗi (nếu có)
- Đôi khi script có thể báo lỗi do một số file đang được mở bởi ứng dụng khác (ví dụ `main.py` đang mở trong PyCharm). Trong trường hợp đó, script vẫn sẽ bỏ qua file bị khóa và xử lý các thư mục khác bình thường. Hãy thông báo cho người dùng biết về các file không thể di chuyển do đang bị khóa.

### Bước 4: Thông báo hoàn tất
Thông báo cho người dùng biết thao tác dọn dẹp thư mục lồng nhau đã hoàn thành.
