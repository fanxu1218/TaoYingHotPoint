"""把实际采集状态写入 Actions 摘要，并为平台失败生成注解。"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict


SOURCE_LABELS = {
    "baidu": "百度", "weibo": "微博", "toutiao": "今日头条",
    "xiaohongshu": "小红书", "tencent": "腾讯",
}


def annotate(level: str, title: str, message: str) -> None:
    # 平台错误可能包含换行或百分号，不能原样拼入工作流命令。
    def escape(value: str) -> str:
        return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")

    print(f"::{level} title={escape(title)}::{escape(message)}")


def render_report(report: Dict[str, Any]) -> str:
    sources = report["sources"]
    failed = [source for source, result in sources.items() if result["status"] != "success"]
    lines = ["## 每日热点采集结果", "", f"- 整体状态：**{'部分成功' if failed else '全部成功'}**", ""]
    if len(failed) == len(sources):
        lines[2] = "- 整体状态：**全部失败**"
    lines.extend(["| 平台 | 要求 | 结果 | 条数 |", "| --- | --- | --- | --- |"])
    for source, result in sources.items():
        label = SOURCE_LABELS.get(source, source)
        required = result.get("required", True)
        success = result["status"] == "success"
        outcome = "成功" if success else "失败" if required else "暂不可用"
        lines.append(f"| {label} | {'必需' if required else '可选'} | {outcome} | {result['count']} |")
        if not success:
            annotate("error" if required else "warning", f"{label}采集{outcome}", str(result.get("error", "无可用榜单")))

    usage = report.get("database") or {}
    status = usage.get("status")
    lines.extend(["", "## 数据库容量", ""])
    if status in {"ok", "warning", "critical"}:
        lines.append(f"- 已使用：**{usage['size_mb']} MB / {usage['limit_mb']} MB**（{usage['usage_percent']}%）")
        lines.append(f"- 预警阈值：**{usage['warning_mb']} MB**")
        if status != "ok":
            annotate("warning", "数据库容量预警", lines[-2])
    elif status == "unavailable":
        lines.append("- 容量读取失败，详见原始报告。")
        annotate("warning", "数据库容量监控", str(usage.get("error", "无可用数据")))
    else:
        lines.append("- 未查询（例如只读试运行）。")
    lines.extend(["", "## 原始采集报告", "", "```json", json.dumps(report, ensure_ascii=False, indent=2), "```", ""])
    return "\n".join(lines)


def main() -> int:
    try:
        report = json.loads(Path("collection-status.json").read_text(encoding="utf-8"))
        summary = render_report(report)
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as output:
            output.write(summary)
    except (OSError, ValueError, KeyError, TypeError) as error:
        annotate("error", "采集状态报告", f"无法生成有效的采集报告：{error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
