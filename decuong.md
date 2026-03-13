# Plan: Xây dựng Ứng dụng Tạo Quy Trình Kỹ Thuật (QTKT) Y Tế Tự Động

Mục tiêu: Xây dựng công cụ tự động hóa việc soạn thảo văn bản quy trình kỹ thuật y tế, đảm bảo tuân thủ chính xác thể thức trình bày của Bộ Y tế (Quyết định 3023/QĐ-BYT).

## 1. Yêu cầu & Phân tích

### 1.1 Input
- Tên quy trình kỹ thuật (VD: "Đặt nội khí quản", "Tiêm bắp", "Thay băng vết thương").
- API Key của Google Gemini.

### 1.2 Output
- File văn bản định dạng `.docx` (Microsoft Word).
- Nội dung chuyên môn y tế được sinh bởi AI.
- Thể thức văn bản chuẩn theo quy định hành chính.

## 2. Kiến trúc Hệ thống

### 2.1 Công nghệ (Tech Stack)
- **Ngôn ngữ:** Python 3.10+
- **Giao diện (UI):** PySide6 (Qt for Python) - Hiện đại, native look & feel.
- **AI Engine:** Google Gemini API (Model `gemini-2.5-pro` - Model tốt nhất cho tiếng Việt và chuyên môn sâu).
- **Xử lý văn bản:** Thư viện `python-docx`.

### 2.2 Luồng xử lý (Workflow)
1.  **Người dùng nhập liệu:** Nhập tên QTKT và API Key trên giao diện.
2.  **AI Processing:**
    - Gửi request đến Gemini API với prompt chuyên biệt (System Prompt).
    - Prompt yêu cầu role "Chuyên gia y tế" và cấu trúc response tuân thủ Phụ lục 01.
3.  **Data Parsing:** Nhận kết quả text từ AI.
4.  **Document Generation:**
    - Khởi tạo file Word trắng.
    - Thiết lập Page Layout (A4, lề chuẩn).
    - Format văn bản (Font Times New Roman, Size 13, Line spacing 1.0).
    - Điền nội dung vào file.
5.  **Export:** Lưu file `.docx` và thông báo hoàn tất.

## 3. Chi tiết Triển khai

### 3.1 Cấu trúc Prompt (Quan trọng)
Prompt gửi cho Gemini phải bao gồm các chỉ dẫn (instructions) sau:
- **Role:** Chuyên gia y khoa, ngôn ngữ Tiếng Việt chuyên ngành.
- **Format:** Tuân thủ chặt chẽ "Phụ lục 01: Hướng dẫn Quy trình kỹ thuật lâm sàng" (QĐ 3023/QĐ-BYT).
- **Các mục bắt buộc:**
    1. ĐẠI CƯƠNG
    2. CHỈ ĐỊNH
    3. CHỐNG CHỈ ĐỊNH
    4. THẬN TRỌNG
    5. CHUẨN BỊ (Nhân lực, Thuốc, Vật tư, Trang thiết bị, Người bệnh, Hồ sơ...)
    6. TIẾN HÀNH QUY TRÌNH KỸ THUẬT (Mô tả từng bước)
    7. THEO DÕI VÀ XỬ TRÍ TAI BIẾN
    8. TÀI LIỆU THAM KHẢO

### 3.2 Quy định định dạng văn bản (Style Guide)
Code xử lý `python-docx` phải đảm bảo các thông số:
- **Font:** Times New Roman.
- **Size:** 13pt (cho nội dung), 14pt Đậm (cho tiêu đề).
- **Line Spacing:** 1.0 (Single).
- **Margins (Lề):**
    - Trên (Top): 2.5 cm
    - Dưới (Bottom): 2.0 cm
    - Trái (Left): 3.0 cm
    - Phải (Right): 2.5 cm
- **Paragraph Spacing:** Before 6pt, After 0pt.

## 4. Các bước thực hiện (Task List)

- [x] **Bước 1: Setup Project**
    - Cấu trúc thư mục: `ui/`, `services/`.
    - `requirements.txt`: `PySide6`, `google-generativeai`, `python-docx`.

- [x] **Bước 2: Backend - Gemini Service**
    - Class `GeminiService`.
    - Config model `gemini-2.5-pro`.
    - Hàm `generate_qtkt(ten_quy_trinh)`.

- [x] **Bước 3: Backend - Docx Generator**
    - Class `DocxGenerator`.
    - Hàm `create_document(content, path)`.
    - Implement chính xác logic căn lề và font chữ.

- [x] **Bước 4: Frontend - PySide6 UI**
    - `MainWindow` với Input field, Nút "Tạo", "Xuất file".
    - Progress Bar và Preview Text Box.
    - Threading để không bị đơ UI khi gọi API.

- [x] **Bước 5: Testing & Packaging**
    - Chạy thử với quy trình mẫu.
    - Kiểm tra file Output bằng Word.

## 5. Hướng dẫn sử dụng
1.  Cài đặt: `pip install -r requirements.txt`
2.  Chạy: `python main.py`
3.  Nhập API Key Gemini (Lấy tại aistudio.google.com).
4.  Nhập tên Quy trình -> Nhấn "Tạo" -> Nhấn "Xuất DOCX".
