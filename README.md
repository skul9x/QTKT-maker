# 🏥 QTKT Generator & Merger (v1.1.0)

**QTKT Generator** là ứng dụng desktop chuyên dụng giúp tự động hóa quá trình soạn thảo và quản lý **Quy trình kỹ thuật (QTKT) lâm sàng** theo đúng tiêu chuẩn của Bộ Y tế Việt Nam (Quyết định 3023/QĐ-BYT).

Ứng dụng tích hợp AI (Google Gemini) để sinh nội dung chuyên môn và bộ engine gộp file chuyên nghiệp để phục vụ in ấn hàng loạt.

---

## 🌟 Tính năng nổi bật

*   🤖 **AI Chuyên gia y tế:** Sử dụng Gemini 1.5 Pro/Flash để soạn thảo nội dung y khoa sâu, ngôn ngữ chính xác.
*   📄 **Định dạng chuẩn Bộ Y tế:** Font Times New Roman, cỡ chữ 13, căn lề chuẩn (Trên 2.5cm, Dưới 2.0cm, Trái 3.0cm, Phải 2.5cm).
*   📚 **Tab Gộp File chuyên dụng:** Hỗ trợ gộp hàng chục file `.docx` riêng lẻ thành một tập chuyên đề duy nhất, tự động ngắt trang thông minh.
*   🚀 **Xử lý hàng loạt:** Nhập danh sách quy trình từ file `.txt` và tự động sinh hàng loạt file Word.
*   🔑 **Bảo mật:** Quản lý API Key dưới dạng mã hóa an toàn trên máy cục bộ.

---

## 🛠️ Cài đặt

### Yêu cầu hệ thống
- Python 3.10 trở lên.
- Kết nối Internet (để gọi API Gemini).

### Các bước cài đặt
1. **Tải mã nguồn về máy.**
2. **Cài đặt các thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Hướng dẫn sử dụng

### Tab 1: Tạo Quy Trình
1.  **Thiết lập API Key:** Nhập Gemini API Key từ [Google AI Studio](https://aistudio.google.com/).
2.  **Nhập liệu:** Nhập tên quy trình đơn lẻ hoặc bấm **"Nhập File TXT"** để xử lý số lượng lớn.
3.  **Thực hiện:** Bấm **"Tạo"**. Kết quả sẽ tự động lưu vào thư mục `QTKT ok`.

### Tab 2: Gộp File DOCX
1.  **Chọn file:** Bấm **"Chọn các file DOCX..."** để đưa các file cần gộp vào danh sách.
2.  **Quản lý danh sách:** Bạn có thể chọn file và nhấn phím **Delete** để xóa bớt các file chọn nhầm.
3.  **Gộp file:** Đặt tên file tổng và nhấn **"BẮT ĐẦU GỘP FILE"**.

---

## 📁 Cấu trúc thư mục

```text
QTKT_code/
├── main.py              # File chạy chính của ứng dụng
├── config.py            # Cấu hình hệ thống (Font, Lề, App Info)
├── services/            # Chứa các dịch vụ nghiệp vụ
│   ├── gemini_service.py # Kết nối Google Gemini API
│   ├── docx_generator.py # Xử lý xuất file Microsoft Word
│   ├── docx_merger.py    # Engine gộp file ngắt trang
│   └── key_manager.py    # Quản lý API Key mã hóa
├── ui/                  # Giao diện người dùng (PySide6)
│   └── main_window.py   # Giao diện 2 Tab và logic điều phối
└── QTKT ok/             # Thư mục mặc định chứa file đầu ra
```

---

## 📄 Giấy phép & Bản quyền
Dự án phát triển nhằm hỗ trợ cộng đồng y tế Việt Nam. Vui lòng rà soát nội dung chuyên môn trước khi ban hành chính thức.

*Chúc bạn làm việc hiệu quả với QTKT Generator!*
