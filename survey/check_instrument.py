#!/usr/bin/env python3
"""问卷题项校验器 —— 任务 16 [A1.3] 的守卫。

问卷里有几处约束是**写错就静默失效**的：选项措辞与判定阶梯绑定、M11 只此一处数据源、
M3 需要「打开即计数」的埋点。纯文档无法防止这些在后续编辑中漂移，故做机器校验。

校验四件事：

1. **枚举一致** —— 题项导出的取值集合必须等于 `survey_responses.csv` schema 的
   `choices`，不多不少。多了会被 `load_csv` 报错，少了则该选项静默归入「其他」。
2. **指标覆盖** —— schema 里每个供指标计算的字段，必须有题项产出。
3. **口径绑定** —— M4/M12 的分子选项必须与 `compute_metrics.py` 的判定逻辑一致。
4. **埋点存在** —— M3 需要开始与提交两处计数，且选项须随机化。

用法::

    python3 survey/check_instrument.py
    python3 survey/check_instrument.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
QUESTIONS = ROOT / "questions.json"

sys.path.insert(0, str(REPO / "validation"))
import compute_metrics as cm  # noqa: E402


class InstrumentError(Exception):
    pass


def load() -> dict:
    return json.loads(QUESTIONS.read_text(encoding="utf-8"))


def _by_id(instr: dict) -> dict[str, dict]:
    return {q["id"]: q for q in instr["questions"]}


def _opts(q: dict) -> list[dict]:
    """把纯字符串选项归一化为 {label, value, numerator}。"""
    out = []
    for o in q["options"]:
        if isinstance(o, str):
            out.append({"label": o, "value": None, "numerator": False})
        else:
            out.append(o)
    return out


def check(instr: dict) -> list[str]:
    """返回问题列表；空列表表示全部通过。"""
    problems: list[str] = []
    schema = cm.SCHEMAS["survey_responses"]
    by_id = _by_id(instr)
    exported = {q["export_field"]: q for q in instr["questions"] if q.get("export_field")}

    # ---- 1. 枚举值与 schema 一致 ----
    for field in ("m4_answer", "m12_answer"):
        col = schema.by_name()[field]
        if field not in exported:
            problems.append(f"{field}：schema 中有该列，但问卷没有产出它的题项 —— 该指标无法计算")
            continue
        values = {o["value"] for o in _opts(exported[field]) if o["value"]}
        expected = set(col.choices or ())
        if values != expected:
            missing, extra = expected - values, values - expected
            if missing:
                problems.append(f"{field}：缺少取值 {sorted(missing)}")
            if extra:
                problems.append(f"{field}：出现 schema 未定义的取值 {sorted(extra)}（load_csv 会报错）")

    # ---- 2. 指标字段覆盖 ----
    # differentiation_needs 是 list 列，不在 enum 检查里，但必须有题项
    for field in ("m4_answer", "m12_answer", "differentiation_needs"):
        if field not in exported:
            problems.append(f"{field}：无题项产出")

    # ---- 3. 口径绑定 ----
    # M4：恰好一个分子选项，且值为 very_needed
    if "m4_answer" in exported:
        nums = [o for o in _opts(exported["m4_answer"]) if o.get("numerator")]
        if len(nums) != 1:
            problems.append(f"M4：应有且仅有 1 个分子选项，实际 {len(nums)} 个")
        elif nums[0]["value"] != "very_needed":
            problems.append(f"M4：分子选项的值应为 very_needed，实际 {nums[0]['value']!r}")

    # M12：分子应为 agree + strongly_agree
    if "m12_answer" in exported:
        nums = sorted(o["value"] for o in _opts(exported["m12_answer"]) if o.get("numerator"))
        if nums != ["agree", "strongly_agree"]:
            problems.append(f"M12：分子应为 agree + strongly_agree，实际 {nums}")

    # M11：必须是不限项多选
    if "differentiation_needs" in exported:
        q = exported["differentiation_needs"]
        if q["type"] != "multi":
            problems.append("M11：题型必须是多选（single 无法产出列表）")
        if not q.get("unlimited_choices"):
            problems.append("M11：必须不限项（unlimited_choices=true），否则 3 项以上无法勾选")

    # ---- 4. 埋点与问卷卫生 ----
    if not instr.get("M3_requires_start_event"):
        problems.append("M3：必须配置「打开问卷即计数」，否则开始数无从取得，M3 不可计算")
    if not instr.get("randomize_all_options"):
        problems.append("未开启选项随机化（任务 Restrictions 要求抑制顺序偏差）")
    if not instr.get("intro"):
        problems.append("缺少问卷开头说明文案（避免引导性作答的必要措施）")

    for field in ("survey_started", "submitted_at", "source_channel"):
        if field not in schema.by_name():
            problems.append(f"schema 缺少列 {field}")

    # 指标题项必须存在（防止误删导致某指标永久无数据源）
    for mid, qid in (("M4", "Q8"), ("M11", "Q9"), ("M12", "Q10")):
        if qid not in by_id:
            problems.append(f"{mid} 的题项 {qid} 已丢失")
        elif by_id[qid].get("metric") != mid:
            problems.append(f"{qid} 的 metric 标注应为 {mid}，实际 {by_id[qid].get('metric')!r}")

    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="问卷题项校验器（任务 16 / A1.3）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    instr = load()
    problems = check(instr)

    if args.json:
        print(json.dumps({"ok": not problems, "problems": problems}, ensure_ascii=False, indent=2))
        return 0 if not problems else 1

    q = instr["questions"]
    metrics = [x for x in q if x.get("metric") and "旁证" not in (x.get("metric") or "")]
    print(f"问卷：{instr['title']}")
    print(f"题量：{len(q)} 题，预计 {instr['estimated_minutes']} 分钟")
    print(f"指标题：{', '.join(x['metric'] for x in metrics)}")
    print(f"M3 开始埋点：{'已配置' if instr.get('M3_requires_start_event') else '未配置'}")
    print(f"选项随机化：{'已开启' if instr.get('randomize_all_options') else '未开启'}")
    print()

    if problems:
        print(f"✗ 发现 {len(problems)} 处问题：")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("✓ 题项与 validation 的 schema、判定阶梯一致")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())