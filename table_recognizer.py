"""
模块2: 表格识别 - 图片/截图 转 Excel
使用 PaddleOCR + 位置分析分行分列
"""

import os
import numpy as np
import pandas as pd
from paddleocr import PaddleOCR


class TableRecognizer:
    def __init__(self):
        self.ocr = PaddleOCR(lang="ch", use_angle_cls=True)

    def run(self, image_path, output_path=None):
        """执行表格识别"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"文件不存在: {image_path}")

        os.makedirs("output", exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        if output_path is None:
            output_path = f"output/{base_name}_table.xlsx"

        result = self.ocr.ocr(image_path)

        # 解析文本和位置信息
        cells = []
        if result and isinstance(result, list) and len(result) > 0:
            ocr_result = result[0]
            res = ocr_result.json.get('res', {})
            rec_texts = res.get('rec_texts', [])
            dt_polys = res.get('dt_polys', [])

            for i, text in enumerate(rec_texts):
                if text.strip() and i < len(dt_polys):
                    poly = dt_polys[i]
                    y_center = np.mean([p[1] for p in poly])
                    x_center = np.mean([p[0] for p in poly])
                    cells.append({
                        'text': text,
                        'x': x_center,
                        'y': y_center
                    })

        if not cells:
            df = pd.DataFrame()
            df.to_excel(output_path, index=False, header=False)
            return {"output_path": output_path, "rows": 0}

        # 提取位置用于分行分列
        y_positions = [c['y'] for c in cells]
        x_positions = [c['x'] for c in cells]

        # 聚类 Y 得到行
        row_clusters = self._cluster(y_positions, tolerance=25)
        # 聚类 X 得到列
        col_clusters = self._cluster(x_positions, tolerance=40)

        # 分配到网格
        grid = {}
        for c in cells:
            row = self._nearest(c['y'], row_clusters)
            col = self._nearest(c['x'], col_clusters)
            key = (row, col)
            if key not in grid:
                grid[key] = []
            grid[key].append(c['text'])

        # 构建表格
        max_row = max(k[0] for k in grid.keys()) + 1
        max_col = max(k[1] for k in grid.keys()) + 1

        data = []
        for r in range(max_row):
            row_data = []
            for c in range(max_col):
                texts = grid.get((r, c), [])
                row_data.append(' '.join(texts))
            data.append(row_data)

        df = pd.DataFrame(data)
        df.to_excel(output_path, index=False, header=False)

        return {"output_path": output_path, "rows": len(data)}

    def _cluster(self, positions, tolerance=20):
        """简单线性聚类"""
        if not positions:
            return []
        sorted_pos = sorted(set(positions))
        clusters = []
        current = [sorted_pos[0]]

        for pos in sorted_pos[1:]:
            if pos - current[-1] <= tolerance:
                current.append(pos)
            else:
                clusters.append(sum(current) / len(current))
                current = [pos]
        clusters.append(sum(current) / len(current))
        return clusters

    def _nearest(self, value, clusters):
        return min(range(len(clusters)), key=lambda i: abs(clusters[i] - value))