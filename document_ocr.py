"""
模块1: 文档识别 - 图片/PDF 转为 TXT/JSON
使用 PaddleOCR
"""

import os
import json
import fitz
from paddleocr import PaddleOCR
from docx import Document


class DocumentOCR:
    def __init__(self, lang="ch"):
        self.ocr = PaddleOCR(lang=lang, use_angle_cls=True)

    def run(self, image_path, output_format="both"):
        """执行文档识别"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"文件不存在: {image_path}")

        ext = os.path.splitext(image_path)[1].lower()
        if ext == ".pdf":
            image_paths = self._pdf_to_images(image_path)
        else:
            image_paths = [image_path]

        all_texts = []
        full_text = ""

        for img_path in image_paths:
            result = self.ocr.ocr(img_path)
            if result and isinstance(result, list) and len(result) > 0:
                ocr_result = result[0]
                res = ocr_result.json.get('res', {})

                rec_texts = res.get('rec_texts', [])
                rec_scores = res.get('rec_scores', [])
                dt_polys = res.get('dt_polys', [])
                rec_polys = res.get('rec_polys', [])

                for i, text in enumerate(rec_texts):
                    confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                    poly = rec_polys[i] if i < len(rec_polys) else []
                    bbox = [[float(p) for p in point] for point in poly] if len(poly) > 0 else []
                    all_texts.append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": bbox
                    })
                    full_text += text + "\n"

        os.makedirs("output", exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]

        output = {"text": full_text.strip(), "lines": all_texts}

        if output_format in ("txt", "both"):
            txt_path = f"output/{base_name}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(full_text.strip())

        if output_format in ("json", "both"):
            json_path = f"output/{base_name}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)

        if output_format in ("docx", "both"):
            docx_path = f"output/{base_name}.docx"
            doc = Document()
            for line in all_texts:
                doc.add_paragraph(line['text'])
            doc.save(docx_path)

        return {
            "text": full_text.strip(),
            "lines": all_texts,
            "txt_path": txt_path if output_format in ("txt", "both") else None,
            "json_path": json_path if output_format in ("json", "both") else None,
            "docx_path": docx_path if output_format in ("docx", "both") else None,
        }

    def _pdf_to_images(self, pdf_path):
        """将 PDF 转换为图片列表"""
        doc = fitz.open(pdf_path)
        image_paths = []
        os.makedirs("output", exist_ok=True)

        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=150)
            img_data = pix.tobytes("png")
            temp_path = f"output/temp_pdf_page_{page_num}.png"
            with open(temp_path, "wb") as f:
                f.write(img_data)
            image_paths.append(temp_path)

        doc.close()
        return image_paths