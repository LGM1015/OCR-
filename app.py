"""
Flask API - 提供 OCR 功能的后端服务
"""

import os
import io
import base64
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# PaddleOCR 模型持久化路径（Railway 持久卷）
PADDLE_HOME = os.environ.get("PADDLE_HOME", "/persist/paddle_models")
os.makedirs(PADDLE_HOME, exist_ok=True)
os.environ["PADDLE_HOME"] = PADDLE_HOME

from document_ocr import DocumentOCR
from table_recognizer import TableRecognizer
from screenshot_ocr import ScreenshotOCR

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif", "bmp", "webp", "pdf"}

os.makedirs("output", exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "OCR 服务运行中"})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory("output", filename)


@app.route("/api/document-ocr", methods=["POST"])
def document_ocr():
    """文档识别 API"""
    if "file" not in request.files and "image" not in request.form:
        return jsonify({"error": "请上传图片文件"}), 400

    try:
        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "未选择文件"}), 400

            # 保存临时文件，保留原始扩展名
            original_ext = os.path.splitext(file.filename)[1].lower()
            import uuid
            temp_filename = f"temp_{uuid.uuid4().hex}{original_ext}"
            temp_path = f"output/{temp_filename}"
            file.save(temp_path)
        else:
            # 处理 base64 图片
            image_data = request.form.get("image")
            if image_data.startswith("data:"):
                image_data = image_data.split(",")[1]
            img_bytes = base64.b64decode(image_data)
            temp_path = "output/temp_upload.png"
            with open(temp_path, "wb") as f:
                f.write(img_bytes)

        ocr = DocumentOCR()
        result = ocr.run(temp_path)

        # 清理临时文件
        try:
            os.remove(temp_path)
        except:
            pass

        return jsonify({
            "success": True,
            "text": result["text"],
            "line_count": len(result["lines"]),
            "lines": result["lines"][:50],
            "txt_path": result.get("txt_path"),
            "json_path": result.get("json_path"),
            "docx_path": result.get("docx_path"),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/table-ocr", methods=["POST"])
def table_ocr():
    """表格识别 API"""
    if "file" not in request.files:
        return jsonify({"error": "请上传图片文件"}), 400

    try:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "未选择文件"}), 400

        filename = secure_filename(file.filename)
        temp_path = f"output/temp_{filename}"
        file.save(temp_path)

        ocr = TableRecognizer()
        result = ocr.run(temp_path)

        try:
            os.remove(temp_path)
        except:
            pass

        return jsonify({
            "success": True,
            "output_path": result["output_path"],
            "rows": result["rows"],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/screenshot-ocr", methods=["POST"])
def screenshot_ocr():
    """截图识别 API - 接收截图并识别"""
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "请提供 base64 图片"}), 400

        image_data = data["image"]
        if image_data.startswith("data:"):
            image_data = image_data.split(",")[1]

        img_bytes = base64.b64decode(image_data)
        temp_path = "output/temp_screenshot.png"
        with open(temp_path, "wb") as f:
            f.write(img_bytes)

        ocr = ScreenshotOCR()
        result = ocr.from_file(temp_path)

        try:
            os.remove(temp_path)
        except:
            pass

        return jsonify({
            "success": True,
            "text": result["text"],
            "line_count": result["line_count"],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/screenshot-region", methods=["POST"])
def screenshot_region():
    """Windows 区域截图 + OCR"""
    try:
        from screenshot_ocr import select_region
        import time

        temp_path = None

        # 通过子进程启动 tkinter 截图（避免阻塞）
        import subprocess
        result = subprocess.run(
            ["python", "-c",
             "from screenshot_ocr import select_region; import sys; "
             "p = select_region(); print(p if p else 'CANCELLED')"],
            capture_output=True, text=True, timeout=30
        )

        temp_path = result.stdout.strip()

        if not temp_path or temp_path == "CANCELLED":
            return jsonify({"error": "已取消截图"}), 400

        ocr = ScreenshotOCR()
        ocr_result = ocr.from_file(temp_path)

        try:
            os.remove(temp_path)
        except:
            pass

        return jsonify({
            "success": True,
            "text": ocr_result["text"],
            "line_count": ocr_result["line_count"],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("启动 OCR 服务: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)