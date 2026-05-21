# OCR 工具集

基于 PaddleOCR 的在线 OCR 工具，支持文档识别、表格提取功能。
<img width="2122" height="1077" alt="image" src="https://github.com/user-attachments/assets/2150d599-b2c9-45f7-b3cd-528055b0dcfd" />

## 功能特性

### 📄 文档识别

- 支持图片（PNG、JPG、BMP、WebP）和 PDF 文件
- 输出格式：纯文本（TXT）、结构化数据（JSON）、Word 文档（DOCX）
- 自动识别中英文，支持多页 PDF 转换

### 📊 表格提取

- 上传表格图片，自动解析为 Excel 文件
- 基于坐标聚类算法精准分行分列
- 输出为 xlsx 格式，可直接编辑


## 技术栈

| 层级   | 技术                              |
|--------|-----------------------------------|
| 后端   | Python + Flask                    |
| OCR 引擎 | PaddleOCR v3.5.0 + PaddlePaddle 3.2.2 |
| 表格处理 | Pandas + openpyxl                |
| PDF 处理 | PyMuPDF                          |
| Word 导出 | python-docx                      |
| 前端   | 原生 HTML/CSS/JS                  |

## 快速部署

### 环境要求

```bash
pip install -r requirements.txt
```

### 运行

```bash
python app.py
```

访问 <http://localhost:5000> 即可使用。

### Docker 部署

```bash
docker build -t ocr-tool .
docker run -d -p 5000:5000 ocr-tool
```

### 云端部署（Railway）

1. 将代码推送到 GitHub
2. 在 Railway 连接仓库
3. 设置启动命令：`python app.py`
4. 访问分配的公网域名

## 项目结构

```
├── app.py                 # Flask API 主服务
├── document_ocr.py       # 文档识别模块
├── table_recognizer.py   # 表格提取模块
├── screenshot_ocr.py    # 截图 OCR 模块
├── templates/index.html # 前端页面
└── requirements.txt     # Python 依赖
```

## 环境变量

| 变量名     | 说明                   | 默认值                  |
|------------|------------------------|-------------------------|
| `PADDLE_HOME` | PaddleOCR 模型缓存路径 | `/persist/paddle_models` |

## 许可证

MIT License
