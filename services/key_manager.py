"""
Key Manager - Secure API Key Storage
Mã hóa và lưu trữ API keys an toàn bằng Fernet (AES-128-CBC)
"""
import os
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class KeyManager:
    """Quản lý lưu trữ API keys được mã hóa"""
    
    def __init__(self, storage_dir: str = None):
        """
        Khởi tạo KeyManager
        
        Args:
            storage_dir: Thư mục lưu file mã hóa. Mặc định là .brain/ trong project
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            # Lưu trong thư mục .brain của project
            self.storage_dir = Path(__file__).parent.parent / ".brain"
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.keys_file = self.storage_dir / "api_keys.enc"
        self.salt_file = self.storage_dir / ".salt"
        
    def _get_machine_id(self) -> str:
        """Lấy machine-specific identifier"""
        # Kết hợp nhiều yếu tố để tạo ID duy nhất cho máy
        import platform
        machine_info = f"{platform.node()}-{platform.machine()}-{os.getlogin()}"
        return machine_info
    
    def _get_or_create_salt(self) -> bytes:
        """Lấy hoặc tạo salt cho encryption"""
        if self.salt_file.exists():
            return self.salt_file.read_bytes()
        else:
            # Tạo salt ngẫu nhiên 16 bytes
            salt = os.urandom(16)
            self.salt_file.write_bytes(salt)
            return salt
    
    def _get_encryption_key(self) -> bytes:
        """Tạo Fernet key từ machine ID + salt"""
        machine_id = self._get_machine_id()
        salt = self._get_or_create_salt()
        
        # Dùng PBKDF2 để derive key từ machine ID
        key_material = hashlib.pbkdf2_hmac(
            'sha256',
            machine_id.encode('utf-8'),
            salt,
            100000  # iterations
        )
        
        # Fernet cần key 32 bytes, base64 encoded
        fernet_key = base64.urlsafe_b64encode(key_material[:32])
        return fernet_key
    
    def save_keys(self, keys: list) -> bool:
        """
        Mã hóa và lưu danh sách API keys
        
        Args:
            keys: List các API key strings
            
        Returns:
            True nếu lưu thành công
        """
        try:
            if not keys:
                logger.warning("Không có keys để lưu")
                return False
            
            fernet = Fernet(self._get_encryption_key())
            
            # Join keys với newline, sau đó mã hóa
            plaintext = "\n".join(keys)
            encrypted = fernet.encrypt(plaintext.encode('utf-8'))
            
            # Lưu vào file
            self.keys_file.write_bytes(encrypted)
            logger.info(f"Đã lưu {len(keys)} API key(s) vào {self.keys_file}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi lưu keys: {e}")
            return False
    
    def load_keys(self) -> list:
        """
        Giải mã và load danh sách API keys
        
        Returns:
            List các API key strings, hoặc empty list nếu không có/lỗi
        """
        try:
            if not self.keys_file.exists():
                logger.info("Chưa có file keys lưu trước đó")
                return []
            
            fernet = Fernet(self._get_encryption_key())
            
            encrypted = self.keys_file.read_bytes()
            decrypted = fernet.decrypt(encrypted)
            
            keys = decrypted.decode('utf-8').split("\n")
            keys = [k.strip() for k in keys if k.strip()]
            
            logger.info(f"Đã load {len(keys)} API key(s) từ file")
            return keys
            
        except Exception as e:
            logger.error(f"Lỗi khi load keys: {e}")
            return []
    
    def clear_keys(self) -> bool:
        """Xóa file keys đã lưu"""
        try:
            if self.keys_file.exists():
                self.keys_file.unlink()
                logger.info("Đã xóa file keys")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa keys: {e}")
            return False
