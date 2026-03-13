import google.genai as genai
from config import GEMINI_API_KEY
import logging
import re
import time

# Configure logger
logger = logging.getLogger(__name__)

class GeminiService:
    """Service để gọi Gemini API và tạo nội dung QTKT"""
    
    # Chỉ sử dụng model này, KHÔNG fallback sang model khác
    MODEL_NAME = "gemini-3-flash-preview"

    def __init__(self, api_key_input: str = None):
        """
        Khởi tạo service.
        Args:
            api_key_input: Chuỗi chứa một hoặc nhiều API key (có thể lẫn text khác).
                           Nếu None, sẽ lấy từ config.
        """
        raw_input = api_key_input or GEMINI_API_KEY
        self.api_keys = self._extract_api_keys(raw_input)
        
        # Lưu các key đã hết quota (429) trong session này - Bỏ qua vĩnh viễn
        self.exhausted_keys = set()
        
        # Lưu các key đang cooldown (503) - {key: thời_điểm_hết_cooldown}
        self.cooldown_keys = {}
        self.COOLDOWN_SECONDS = 180  # 3 phút
        
        if not self.api_keys:
            logger.warning("Không tìm thấy API key nào hợp lệ!")
        else:
            logger.info(f"Đã tìm thấy {len(self.api_keys)} API key(s).")

    def _extract_api_keys(self, input_string: str) -> list:
        """Dùng regex để trích xuất tất cả API keys bắt đầu bằng 'AIza' từ chuỗi input."""
        if not input_string:
            return []
        
        pattern = r"AIza[0-9A-Za-z\-_]{35}"
        keys = re.findall(pattern, input_string)
        return list(set(keys))

    def set_api_key(self, api_key_input: str):
        """Cập nhật danh sách API key từ input mới"""
        self.api_keys = self._extract_api_keys(api_key_input)
        if self.api_keys:
            logger.info(f"Đã cập nhật: {len(self.api_keys)} API key(s).")
        else:
            logger.warning("Cập nhật thất bại: Không tìm thấy API key hợp lệ trong input.")
    
    def generate_qtkt(self, ten_quy_trinh: str) -> dict:
        """
        Tạo nội dung QTKT sử dụng model gemini-3-flash-preview.
        Chỉ thử qua các API keys, KHÔNG fallback sang model khác.
        """
        if not self.api_keys:
            raise ValueError("Chưa có API key nào được cấu hình! Vui lòng nhập API key.")
        
        prompt = f"""Bạn là chuyên gia y khoa hàng đầu. Hãy viết "Quy trình kỹ thuật lâm sàng" cho kỹ thuật: "{ten_quy_trinh}"

Vui lòng viết CHÍNH XÁC theo mẫu "Phụ lục 01: Hướng dẫn Quy trình kỹ thuật lâm sàng" (Ban hành kèm theo Quyết định số 3023/QĐ-BYT ngày 28 tháng 7 năm 2023 của Bộ trưởng Bộ Y tế).

Yêu cầu nội dung:
- Viết bằng tiếng Việt chuyên ngành y khoa, văn phong chuyên nghiệp, súc tích.
- Nội dung phải chính xác, an toàn, cập nhật theo y văn mới nhất.
- Đầy đủ các mục lớn nhỏ theo đúng cấu trúc dưới đây.
- Các mục con (ví dụ 5.1, 5.2...) phải viết chi tiết, TUYỆT ĐỐI KHÔNG ĐƯỢC BỎ SÓT.

QUAN TRỌNG:
- KHÔNG được có lời chào (Chào bạn...), lời dẫn nhập, hay lời kết.
- KHÔNG được ký tên (Người viết, Chuyên gia...).
- TUYỆT ĐỐI KHÔNG lặp lại dòng chứa tên kỹ thuật ở đầu phần trả về (vì tôi đã có tiêu đề file riêng).
- Bắt đầu ngay bằng dòng "1. ĐẠI CƯƠNG" và kết thúc ở mục lục tham khảo.

CẤU TRÚC TRẢ VỀ:

1. ĐẠI CƯƠNG
(Định nghĩa, nguyên lý, mục đích của kỹ thuật)

2. CHỈ ĐỊNH
(Liệt kê các trường hợp bệnh lý hoặc tình huống lâm sàng được chỉ định thực hiện kỹ thuật)

3. CHỐNG CHỈ ĐỊNH
(Liệt kê các trường hợp tuyệt đối hoặc tương đối không được thực hiện)

4. THẬN TRỌNG
(Các trường hợp cần đặc biệt lưu ý hoặc thận trọng khi thực hiện)

5. CHUẨN BỊ
5.1. Người thực hiện
a) Nhân lực trực tiếp (Ví dụ: Bác sĩ chuyên khoa, Kỹ thuật viên, Điều dưỡng...)
b) Nhân lực hỗ trợ (Nếu có)

5.2. Thuốc
(Liệt kê cụ thể: Tên hoạt chất, nồng độ, hàm lượng, đường dùng, dạng dùng, sơ bộ số lượng nếu ước tính được)

5.3. Vật tư
(Vật tư tiêu hao dùng trực tiếp cho kỹ thuật: Bơm kim tiêm, găng tay, bông băng, gạc... - không bao gồm văn phòng phẩm)

5.4. Trang thiết bị
(Máy móc, dụng cụ y tế, phương tiện phục vụ kỹ thuật và hồi sức cấp cứu)

5.5. Người bệnh
- Giải thích cho người bệnh/người nhà về mục đích, tai biến có thể xảy ra.
- Chuẩn bị người bệnh: Tư thế, nhịn ăn (nếu cần), vệ sinh vùng can thiệp...

5.6. Hồ sơ bệnh án
(Các giấy tờ, cam kết, phiếu chỉ định cần thiết)

5.7. Thời gian thực hiện kỹ thuật (Ước tính khoảng bao nhiêu phút/giờ)

5.8. Địa điểm thực hiện kỹ thuật (Phòng thủ thuật, phòng mổ, hay tại giường...)

5.9. Kiểm tra hồ sơ
a) Kiểm tra người bệnh (Đúng người, đúng bệnh, đúng vị trí...)
b) Thực hiện bảng kiểm an toàn phẫu thuật/thủ thuật
c) Đặt tư thế người bệnh

6. TIẾN HÀNH QUY TRÌNH KỸ THUẬT
(Mô tả chi tiết từng bước thực hiện theo trình tự thời gian. Chia rõ ràng: 6.1. Bước 1; 6.2. Bước 2; ...)
LƯU Ý QUAN TRỌNG: Bước CUỐI CÙNG của mục 6 PHẢI là "6.X. Kết thúc quy trình" (X là số thứ tự bước cuối), với nội dung bắt buộc:
- Đánh giá tình trạng người bệnh sau thực hiện kỹ thuật.
- Hoàn thiện ghi chép hồ sơ bệnh án, lưu hồ sơ.
- Bàn giao người bệnh cho bộ phận tiếp theo (nếu có).

7. THEO DÕI VÀ XỬ TRÍ TAI BIẾN
7.1. Tai biến trong khi thực hiện kỹ thuật (Nhận biết và xử trí)
7.2. Tai biến sau khi thực hiện kỹ thuật (Nhận biết và xử trí)
7.3. Biến chứng muộn

8. TÀI LIỆU THAM KHẢO
(Liệt kê ít nhất 3 tài liệu tham khảo uy tín: Sách giáo khoa, Hướng dẫn của Bộ Y tế, Guidelines quốc tế...)"""

        errors_log = []
        print(f"🚀 Bắt đầu tạo QTKT: {ten_quy_trinh}")
        print(f"ℹ️ Model: {self.MODEL_NAME} | API Keys: {len(self.api_keys)}")

        # Chỉ loop qua API keys, KHÔNG fallback sang model khác
        for index, key in enumerate(self.api_keys):
            masked_key = f"...{key[-4:]}"
            
            # Skip key đã hết quota (429)
            if key in self.exhausted_keys:
                print(f"  ⏭️ Bỏ qua Key {index+1}/{len(self.api_keys)} ({masked_key}) - Đã hết quota")
                continue
            
            # Skip key đang cooldown (503)
            if key in self.cooldown_keys:
                remaining = self.cooldown_keys[key] - time.time()
                if remaining > 0:
                    print(f"  ⏳ Bỏ qua Key {index+1}/{len(self.api_keys)} ({masked_key}) - Cooldown còn {int(remaining)}s")
                    continue
                else:
                    # Hết cooldown, xóa khỏi dict
                    del self.cooldown_keys[key]
            
            try:
                client = genai.Client(api_key=key)
                
                print(f"  🔑 Thử Key {index+1}/{len(self.api_keys)} ({masked_key})...")
                
                response = client.models.generate_content(
                    model=self.MODEL_NAME,
                    contents=prompt
                )
                
                print(f"✅ THÀNH CÔNG! (Model: {self.MODEL_NAME} | Key: {masked_key})")
                return {
                    "ten_quy_trinh": ten_quy_trinh,
                    "noi_dung": response.text,
                    "meta": {
                        "model_used": self.MODEL_NAME,
                        "key_used": masked_key
                    }
                }

            except Exception as e:
                error_str = str(e)
                
                # Đánh dấu key hết quota (429) - Bỏ qua vĩnh viễn trong session
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    self.exhausted_keys.add(key)
                    print(f"  ⛔ Key {masked_key}: HẾT QUOTA - Bỏ qua vĩnh viễn!")
                # Đánh dấu key lỗi 503 - Cooldown 3 phút
                elif "503" in error_str or "UNAVAILABLE" in error_str:
                    self.cooldown_keys[key] = time.time() + self.COOLDOWN_SECONDS
                    print(f"  ⏸️ Key {masked_key}: SERVER BẬN - Cooldown 3 phút!")
                else:
                    print(f"  ⚠️ Key {masked_key}: {error_str[:100]}...")
                
                errors_log.append(f"Key {masked_key}: {error_str}")
                continue
        
        # Nếu tất cả keys đều fail
        raise RuntimeError(
            f"❌ ĐÃ HẾT QUOTA!\n\n"
            f"Model: {self.MODEL_NAME}\n"
            f"Đã thử {len(self.api_keys)} API key(s) nhưng đều thất bại.\n\n"
            f"Vui lòng:\n"
            f"1. Thử lại sau 1 phút\n"
            f"2. Hoặc thêm API key mới\n\n"
            f"Chi tiết lỗi:\n" + "\n".join(errors_log)
        )
