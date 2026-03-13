# 🏥 QTKT Generator (v1.0.0)

**QTKT Generator** là ứng dụng desktop mạnh mẽ giúp tự động hóa quá trình soạn thảo **Quy trình kỹ thuật (QTKT) lâm sàng** theo đúng tiêu chuẩn của Bộ Y tế Việt Nam (Quyết định 3023/QĐ-BYT).

Ứng dụng kết hợp sức mạnh của Trí tuệ nhân tạo (Google Gemini AI) để sinh nội dung chuyên môn và thư viện xử lý văn bản chuyên nghiệp để đảm bảo thể thức trình bày chuẩn xác 100%.

---

## 🌟 Tính năng nổi bật

*   🤖 **AI Chuyên gia y tế:** Sử dụng model Gemini 1.5 Pro/Flash để soạn thảo nội dung chuyên môn y khoa sâu, ngôn ngữ chính xác.
*   📄 **Định dạng chuẩn Bộ Y tế:** Tự động thiết lập font Times New Roman, cỡ chữ 13, căn lề chuẩn (Trên 2.5cm, Dưới 2.0cm, Trái 3.0cm, Phải 2.5cm) trong file `.docx`.
*   🚀 **Xử lý hàng loạt:** Cho phép nhập danh sách nhiều quy trình cùng lúc và tự động xuất ra từng file riêng biệt.
*   🔑 **Bảo mật API Key:** Quản lý và lưu trữ API Key dưới dạng mã hóa an toàn trên máy cục bộ.
*   💻 **Giao diện hiện đại:** Xây dựng trên nền tảng PySide6 (Qt) mang lại trải nghiệm mượt mà, chuyên nghiệp.

---

## 🛠️ Cài đặt

### Yêu cầu hệ thống
- Python 3.10 trở lên.
- Kết nối Internet (để gọi API Gemini).

### Các bước cài đặt
1. **Tải mã nguồn về máy.**
2. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Hướng dẫn sử dụng

### Bước 1: Lấy Gemini API Key
- Truy cập [Google AI Studio](https://aistudio.google.com/).
- Đăng nhập bằng tài khoản Google và chọn **"Create API key"**.
- Lưu lại key này để nhập vào ứng dụng.

### Bước 2: Khởi động ứng dụng
- Chạy lệnh sau trong terminal hoặc terminal của VS Code:
  ```bash
  python main.py
  ```

### Bước 3: Soạn thảo Quy trình
1.  **Nhập API Key:** Nhập key bạn đã lấy ở Bước 1 vào ô "Gemini API Key".
2.  **Nhập danh sách quy trình:** Nhập tên các quy trình cần tạo (mỗi dòng một quy trình).
    *   *Ví dụ: Đặt nội khí quản, Tiêm bắp, Thay băng vết thương.*
3.  **Tạo nội dung:** Nhấn nút **"Bắt đầu tạo"**. Ứng dụng sẽ gọi AI để soạn thảo từng mục theo cấu trúc:
    - *Đại cương -> Chỉ định -> Chống chỉ định -> Chuẩn bị -> Các bước tiến hành -> Theo dõi & Xử trí tai biến.*
4.  **Xuất file DOCX:** Sau khi AI hoàn tất, nhấn **"Xuất File Word"**. Các file sẽ được lưu vào thư mục `QTKT ok` ngay tại thư mục gốc của dự án.

---

## 📁 Cấu trúc thư mục

```text
QTKT_code/
├── main.py              # File chạy chính của ứng dụng
├── config.py            # Cấu hình hệ thống (Font, Lề, App Info)
├── requirements.txt     # Danh sách thư viện phụ thuộc
├── ui/                  # Chứa code giao diện (PySide6)
│   └── main_window.py   # Giao diện chính và logic điều phối
├── services/            # Chứa các dịch vụ nghiệp vụ
│   ├── gemini_service.py # Kết nối Google Gemini API
│   ├── docx_generator.py # Xử lý xuất file Microsoft Word
│   └── key_manager.py    # Mã hóa và quản lý API Key
└── .brain/              # (Tự động tạo) Lưu key đã mã hóa
```

---

## ⚠️ Lưu ý quan trọng
- **Tốc độ:** Thời gian tạo phụ thuộc vào độ phức tạp của quy trình và tốc độ phản hồi của API.
- **Kiểm tra lại:** Mặc dù AI rất mạnh mẽ, người dùng (nhân viên y tế) **bắt buộc** phải rà soát lại nội dung chuyên môn trước khi ban hành chính thức.
- **File đang mở:** Đảm bảo không mở file Word trùng tên trong thư mục đầu ra khi ứng dụng đang thực hiện quá trình xuất file.

---

## 📄 Giấy phép & Bản quyền
Dự án được phát triển nhằm hỗ trợ cộng đồng y tế Việt Nam. Vui lòng tuân thủ các quy định về an toàn dữ liệu và bảo mật thông tin khi sử dụng.

---
*Chúc bạn có những trải nghiệm tuyệt vời với QTKT Generator!*
