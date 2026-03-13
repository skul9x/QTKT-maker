# 🏥 QTKT Generator & Merger (v1.1.0)

**QTKT Generator & Merger** là giải pháp phần mềm chuyên dụng được thiết kế nhằm tối ưu hóa quy trình soạn thảo, quản lý và lưu trữ **Quy trình kỹ thuật (QTKT) lâm sàng**. Tuân thủ nghiêm ngặt theo **Phụ lục 01 - Quyết định 3023/QĐ-BYT** của Bộ Y tế Việt Nam.

Dự án kết hợp sức mạnh của AI hiện đại (Google Gemini) để hỗ trợ chuyên môn và bộ lọc xử lý văn bản Microsoft Word chuẩn xác.

---

## 🌟 Tính năng chính

*   🤖 **Soạn thảo AI thông minh:** Tự động tạo nội dung 6 mục quy trình chuẩn y khoa (Đại cương, Chỉ định, Chống chỉ định, Chuẩn bị, Tiến hành, Theo dõi).
*   📚 **Gộp file chuyên nghiệp:** Tab "Gộp File" cho phép hợp nhất nhiều quy trình lẻ thành sổ tay chuyên đề, tự động thêm ngắt trang (Page Break).
*   🎨 **Định dạng tự động:** Tự động thiết lập Font Times New Roman 13, căn lề văn bản hành chính chuẩn (3-2-2.5-2.5cm).
*   📥 **Xử lý Batch:** Hỗ trợ nhập hàng loạt từ danh sách file `.txt` giúp tiết kiệm thời gian tối đa.
*   🔒 **Bảo mật dữ liệu:** API Key được mã hóa AES và lưu trữ cục bộ, không gửi đi bất kỳ đâu ngoài máy chủ Google AI.

---

## 🛠️ Cài đặt & Khởi động

### Yêu cầu hệ thống
- **Python:** Phiên bản 3.10 hoặc mới hơn.
- **Thư viện:** `PySide6`, `python-docx`, `google-generativeai`.

### Các bước thực hiện
1. **Clone project:**
   ```bash
   git clone https://github.com/skul9x/QTKT-maker.git
   cd QTKT-maker
   ```
2. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Chạy ứng dụng:**
   ```bash
   python main.py
   ```

---

## 🚀 Quy trình sử dụng

### 1. Tạo mới quy trình (Tab 1)
- Lấy API Key từ [Google AI Studio](https://aistudio.google.com/).
- Nhập tên kỹ thuật cần soạn (VD: *Thay băng bỏng*).
- Nhấn **"Tạo"**. File DOCX sẽ xuất hiện trong thư mục `QTKT ok`.

### 2. Gộp nhiều quy trình (Tab 2)
- Chọn danh sách các file `.docx` đã có.
- Sắp xếp thứ tự (sắp tới sẽ hỗ trợ kéo thả).
- Đặt tên file tổng hợp và nhấn **"BẮT ĐẦU GỘP FILE"**.

---

## 📁 Cấu trúc thư mục dự án

```text
QTKT_code/
├── main.py              # Điểm khởi đầu ứng dụng
├── config.py            # Cấu hình UI và Style văn bản
├── services/            # Lớp xử lý nghiệp vụ (Business Logic)
│   ├── gemini_service.py # Xử lý AI Gemini
│   ├── docx_generator.py # Xử lý xuất văn bản Word
│   ├── docx_merger.py    # Thuật toán gộp file ngắt trang
│   └── key_manager.py    # Quản lý khóa API bảo mật
├── ui/                  # Lớp giao diện người dùng
│   └── main_window.py   # Quản lý Tabs và tương tác người dùng
└── QTKT ok/             # Nơi lưu trữ thành phẩm
```

---

## 📄 Quyền hạn & Trách nhiệm
Phần mềm là công cụ hỗ trợ soạn thảo. Người dùng (Hội đồng chuyên môn) chịu trách nhiệm cuối cùng về nội dung y khoa trước khi ký ban hành.

---
*Phát triển bởi đội ngũ đam mê công nghệ y tế Việt Nam.*
