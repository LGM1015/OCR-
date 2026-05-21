import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_ocr import DocumentOCR
from table_recognizer import TableRecognizer
from screenshot_ocr import ScreenshotOCR


def main():
    os.makedirs("output", exist_ok=True)

    while True:
        print("\n=== OCR 工具集 ===")
        print("1. 文档识别 (图片/PDF → TXT/JSON)")
        print("2. 表格识别 (图片 → Excel)")
        print("3. 截图识字 (截屏 → 文字)")
        print("q. 退出")
        choice = input("\n请选择功能: ").strip()

        if choice == "1":
            path = input("请输入图片路径: ").strip().strip('"')
            if os.path.exists(path):
                ocr = DocumentOCR()
                result = ocr.run(path)
                print(f"\n识别结果:\n{result['text'][:500]}...")
            else:
                print("文件不存在")

        elif choice == "2":
            path = input("请输入图片路径: ").strip().strip('"')
            if os.path.exists(path):
                ocr = TableRecognizer()
                result = ocr.run(path)
                print(f"\n表格已保存: {result['output_path']}")
            else:
                print("文件不存在")

        elif choice == "3":
            ocr = ScreenshotOCR()
            ocr.run()

        elif choice == "q":
            print("再见!")
            break


if __name__ == "__main__":
    main()