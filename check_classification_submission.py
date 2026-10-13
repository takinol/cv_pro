# -*- coding: utf-8 -*-
"""检查图像级多标签分类预测 JSON 的基本格式。"""

import json
import math
import re
import sys
from pathlib import Path


# ==================== 请填写文件位置 ====================
PREDICTION_PATH = Path(
    r"C:\Users\Legion\Desktop\computer_vision_dataset\classification_predictions.json"
)
# ========================================================

CATEGORY_COUNT = 10
REQUIRED_FIELDS = {"image_id", "scores"}
FILENAME_PATTERN = re.compile(r"^[0-9]+_[^_\s]+_classification_predictions\.json$")
SCORE_PATTERN = re.compile(r"^(?:0\.\d{3}|1\.000)$")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    if not PREDICTION_PATH.is_file():
        print(f"检查失败：文件不存在：{PREDICTION_PATH}")
        return 1

    if FILENAME_PATTERN.fullmatch(PREDICTION_PATH.name) is None:
        print("检查失败：文件名必须为“学号_姓名_classification_predictions.json”")
        print("示例：20230001_张三_classification_predictions.json")
        return 1

    try:
        raw_text = PREDICTION_PATH.read_text(encoding="utf-8-sig")
        predictions = json.loads(raw_text)
        number_tokens = json.loads(raw_text, parse_float=str, parse_int=str)
    except json.JSONDecodeError as error:
        print(f"检查失败：JSON 语法错误，第 {error.lineno} 行，第 {error.colno} 列")
        return 1
    except UnicodeDecodeError:
        print("检查失败：文件必须使用 UTF-8 编码")
        return 1

    errors = []

    if not isinstance(predictions, list):
        errors.append("JSON 最外层必须是数组 []")
    else:
        image_ids = set()

        for index, item in enumerate(predictions, start=1):
            prefix = f"第 {index} 条记录"

            if not isinstance(item, dict):
                errors.append(f"{prefix}必须是对象 {{}}")
                continue

            missing = REQUIRED_FIELDS - set(item)
            extra = set(item) - REQUIRED_FIELDS

            if missing:
                errors.append(f"{prefix}缺少字段：{', '.join(sorted(missing))}")
            if extra:
                errors.append(f"{prefix}包含多余字段：{', '.join(sorted(extra))}")

            image_id = item.get("image_id")
            if isinstance(image_id, bool) or not isinstance(image_id, int):
                errors.append(f"{prefix}的 image_id 必须是整数")
            elif image_id in image_ids:
                errors.append(f"image_id={image_id} 重复")
            else:
                image_ids.add(image_id)

            scores = item.get("scores")
            if not isinstance(scores, list):
                errors.append(f"{prefix}的 scores 必须是数组")
                continue

            if len(scores) != CATEGORY_COUNT:
                errors.append(
                    f"{prefix}的 scores 必须有 10 个分数，当前有 {len(scores)} 个"
                )
                continue

            invalid_scores = [
                score
                for score in scores
                if (
                    isinstance(score, bool)
                    or not isinstance(score, (int, float))
                    or not math.isfinite(score)
                    or not 0 <= score <= 1
                )
            ]
            if invalid_scores:
                errors.append(
                    f"{prefix}包含非法分数，分数必须是 0 到 1 之间的数字"
                )

            token_item = number_tokens[index - 1]
            token_scores = token_item.get("scores") if isinstance(token_item, dict) else None
            if isinstance(token_scores, list) and len(token_scores) == CATEGORY_COUNT:
                invalid_decimal_positions = [
                    position
                    for position, token in enumerate(token_scores, start=1)
                    if not isinstance(token, str) or SCORE_PATTERN.fullmatch(token) is None
                ]
                if invalid_decimal_positions:
                    errors.append(
                        f"{prefix}的 scores 必须全部保留 3 位小数，"
                        f"不符合的位置：{invalid_decimal_positions}"
                    )

    if errors:
        print("格式检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("格式检查通过，可以提交。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
