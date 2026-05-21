"""
模块3: 截图识字 - 截屏 → OCR → 复制到剪贴板
使用 PaddleOCR
"""

import os
import pyperclip
from paddleocr import PaddleOCR


class ScreenshotOCR:
    def __init__(self):
        self.ocr = PaddleOCR(lang="ch", use_angle_cls=True)

    def run(self):
        """截图并识别文字，自动复制到剪贴板"""
        print("3秒后开始截图...")
        import time
        time.sleep(3)

        img_path = self._screenshot()
        if img_path is None:
            print("截图已取消")
            return

        result = self.ocr.ocr(img_path)
        self._process_and_copy(result)

        try:
            os.remove(img_path)
        except:
            pass

    def _process_and_copy(self, result):
        texts = []
        if result and isinstance(result, list) and len(result) > 0:
            ocr_result = result[0]
            res = ocr_result.json.get('res', {})
            texts = [text for text in res.get('rec_texts', []) if text.strip()]

        full_text = "\n".join(texts)

        if full_text.strip():
            pyperclip.copy(full_text)
            print(f"\n已识别并复制到剪贴板:\n{full_text[:300]}...")
        else:
            print("未识别到文字")

    def _screenshot(self):
        """截取全屏"""
        temp_path = "output/screenshot_temp.png"
        os.makedirs("output", exist_ok=True)

        try:
            import pyautogui
            img = pyautogui.screenshot()
            img.save(temp_path)
            return temp_path
        except ImportError:
            import mss
            with mss.mss() as s:
                s.shot(output=temp_path)
            return temp_path

    def from_file(self, image_path):
        """从文件识别并复制"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"文件不存在: {image_path}")

        result = self.ocr.ocr(image_path)

        texts = []
        if result and isinstance(result, list) and len(result) > 0:
            ocr_result = result[0]
            res = ocr_result.json.get('res', {})
            texts = [text for text in res.get('rec_texts', []) if text.strip()]

        full_text = "\n".join(texts)

        if full_text.strip():
            pyperclip.copy(full_text)
            print(f"已复制到剪贴板:\n{full_text[:300]}...")
        else:
            print("未识别到文字")

        return {"text": full_text, "line_count": len(texts)}