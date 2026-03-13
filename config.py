"""
Configuration for QTKT Generator App
"""
import os

# Gemini API Key - lấy từ environment variable hoặc nhập trực tiếp
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Document formatting constants (theo QĐ 3023/QĐ-BYT)
FONT_NAME = "Times New Roman"
FONT_SIZE = 13  # pt
LINE_SPACING = 1.0
MARGIN_TOP = 2.5  # cm
MARGIN_BOTTOM = 2.0  # cm
MARGIN_LEFT = 3.0  # cm
MARGIN_RIGHT = 2.5  # cm
PARAGRAPH_BEFORE = 6  # pt
PARAGRAPH_AFTER = 0  # pt

# App info
APP_NAME = "QTKT Generator"
APP_VERSION = "1.0.0"
