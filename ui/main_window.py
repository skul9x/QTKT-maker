"""
Main Window for QTKT Generator App
"""
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QProgressBar, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QListWidget, QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor

from services.gemini_service import GeminiService
from services.docx_generator import DocxGenerator
from services.key_manager import KeyManager
from services.docx_merger import merge_docx_files
from config import APP_NAME, APP_VERSION


class GenerateThread(QThread):
    """Thread để generate content không block UI"""
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, service: GeminiService, ten_quy_trinh: str):
        super().__init__()
        self.service = service
        self.ten_quy_trinh = ten_quy_trinh
    
    def run(self):
        try:
            result = self.service.generate_qtkt(self.ten_quy_trinh)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class BatchGenerateThread(QThread):
    """Thread để generate nhiều QTKT tuần tự"""
    item_finished = Signal(str, bool, str, dict)  # ten_quy_trinh, success, model_used, content
    all_finished = Signal()
    stopped = Signal()  # Signal báo đã dừng
    progress_update = Signal(int, int)  # current, total
    
    def __init__(self, service: GeminiService, qtkt_list: list):
        super().__init__()
        self.service = service
        self.qtkt_list = qtkt_list
        self.stop_requested = False      # Flag yêu cầu dừng
        self.waiting_for_response = False # Đang chờ Gemini phản hồi
    
    def request_stop(self):
        """Yêu cầu dừng sau khi hoàn thành item hiện tại"""
        self.stop_requested = True
        return self.waiting_for_response  # True nếu đang chờ Gemini
    
    def run(self):
        total = len(self.qtkt_list)
        for i, ten_quy_trinh in enumerate(self.qtkt_list):
            # Kiểm tra stop TRƯỚC khi gọi API
            if self.stop_requested:
                break
            
            self.progress_update.emit(i + 1, total)
            self.waiting_for_response = True  # Đánh dấu đang chờ Gemini
            
            try:
                result = self.service.generate_qtkt(ten_quy_trinh)
                model_used = result.get("meta", {}).get("model_used", "N/A")
                self.item_finished.emit(ten_quy_trinh, True, model_used, result)
            except Exception as e:
                self.item_finished.emit(ten_quy_trinh, False, str(e), {})
            finally:
                self.waiting_for_response = False
                
                # Kiểm tra stop SAU KHI hoàn thành item (dù thành công hay thất bại)
                if self.stop_requested:
                    break
        
        # Emit signal phù hợp
        if self.stop_requested:
            self.stopped.emit()
        else:
            self.all_finished.emit()


class SelectionListWidget(QListWidget):
    """QListWidget tùy chỉnh hỗ trợ phím Delete để xóa item"""
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                self.takeItem(self.row(item))
        else:
            super().keyPressEvent(event)


class MergeWorker(QThread):
    """Thread xử lý gộp file DOCX"""
    progress = Signal(int, int, str)
    finished_signal = Signal(bool, str)

    def __init__(self, file_paths, output_path):
        super().__init__()
        self.file_paths = file_paths
        self.output_path = output_path

    def run(self):
        try:
            merge_docx_files(self.file_paths, self.output_path, self.progress.emit)
            self.finished_signal.emit(True, f"Đã gộp thành công vào file:\n{self.output_path}")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class MainWindow(QMainWindow):
    """Main Window của QTKT Generator"""
    
    def __init__(self):
        super().__init__()
        self.gemini_service = GeminiService()
        self.docx_generator = DocxGenerator()
        self.key_manager = KeyManager()
        self.current_content = None
        self.generate_thread = None
        self.batch_thread = None
        
        self.setup_ui()
        self._load_saved_keys()
    
    def setup_ui(self):
        """Thiết lập giao diện chính với Tabs"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1000, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Tab Widget
        self.tabs = QTabWidget()
        
        # Tab 1: Tạo Quy Trình
        self.generator_tab = QWidget()
        self.setup_generator_tab()
        self.tabs.addTab(self.generator_tab, "📝 Tạo Quy Trình")
        
        # Tab 2: Gộp File
        self.merger_tab = QWidget()
        self.setup_merger_tab()
        self.tabs.addTab(self.merger_tab, "📚 Gộp File DOCX")
        
        main_layout.addWidget(self.tabs)
        
        # Global Status bar
        self.statusBar().showMessage("Sẵn sàng")

    def setup_generator_tab(self):
        """Thiết lập giao diện Tab Tạo Quy Trình (Logic cũ)"""
        layout = QVBoxLayout(self.generator_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("📋 Tạo Quy Trình Kỹ Thuật Lâm Sàng")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QLabel("Theo mẫu Phụ lục 01 - Quyết định 3023/QĐ-BYT")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #666;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # API Key section
        api_group = QGroupBox("🔑 Gemini API Keys (mỗi key một dòng)")
        api_layout = QVBoxLayout(api_group)
        
        self.api_key_input = QTextEdit()
        self.api_key_input.setPlaceholderText("Nhập một hoặc nhiều Gemini API key (mỗi key một dòng).\nVí dụ:\nAIzaSyD...\nAIzaSyB...\nAIzaSyC...")
        self.api_key_input.setMinimumHeight(80)
        self.api_key_input.setMaximumHeight(100)
        self.api_key_input.setFont(QFont("Consolas", 9))
        api_layout.addWidget(self.api_key_input)
        
        self.save_key_btn = QPushButton("💾 Lưu API Keys")
        self.save_key_btn.clicked.connect(self.save_api_key)
        api_layout.addWidget(self.save_key_btn)
        
        layout.addWidget(api_group)
        
        # Input section
        input_group = QGroupBox("📝 Nhập thông tin")
        input_layout = QVBoxLayout(input_group)
        
        input_label = QLabel("Tên quy trình kỹ thuật (đơn lẻ):")
        input_layout.addWidget(input_label)
        
        single_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("VD: Đặt nội khí quản, Thay băng vết thương...")
        self.input_field.setFont(QFont("Segoe UI", 11))
        self.input_field.returnPressed.connect(self.generate_content)
        single_row.addWidget(self.input_field)
        
        self.generate_btn = QPushButton("🔄 Tạo")
        self.generate_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.generate_btn.setMinimumWidth(80)
        self.generate_btn.clicked.connect(self.generate_content)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        single_row.addWidget(self.generate_btn)
        input_layout.addLayout(single_row)
        
        layout.addWidget(input_group)
        
        # Batch Buttons
        batch_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("📂 Nhập File TXT (Xử lý hàng loạt)")
        self.import_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.import_btn.setMinimumHeight(40)
        self.import_btn.clicked.connect(self.import_txt_file)
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #F57C00; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        batch_layout.addWidget(self.import_btn)
        
        # Stop button (ẩn mặc định)
        self.stop_btn = QPushButton("⏹️ Dừng")
        self.stop_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #d32f2f; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.stop_btn.hide()  # Ẩn mặc định
        batch_layout.addWidget(self.stop_btn)
        
        layout.addLayout(batch_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Results Table
        results_group = QGroupBox("📊 Kết quả xử lý")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Tên Quy Trình", "Kết Quả", "Model"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setFont(QFont("Segoe UI", 10))
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        results_layout.addWidget(self.results_table)
        
        layout.addWidget(results_group, 1)  # Stretch factor = 1
        
        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QLineEdit:focus { border-color: #4CAF50; }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
    
    def save_api_key(self):
        """Lưu API keys"""
        api_key_text = self.api_key_input.toPlainText().strip()
        if not api_key_text:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập ít nhất một API key!")
            return
        
        try:
            self.gemini_service.set_api_key(api_key_text)
            num_keys = len(self.gemini_service.api_keys)
            if num_keys > 0:
                self.key_manager.save_keys(self.gemini_service.api_keys)
                self.statusBar().showMessage(f"✅ Đã lưu {num_keys} API key(s) thành công!")
                QMessageBox.information(self, "Thành công", f"Đã lưu {num_keys} API key(s)!\nKeys sẽ được nhớ cho lần sau.")
            else:
                QMessageBox.warning(self, "Cảnh báo", "Không tìm thấy API key hợp lệ nào!\nAPI key phải bắt đầu bằng 'AIza...'")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thiết lập API key: {e}")
    
    def _load_saved_keys(self):
        """Load API keys đã lưu từ file mã hóa"""
        try:
            saved_keys = self.key_manager.load_keys()
            if saved_keys:
                self.api_key_input.setPlainText("\n".join(saved_keys))
                self.gemini_service.api_keys = saved_keys
                self.statusBar().showMessage(f"✅ Đã load {len(saved_keys)} API key(s) từ lần trước.")
        except Exception as e:
            print(f"Không thể load saved keys: {e}")
    
    def import_txt_file(self):
        """Nhập file TXT và xử lý hàng loạt"""
        if not self.gemini_service.api_keys:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập và lưu Gemini API key trước!")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file danh sách QTKT", "", "Text Files (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse từng dòng, loại bỏ dòng trống và trùng lặp
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            qtkt_list = list(dict.fromkeys(lines))  # Loại trùng, giữ thứ tự
            
            if not qtkt_list:
                QMessageBox.warning(self, "Lỗi", "File không có nội dung hợp lệ!")
                return
            
            # Confirm
            reply = QMessageBox.question(
                self, "Xác nhận",
                f"Tìm thấy {len(qtkt_list)} quy trình kỹ thuật.\n\nBắt đầu xử lý?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.start_batch_processing(qtkt_list)
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể đọc file:\n{e}")
    
    def start_batch_processing(self, qtkt_list: list):
        """Bắt đầu xử lý hàng loạt"""
        # Clear table
        self.results_table.setRowCount(0)
        
        # Disable buttons, show stop button
        self.generate_btn.setEnabled(False)
        self.import_btn.setEnabled(False)
        self.stop_btn.setText("⏹️ Dừng")
        self.stop_btn.setEnabled(True)
        self.stop_btn.show()
        
        # Setup progress bar
        self.progress_bar.setRange(0, len(qtkt_list))
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        # Start batch thread
        self.batch_thread = BatchGenerateThread(self.gemini_service, qtkt_list)
        self.batch_thread.item_finished.connect(self.on_batch_item_finished)
        self.batch_thread.progress_update.connect(self.on_batch_progress)
        self.batch_thread.all_finished.connect(self.on_batch_all_finished)
        self.batch_thread.stopped.connect(self.on_batch_stopped)  # Connect stopped signal
        self.batch_thread.start()
        
        self.statusBar().showMessage(f"Đang xử lý {len(qtkt_list)} quy trình...")
    
    def on_stop_clicked(self):
        """Xử lý khi người dùng nhấn nút Dừng"""
        if self.batch_thread and self.batch_thread.isRunning():
            is_waiting = self.batch_thread.request_stop()
            self.stop_btn.setEnabled(False)
            self.stop_btn.setText("⏳ Đang dừng...")
            
            if is_waiting:
                QMessageBox.information(
                    self, "Đang dừng",
                    "Em đang chờ Gemini phản hồi, phản hồi xong em sẽ dừng ạ"
                )
            
            self.statusBar().showMessage("Đang dừng... chờ hoàn thành item hiện tại")
    
    def on_batch_item_finished(self, ten_quy_trinh: str, success: bool, model_or_error: str, content: dict):
        """Xử lý khi một item trong batch hoàn thành"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Cột 1: Tên quy trình
        self.results_table.setItem(row, 0, QTableWidgetItem(ten_quy_trinh))
        
        # Cột 2: Kết quả
        result_item = QTableWidgetItem("✅ Thành công" if success else "❌ Thất bại")
        result_item.setForeground(QColor("#4CAF50") if success else QColor("#f44336"))
        self.results_table.setItem(row, 1, result_item)
        
        # Cột 3: Model hoặc lỗi
        self.results_table.setItem(row, 2, QTableWidgetItem(model_or_error))
        
        # Nếu thành công, tự động xuất DOCX
        if success and content:
            self._auto_export_docx(content)
        
        # Scroll to bottom
        self.results_table.scrollToBottom()
    
    def on_batch_progress(self, current: int, total: int):
        """Cập nhật progress bar"""
        self.progress_bar.setValue(current)
        self.statusBar().showMessage(f"Đang xử lý: {current}/{total}...")
    
    def on_batch_all_finished(self):
        """Xử lý khi toàn bộ batch hoàn thành"""
        self.generate_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.stop_btn.hide()
        self.progress_bar.hide()
        
        # Count results
        total = self.results_table.rowCount()
        success = sum(1 for i in range(total) if "Thành công" in self.results_table.item(i, 1).text())
        
        self.statusBar().showMessage(f"✅ Hoàn thành! {success}/{total} quy trình thành công.")
        QMessageBox.information(
            self, "Hoàn thành",
            f"Đã xử lý xong {total} quy trình.\n\n✅ Thành công: {success}\n❌ Thất bại: {total - success}\n\n📁 File DOCX đã lưu vào thư mục 'QTKT ok'"
        )
    
    def on_batch_stopped(self):
        """Xử lý khi batch bị dừng bởi người dùng"""
        self.generate_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.stop_btn.hide()
        self.progress_bar.hide()
        
        # Count results
        total = self.results_table.rowCount()
        success = sum(1 for i in range(total) if "Thành công" in self.results_table.item(i, 1).text())
        
        self.statusBar().showMessage(f"⏹️ Đã dừng! {success}/{total} quy trình thành công.")
        QMessageBox.information(
            self, "Đã dừng",
            f"Đã dừng xử lý theo yêu cầu.\n\n✅ Thành công: {success}\n📁 File DOCX đã lưu vào thư mục 'QTKT ok'"
        )
    
    def _auto_export_docx(self, content: dict):
        """Tự động xuất file DOCX"""
        try:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "QTKT ok")
            os.makedirs(output_dir, exist_ok=True)
            
            ten_quy_trinh = content.get("ten_quy_trinh", "QTKT")
            safe_name = "".join(c for c in ten_quy_trinh if c.isalnum() or c in (' ', '-', '_')).strip()
            file_path = os.path.join(output_dir, f"{safe_name}.docx")
            
            self.docx_generator.create_document(content, file_path)
        except Exception as e:
            print(f"Lỗi xuất DOCX: {e}")
    
    def generate_content(self):
        """Tạo nội dung QTKT đơn lẻ"""
        ten_quy_trinh = self.input_field.text().strip()
        
        if not ten_quy_trinh:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên quy trình kỹ thuật!")
            return
        
        if not self.gemini_service.api_keys:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập và lưu Gemini API key trước!")
            return
        
        # Disable buttons and show progress
        self.generate_btn.setEnabled(False)
        self.import_btn.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.show()
        self.statusBar().showMessage(f"Đang tạo quy trình: {ten_quy_trinh}...")
        
        # Start generate thread
        self.generate_thread = GenerateThread(self.gemini_service, ten_quy_trinh)
        self.generate_thread.finished.connect(self.on_generate_finished)
        self.generate_thread.error.connect(self.on_generate_error)
        self.generate_thread.start()
    
    def on_generate_finished(self, result: dict):
        """Xử lý khi generate đơn lẻ xong"""
        self.current_content = result
        
        # Auto export DOCX
        self._auto_export_docx(result)
        
        # Add to table
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        self.results_table.setItem(row, 0, QTableWidgetItem(result.get("ten_quy_trinh", "")))
        result_item = QTableWidgetItem("✅ Thành công")
        result_item.setForeground(QColor("#4CAF50"))
        self.results_table.setItem(row, 1, result_item)
        self.results_table.setItem(row, 2, QTableWidgetItem(result.get("meta", {}).get("model_used", "N/A")))
        
        # Enable buttons
        self.generate_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.progress_bar.hide()
        
        self.statusBar().showMessage(f"✅ Đã tạo xong và xuất file DOCX!")
        self.input_field.clear()
    
    def on_generate_error(self, error_msg: str):
        """Xử lý khi có lỗi"""
        self.generate_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.progress_bar.hide()
        
        # Add to table
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        self.results_table.setItem(row, 0, QTableWidgetItem(self.input_field.text()))
        result_item = QTableWidgetItem("❌ Thất bại")
        result_item.setForeground(QColor("#f44336"))
        self.results_table.setItem(row, 1, result_item)
        self.results_table.setItem(row, 2, QTableWidgetItem(error_msg[:50]))
        
        QMessageBox.critical(self, "Lỗi", f"Không thể tạo nội dung:\n{error_msg}")
        self.statusBar().showMessage("❌ Lỗi khi tạo nội dung")

    # --- TAB 2: MERGER LOGIC ---
    
    def setup_merger_tab(self):
        """Thiết lập giao diện Tab Gộp File DOCX"""
        layout = QVBoxLayout(self.merger_tab)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header Merger
        header_text = QLabel("📚 Công cụ Gộp File Quy Trình")
        header_text.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_text)

        # Help text
        help_text = QLabel("Chọn nhiều file DOCX lẻ để gộp thành một file duy nhất (tự động ngắt trang).")
        help_text.setStyleSheet("color: #666;")
        help_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(help_text)

        # Control Frame
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #ddd; }")
        ctrl_layout = QVBoxLayout(ctrl_frame)
        ctrl_layout.setContentsMargins(20, 20, 20, 20)

        # File Selection Buttons
        btn_layout = QHBoxLayout()
        self.select_files_btn = QPushButton("📁 Chọn các file DOCX...")
        self.select_files_btn.setMinimumHeight(45)
        self.select_files_btn.clicked.connect(self.on_select_merge_files)
        self.select_files_btn.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #1976D2; }
        """)
        
        self.clear_list_btn = QPushButton("🗑️ Xóa danh sách")
        self.clear_list_btn.setMinimumHeight(45)
        self.clear_list_btn.clicked.connect(lambda: self.merge_list_widget.clear())
        
        btn_layout.addWidget(self.select_files_btn, 2)
        btn_layout.addWidget(self.clear_list_btn, 1)
        ctrl_layout.addLayout(btn_layout)

        # List Widget
        ctrl_layout.addWidget(QLabel("Các file sẽ được gộp (theo thứ tự từ trên xuống):"))
        self.merge_list_widget = SelectionListWidget()
        self.merge_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.merge_list_widget.setMinimumHeight(250)
        ctrl_layout.addWidget(self.merge_list_widget)
        
        # Output info
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Tên file gộp đầu ra:"))
        self.merge_output_name = QLineEdit("QTKT_Tong_Hop.docx")
        self.merge_output_name.setPlaceholderText("VD: QTKT_Noi_Khoa_V1.docx")
        output_row.addWidget(self.merge_output_name)
        ctrl_layout.addLayout(output_row)

        layout.addWidget(ctrl_frame)

        # Progress & Action
        self.merge_progress_bar = QProgressBar()
        self.merge_progress_bar.hide()
        layout.addWidget(self.merge_progress_bar)

        self.start_merge_btn = QPushButton("🚀 BẮT ĐẦU GỘP FILE")
        self.start_merge_btn.setMinimumHeight(55)
        self.start_merge_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.start_merge_btn.clicked.connect(self.start_merge_process)
        self.start_merge_btn.setStyleSheet("""
            QPushButton { background-color: #673AB7; color: white; border-radius: 8px; }
            QPushButton:hover { background-color: #5E35B1; }
            QPushButton:disabled { background-color: #ccc; }
        """)
        layout.addWidget(self.start_merge_btn)
        
        layout.addStretch()

    def on_select_merge_files(self):
        """Mở dialog chọn nhiều file để gộp"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Chọn các file DOCX để gộp", 
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "QTKT ok"), 
            "Word Files (*.docx)"
        )
        if files:
            for f in files:
                item = QListWidgetItem(f"📄 {os.path.basename(f)}")
                item.setData(Qt.UserRole, f) # Lưu path tuyệt đối
                item.setToolTip(f)
                self.merge_list_widget.addItem(item)
            self.statusBar().showMessage(f"Đã thêm {len(files)} file vào danh sách gộp.")

    def start_merge_process(self):
        """Bắt đầu quá trình gộp file trong thread riêng"""
        file_paths = []
        for i in range(self.merge_list_widget.count()):
            item = self.merge_list_widget.item(i)
            file_paths.append(item.data(Qt.UserRole))
        
        if not file_paths:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một file để gộp!")
            return
            
        output_name = self.merge_output_name.text().strip()
        if not output_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên file kết quả!")
            return
            
        if not output_name.lower().endswith(".docx"):
            output_name += ".docx"
            
        # Đường dẫn lưu: cùng folder "QTKT ok"
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "QTKT ok")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_name)
        
        # UI Update
        self.start_merge_btn.setEnabled(False)
        self.select_files_btn.setEnabled(False)
        self.clear_list_btn.setEnabled(False)
        self.merge_progress_bar.setRange(0, 100)
        self.merge_progress_bar.setValue(0)
        self.merge_progress_bar.show()
        self.statusBar().showMessage("Đang bắt đầu gộp file...")

        # Worker
        self.merge_worker = MergeWorker(file_paths, output_path)
        self.merge_worker.progress.connect(self.update_merge_progress)
        self.merge_worker.finished_signal.connect(self.on_merge_finished)
        self.merge_worker.start()

    def update_merge_progress(self, current, total, filename):
        """Cập nhật tiến trình gộp"""
        percent = int((current / total) * 100)
        self.merge_progress_bar.setValue(percent)
        self.statusBar().showMessage(f"Đang gộp ({current}/{total}): {filename}")

    def on_merge_finished(self, success, message):
        """Kết thúc quá trình gộp"""
        self.start_merge_btn.setEnabled(True)
        self.select_files_btn.setEnabled(True)
        self.clear_list_btn.setEnabled(True)
        self.merge_progress_bar.hide()
        
        if success:
            self.statusBar().showMessage("✅ Đã gộp file thành công!")
            QMessageBox.information(self, "Thành công", message)
        else:
            self.statusBar().showMessage("❌ Lỗi khi gộp file")
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra khi gộp:\n{message}")
