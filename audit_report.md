# 🏥 Báo cáo Phân tích Lỗi Code: main_window.py

Dựa trên yêu cầu rà soát các lỗi tiềm ẩn (Race Condition, Memory Leak, v.v.), dưới đây là kết quả phân tích:

## 📊 Tóm tắt

| Mức độ | Loại lỗi | Chi tiết & Vị trí |
| :--- | :--- | :--- |
| **Trung bình** | **Blocking / Graceful Stop Issue** | **Logic dừng (Stop Logic):** Trong `BatchGenerateThread.run`, việc kiểm tra `self.stop_requested` chỉ diễn ra *trước* và *sau* khi gọi API. Nếu API call bị treo hoặc mất quá nhiều thời gian (ngoài tầm kiểm soát của `gemini_service`), thread sẽ không thể dừng ngay lập tức khi user bấm nút. App sẽ "đơ" ở trạng thái "Đang dừng..." cho đến khi request hiện tại timeout hoặc kêt thúc. |
| **Thấp** | **Potential Resource Leak** | **File Handling (`_auto_export_docx`):** Không có cơ chế kiểm tra `PermissionError` kỹ càng. Nếu file DOCX đích đang được mở bởi Microsoft Word, quá trình ghi sẽ thất bại và chỉ in lỗi ra console mà không cảnh báo người dùng trên UI. |
| **Thấp** | **Hardcoded Strings** | **Maintenance Issue:** Các chuỗi như màu sắc `"#4CAF50"`, `"#f44336"`, tên thư mục `"QTKT ok"` được code cứng rải rác. Khó khăn khi muốn đổi theme hoặc cấu hình đường dẫn sau này. |
| **Thấp** | **UI Blocking (Monitor)** | **Encryption on Main Thread:** Hàm `save_api_key` thực hiện mã hóa và I/O trên Main Thread. Với lượng dữ liệu nhỏ hiện tại thì không sao, nhưng về nguyên tắc là nên tránh Blocking Main Thread. |

---

## ✅ Các lỗi KHÔNG tìm thấy (An toàn)

Code hiện tại **AN TOÀN** với các lỗi nghiêm trọng sau:

- **Race Condition / Deadlock:** Logic đa luồng đơn giản, không có shared resources phức tạp gây tranh chấp. Biến flag `stop_requested` được sử dụng an toàn.
- **Memory Leak:** Các object Qt (Widget, Thread) được quản lý đúng vòng đời (parent-child ownership của Qt), Python GC sẽ dọn dẹp biến local.
- **Null Pointer Exception:** Code sử dụng `get()` an toàn cho dictionary và có try/catch bao bọc các vùng nguy hiểm.
- **SQL Injection / XSS:** Không sử dụng database SQL hay render HTML từ user input.
- **Infinite Loop:** Vòng lặp `for` hữu hạn theo danh sách input, không có `while True` nguy hiểm.

## 💡 Khuyến nghị
Code ở trạng thái **ỔN ĐỊNH** cho nhu cầu sử dụng hiện tại. Chỉ cần lưu ý vấn đề file DOCX đang mở khi chạy batch để tránh mất dữ liệu output.
