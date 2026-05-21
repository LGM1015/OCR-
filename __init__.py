"""
PaddleOCR 工具集
文档识别 / 表格提取 / 截图识字
"""

from .document_ocr import DocumentOCR
from .table_recognizer import TableRecognizer
from .screenshot_ocr import ScreenshotOCR

__all__ = ["DocumentOCR", "TableRecognizer", "ScreenshotOCR"]