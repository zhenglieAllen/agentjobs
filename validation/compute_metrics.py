#!/usr/bin/env python3
"""AgentJobs 验证指标计算器 —— 任务 15 [A1.2]。

从 5 份结构化 CSV 计算 M1–M12 / S1–S3 / D1–D2，并对照
`.spec-workflow/specs/agentjobs/validation-metrics.md` 的「判定阶梯」给出判定。

设计约束（来自 A1.2 任务定义，不可违反）：

1. **阈值不得硬编码。** 全部阈值在运行时从 validation-metrics.md 的判定阶梯
   表格解析。若该表格式变化或数值更新，脚本自动跟随，不需要改代码。
2. **缺列或枚举值非法必须明确报错**，不得静默跳过，也不得按 0 处理。
3. **样本量门槛语义**：S1/S2/S3 未达标时不判失败，而是用已完成样本重算
   M4–M12 并输出提示。
4. **D2 特殊规则**：D2 ≥ 1 可单独支撑「继续」；D2 = 0 且 M1–M12 中 ≥ 3 项
   未达标时输出风险 4（双边市场冷启动）告警。

用法::

    python3 validation/compute_metrics.py --data-dir validation/data
    python3 validation/compute_metrics.py --data-dir validation/data --json
    python3 validation/compute_metrics.py --data-dir validation/data \\
        --window-start 2026-10-07
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_THRESHOLDS = REPO_ROOT / ".spec-workflow" / "specs" / "agentjobs" / "validation-metrics.md"


# --------------------------------------------------------------------------
# 错误类型
# --------------------------------------------------------------------------


class SchemaError(Exception):
    """schema 不合法：缺列、枚举值非法、数值越界等。必须让调用方失败。"""


# --------------------------------------------------------------------------
# 阈值：从 validation-metrics.md 的判定阶梯解析
# --------------------------------------------------------------------------

OPERATORS = {"≥": ">=", "⩾": ">=", "<=": "<=", "≤": "<=", "<": "<", ">": ">", "=": "="}

# 「≥ 8/10」这类写作必须能识别为 score（分）而非 count，否则 M7/M10 的量纲判断会错
_BOUND_RE = re.compile(
    r"^\s*(≥|⩾|<=|≤|>|<|=)\s*([0-9]+(?:\.[0-9]+)?)\s*(%|个|家|次)?\s*(?:/\s*10)?\s*$"
)
_BOUND_BARE_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(%|个|家|次)?\s*(?:/\s*10)?\s*$")


@dataclass(frozen=True)
class Bound:
    op: str
    value: float
    unit: str

    def fmt(self, kind: str) -> str:
        sign = {">=": "≥", "<=": "≤", "<": "<", ">": ">", "=": "="}[self.op]
        # 自身带计数单位的（如 M8 的「0 家」表示 0 家企业，而非 0%）优先按计数渲染
        if self.unit in ("家", "个", "次"):
            return f"{sign} {self.value:g}{self.unit}"
        if kind == "ratio":
            return f"{sign} {self.value * 100:g}%"
        if kind == "score":
            return f"{sign} {self.value:g}/10"
        return f"{sign} {self.value:g}{self.unit}"

    def __str__(self) -> str:
        return self.fmt("count")


@dataclass(frozen=True)
class Threshold:
    key: str
    metric_id: str
    name: str
    ideal: Bound
    passed: Bound
    fail: Bound
    kind: str  # ratio | score | count
    lower_is_better: bool

    @property
    def raw(self) -> str:
        return (
            f"理想 {self.ideal.fmt(self.kind)} / "
            f"通过 {self.passed.fmt(self.kind)} / "
            f"失败 {self.fail.fmt(self.kind)}"
        )


def _kind_of(bounds: Iterable[Bound]) -> str:
    units = {b.unit for b in bounds}
    if "%" in units:
        return "ratio"
    if "分" in units:
        return "score"
    return "count"


def _parse_bound(raw: str) -> Bound:
    text = raw.strip()
    m = _BOUND_RE.match(text)
    if m:
        op, num, unit = m.group(1), float(m.group(2)), m.group(3)
        # 「≥ 8/10」「≤ 4/10」：分母为 10 的量表，量纲是分
        if unit is None and "/10" in text.replace(" ", ""):
            unit = "分"
        return _normalize(Bound(OPERATORS[op], num, unit or ""))

    m = _BOUND_BARE_RE.match(text)
    if m:
        num, unit = float(m.group(1)), m.group(2) or ""
        if unit is None and "/10" in text.replace(" ", ""):
            unit = "分"
        # 「0 家」「0 个」这类无运算符写法语义为 == 0（未达底线）
        return _normalize(Bound("=", num, unit))
    raise SchemaError(f"无法解析阈值表达式：{raw!r}（判定阶梯格式可能已变更）")


def _normalize(b: Bound) -> Bound:
    """百分比归一化为小数，使实测值（同样以小数存储）与之同量纲。

    文档写作「≥ 80%」，实测量按 0.80 计算，故此处除以 100。
    """
    return Bound(b.op, b.value / 100.0, b.unit) if b.unit == "%" else b


def _distinguish(metric_id: str, name: str, dupe: bool) -> str:
    """只有同一 ID 出现多行时（如 M1 首周 / 次周累计）才需要加限定词。

    M10 的指标名本身含括号（「现有平台满意度（越低越好）」），但它只出现一行，
    不应因此把 key 变成 `M10.越低越好`——调用方按 ID 查找。
    """
    if not dupe:
        return metric_id
    m = re.search(r"[（(]([^）)]+)[）)]", name)
    return f"{metric_id}.{m.group(1)}" if m else metric_id


def load_thresholds(md_path: Path) -> dict[str, Threshold]:
    """从 validation-metrics.md 的「判定阶梯」表格解析全部阈值。

    判定阶梯表格形如::

        | 编号 | 指标 | 理想值 | 通过值 | 失败值 |
        |---|---|---|---|---|
        | M1  | 着陆页邮件订阅（首周） | ≥ 100 | ≥ 50 | < 10 |
    """
    if not md_path.exists():
        raise SchemaError(f"阈值真相源不存在：{md_path}")

    text = md_path.read_text(encoding="utf-8")

    # 只取「判定阶梯」小节，避免抓到正文里的散落阈值
    section = re.search(r"##\s*判定阶梯.*?\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    if not section:
        raise SchemaError(f"{md_path} 中找不到「判定阶梯」小节")

    rows: list[list[str]] = []
    counts: dict[str, int] = {}
    for line in section.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        metric_id = cells[0]
        if not re.fullmatch(r"[A-Z]\d+", metric_id):  # 表头行 / 分隔行
            continue
        rows.append(cells)
        counts[metric_id] = counts.get(metric_id, 0) + 1

    thresholds: dict[str, Threshold] = {}
    for cells in rows:
        metric_id, name = cells[0], cells[1]
        ideal = _parse_bound(cells[2])
        passed = _parse_bound(cells[3])
        fail = _parse_bound(cells[4])

        key = _distinguish(metric_id, name, counts[metric_id] > 1)
        if key in thresholds:  # 兜底：限定词仍撞车时追加序号
            key = f"{key}#{len(thresholds) + 1}"

        thresholds[key] = Threshold(
            key=key,
            metric_id=metric_id,
            name=name,
            ideal=ideal,
            passed=passed,
            fail=fail,
            kind=_kind_of([ideal, passed, fail]),
            # 失败值写成「≥」表示数值越低越好（M10 满意度）
            lower_is_better=fail.op in (">", ">="),
        )

    if not thresholds:
        raise SchemaError(f"{md_path} 的判定阶梯表格中没有解析到任何指标")

    return thresholds


# 判定档位
IDEAL, PASS, NOT_MET, FAIL, NO_DATA = "理想", "通过", "未达标", "失败", "无数据源"


def judge(value: float | None, t: Threshold) -> str:
    """把实测值与阈值比较，得出判定阶梯档位。"""
    if value is None:
        return NO_DATA

    if t.fail.op == "=":
        is_fail = value == t.fail.value
    elif t.lower_is_better:
        is_fail = value >= t.fail.value
    else:
        is_fail = value < t.fail.value
    if is_fail:
        return FAIL

    def meets(b: Bound) -> bool:
        return value <= b.value if t.lower_is_better else value >= b.value

    if meets(t.ideal):
        return IDEAL
    if meets(t.passed):
        return PASS
    return NOT_MET


# --------------------------------------------------------------------------
# Schema 定义
# --------------------------------------------------------------------------

TRUE_TOKENS = {"true", "1", "yes", "y", "是", "有"}
FALSE_TOKENS = {"false", "0", "no", "n", "否", "无"}
LIST_SEP = ";"


@dataclass
class Column:
    name: str
    kind: str  # text | bool | int | float | enum | date | list
    required: bool = True
    choices: frozenset[str] | None = None
    lo: float | None = None
    hi: float | None = None
    note: str = ""


@dataclass
class Schema:
    columns: list[Column]
    description: str

    @property
    def names(self) -> list[str]:
        return [c.name for c in self.columns]

    def by_name(self) -> dict[str, Column]:
        return {c.name: c for c in self.columns}


M4_ANSWERS = frozenset({"very_needed", "somewhat_needed", "not_needed", "not_at_all"})
M12_ANSWERS = frozenset({"strongly_agree", "agree", "neutral", "disagree", "strongly_disagree"})
AB_VARIANTS = frozenset({"A", "B", "C"})

SCHEMAS: dict[str, Schema] = {
    "subscribers": Schema(
        description="着陆页邮件订阅（由任务 14 [A1.1] 产出）→ 供 M1",
        columns=[
            Column("email", "text"),
            Column("source_channel", "text", note="推广渠道，须与投放记录逐条对应"),
            Column("ab_variant", "enum", choices=AB_VARIANTS, note="落地页 A/B 变体 A/B/C"),
            Column("subscribed_at", "date"),
            Column("confirmed_at", "date", required=False),
            Column("unsubscribed_at", "date", required=False),
        ],
    ),
    "interviews": Schema(
        description="开发者深度访谈结构化摘要（由任务 1 [H1.1] 产出）→ 供 S1 / M4 / M5",
        columns=[
            Column("respondent_id", "text"),
            Column("skill_tags", "list", required=False),
            Column("job_search_status", "text", required=False),
            Column("pain_points", "list", required=False,
                   note=f"以 {LIST_SEP} 分隔，M5 数 ≥3 个者；留空 = 未提及痛点，计入分母不计入分子"),
            Column("needs", "list", required=False),
            Column("strong_need", "bool", note="M4 访谈口径"),
            Column("interview_date", "date"),
            Column("channel", "text", required=False),
        ],
    ),
    "companies": Schema(
        description="企业深度访谈结构化摘要（由任务 4 [H2.1] 产出）→ 供 S2 / M6–M9",
        columns=[
            Column("company_id", "text"),
            Column("agent_projects", "text", required=False),
            Column("hiring_challenge", "text", required=False),
            Column("required_skills", "list", required=False),
            Column(
                "interested_in_platform",
                "bool",
                note="M6 口径：是否愿意使用专门平台。**本字段为 A1.2 补齐**——"
                "任务原文将 M6 归给 companies.csv，但原字段集中无任何字段可承载该口径",
            ),
            Column("has_budget", "bool", note="M9"),
            Column("committed_to_post", "bool", note="M8"),
            Column("difficulty_score", "float", lo=1, hi=10, note="M7：招聘难度自评"),
            Column("interview_date", "date"),
        ],
    ),
    "survey_responses": Schema(
        description="问卷回收（由任务 16 [A1.3] 设计、任务 3 [H1.3] 投放）→ 供 S3 / M3 / M4 / M11 / M12",
        columns=[
            Column("respondent_id", "text"),
            Column("submitted_at", "date", required=False,
                   note="问卷开始即建行，提交后回填；空表示未提交，是 M3 分子判定的依据"),
            Column("source_channel", "text", required=False),
            Column("m4_answer", "enum", choices=M4_ANSWERS, required=False),
            Column("m12_answer", "enum", choices=M12_ANSWERS, required=False),
            Column("differentiation_needs", "list", required=False,
                   note=f"以 {LIST_SEP} 分隔；M11 数 ≥3 项者。问卷多选题产出"),
            Column("survey_started", "bool", note="true 表示该行计入 M3 分母"),
        ],
    ),
    "social_posts": Schema(
        description="社媒内容记录（由创始人手工记录）→ 供 M2",
        columns=[
            Column("platform", "text"),
            Column("post_url", "text"),
            Column("published_at", "date"),
            Column("impressions", "int", lo=0, note="曝光量。为 0 的帖子跳过并计入提示，不得按 0 计入均值"),
            Column("likes", "int", lo=0),
            Column("comments", "int", lo=0),
            Column("shares", "int", lo=0),
        ],
    ),
    "competitors": Schema(
        description="竞品对比（由任务 6/7 实操 + 任务 18 检索，任务 19 汇总）→ 供 M10 / D1",
        columns=[
            Column("platform", "text"),
            Column("job_types_covered", "list", required=False),
            Column("agent_job_availability", "text", required=False),
            Column("skill_tag_support", "text", required=False),
            Column("differentiation", "list", required=False,
                   note=f"以 {LIST_SEP} 分隔；D1 去重计数。无观察到的差异化点时留空，不得填推测值"),
            Column("satisfaction_score", "float", lo=1, hi=10, note="M10：用户对现有平台满意度"),
            Column("evidence_url", "text"),
        ],
    ),
}


# --------------------------------------------------------------------------
# 载入与校验
# --------------------------------------------------------------------------

Row = dict[str, Any]


def _parse_bool(raw: str, col: Column, ctx: str) -> bool:
    v = raw.strip().lower()
    if v in TRUE_TOKENS:
        return True
    if v in FALSE_TOKENS:
        return False
    raise SchemaError(
        f"{ctx}: 列 `{col.name}` 布尔值非法：{raw!r}；"
        f"允许值 {sorted(TRUE_TOKENS | FALSE_TOKENS)}"
    )


def _parse_date(raw: str, col: Column, ctx: str) -> datetime | None:
    text = raw.strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SchemaError(f"{ctx}: 列 `{col.name}` 时间格式非法：{raw!r}（须为 ISO 8601）") from exc


def load_csv(data_dir: Path, name: str) -> list[Row]:
    """读取并严格校验一份 CSV。缺列、枚举非法、数值越界一律抛 SchemaError。"""
    schema = SCHEMAS[name]
    path = data_dir / f"{name}.csv"

    if not path.exists():
        raise SchemaError(
            f"缺少必需的数据文件：{path}\n"
            f"  表头模板见 validation/schemas/templates/{name}.csv"
        )

    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []

        missing = [c for c in schema.names if c not in header]
        if missing:
            raise SchemaError(
                f"{path} 缺少必需列：{', '.join(missing)}\n"
                f"  应有表头：{','.join(schema.names)}"
            )

        rows: list[Row] = []
        for line_no, raw_row in enumerate(reader, start=2):
            ctx = f"{path.name}:{line_no}"
            row: Row = {}
            for col in schema.columns:
                raw = raw_row.get(col.name, "")
                if raw is None:
                    raw = ""
                if not raw.strip():
                    # 可选列留空是合法语义（如 submitted_at 为空 = 开始未提交，M3 的分子判定依赖此点）
                    if col.required:
                        raise SchemaError(f"{ctx}: 必需列 `{col.name}` 为空")
                    row[col.name] = None
                    continue

                if col.kind == "bool":
                    row[col.name] = _parse_bool(raw, col, ctx)
                elif col.kind == "enum":
                    v = raw.strip()
                    if v not in col.choices:
                        raise SchemaError(
                            f"{ctx}: 列 `{col.name}` 取值非法：{v!r}；"
                            f"允许值 {sorted(col.choices)}"
                        )
                    row[col.name] = v
                elif col.kind == "int":
                    try:
                        v = int(raw)
                    except ValueError as exc:
                        raise SchemaError(f"{ctx}: 列 `{col.name}` 期望整数：{raw!r}") from exc
                    lo = col.lo if col.lo is not None else -float("inf")
                    hi = col.hi if col.hi is not None else float("inf")
                    if not lo <= v <= hi:
                        raise SchemaError(
                            f"{ctx}: 列 `{col.name}` 越界：{v}，应在 {col.lo}–{col.hi} 之间"
                        )
                    row[col.name] = v
                elif col.kind == "float":
                    try:
                        v = float(raw)
                    except ValueError as exc:
                        raise SchemaError(f"{ctx}: 列 `{col.name}` 期望数值：{raw!r}") from exc
                    lo = col.lo if col.lo is not None else -float("inf")
                    hi = col.hi if col.hi is not None else float("inf")
                    if not lo <= v <= hi:
                        raise SchemaError(
                            f"{ctx}: 列 `{col.name}` 越界：{v}，应在 {col.lo}–{col.hi} 之间"
                        )
                    row[col.name] = v
                elif col.kind == "date":
                    row[col.name] = _parse_date(raw, col, ctx)
                elif col.kind == "list":
                    row[col.name] = [p.strip() for p in raw.split(LIST_SEP) if p.strip()]
                else:
                    row[col.name] = raw.strip()

            rows.append(row)

    return rows


# --------------------------------------------------------------------------
# 指标计算
# --------------------------------------------------------------------------


def _ratio(num: float, den: float) -> float | None:
    return (num / den) if den else None


def _mean(values: list[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


@dataclass
class Result:
    key: str
    value: float | None
    verdict: str
    detail: str
    threshold: Threshold | None = None
    source: str = ""
    advisory: str = ""


@dataclass
class Report:
    results: list[Result] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, key: str, value, detail: str, thresholds, source: str, advisory: str = "") -> None:
        t = thresholds.get(key)
        self.results.append(
            Result(
                key=key,
                value=value,
                verdict=judge(value, t) if t else NO_DATA,
                detail=detail,
                threshold=t,
                source=source,
                advisory=advisory,
            )
        )

    def gap(self, key: str, reason: str, expected: bool = False) -> None:
        """记录一项无数据源的指标。

        expected=True 表示该缺失是设计预期（如 D2 的验证期不评估），
        不计入「结论为暂定」的警告列表——但仍会在结论中声明。
        """
        self.results.append(Result(key=key, value=None, verdict=NO_DATA, detail=reason))
        if not expected:
            self.warnings.append(f"[{key}] 数据源缺失：{reason}")


def compute(
    data_dir: Path,
    thresholds: dict[str, Threshold],
    window_start: date | None = None,
) -> Report:
    rep = Report()
    subs = load_csv(data_dir, "subscribers")
    interviews = load_csv(data_dir, "interviews")
    companies = load_csv(data_dir, "companies")
    survey = load_csv(data_dir, "survey_responses")
    social = load_csv(data_dir, "social_posts")
    comps = load_csv(data_dir, "competitors")

    # ---- S 样本量 ----
    rep.add("S1", len(interviews), f"访谈记录 {len(interviews)} 条", thresholds, "interviews.csv")
    rep.add("S2", len(companies), f"企业访谈记录 {len(companies)} 条", thresholds, "companies.csv")
    rep.add("S3", len(survey), f"问卷记录 {len(survey)} 条", thresholds, "survey_responses.csv")

    sample_short = {
        r.key: r for r in rep.results if r.key in ("S1", "S2", "S3") and r.verdict != PASS
    }
    sample_advisory = (
        "样本量未达通过值，结果仅供参考（按判定阶梯「关于样本量的门槛语义」不判失败）"
        if sample_short
        else ""
    )

    # ---- M1 着陆页订阅 ----
    dates = [r["subscribed_at"] for r in subs if r["subscribed_at"]]
    if dates:
        start = window_start or min(dates).date()
        w1 = [r for r in subs if r["subscribed_at"] and r["subscribed_at"].date() < start + timedelta(days=7)]
        w2 = [r for r in subs if r["subscribed_at"] and r["subscribed_at"].date() < start + timedelta(days=14)]
        unsub = sum(1 for r in subs if r["unsubscribed_at"])
        common = f"窗口起点 {start}；已退订 {unsub}"
        rep.add("M1.首周", len(w1), f"首周订阅 {len(w1)} 条", thresholds, "subscribers.csv", common)
        rep.add("M1.次周累计", len(w2), f"前两周累计订阅 {len(w2)} 条", thresholds, "subscribers.csv", common)
    else:
        rep.gap("M1.首周", "subscribers.csv 无有效 subscribed_at")
        rep.gap("M1.次周累计", "subscribers.csv 无有效 subscribed_at")

    # ---- M2 社媒互动率 ----
    # 逐条计算后取算术平均；impressions = 0 的帖子无法计算，跳过并提示，不得按 0 计入
    rates: list[float] = []
    skipped = 0
    for r in social:
        if not r["impressions"]:
            skipped += 1
            continue
        eng = r["likes"] + r["comments"] + r["shares"]
        rates.append(eng / r["impressions"])
    if rates:
        detail = f"逐条互动率均值（{len(rates)} 条参与计算）"
        if skipped:
            detail += f"；跳过 {skipped} 条 impressions 为 0 的帖子"
        rep.add("M2", _mean(rates), detail, thresholds, "social_posts.csv")
    else:
        rep.gap("M2", "social_posts.csv 无 impressions > 0 的记录"
                       + (f"（{skipped} 条帖子曝光量为 0，无法计算）" if skipped else ""))

    # ---- M3 问卷完成率 ----
    started = sum(1 for r in survey if r["survey_started"])
    submitted = sum(1 for r in survey if r["submitted_at"])
    rep.add("M3", _ratio(submitted, started),
            f"提交 {submitted} / 开始 {started}", thresholds, "survey_responses.csv",
            sample_advisory)

    # ---- M4 强需求表达（问卷为主口径，访谈为交叉校验）----
    answered = [r for r in survey if r["m4_answer"]]
    very = sum(1 for r in answered if r["m4_answer"] == "very_needed")
    survey_m4 = _ratio(very, len(answered))

    if answered:
        rep.add("M4", survey_m4,
                f"问卷口径：选「非常需要」{very} / 有效作答 {len(answered)}",
                thresholds, "survey_responses.csv", sample_advisory)
        strong = sum(1 for r in interviews if r["strong_need"])
        if interviews:
            rep.notes.append(
                f"M4 交叉校验（interviews.csv）：strong_need=true {strong} / {len(interviews)}"
                f" = {_ratio(strong, len(interviews)) or 0:.1%}。判定阶梯只有一条 M4，本表采用问卷口径。"
            )
    else:
        strong = sum(1 for r in interviews if r["strong_need"])
        if interviews:
            rep.add("M4", _ratio(strong, len(interviews)),
                    f"访谈口径：strong_need=true {strong} / {len(interviews)}",
                    thresholds, "interviews.csv", sample_advisory)
            rep.notes.append("M4 采用访谈口径（问卷无有效作答）。问卷回收后须重跑并以问卷为准。")
        else:
            rep.gap("M4", "survey_responses.csv 与 interviews.csv 均无 M4 相关数据")

    # ---- M5 痛点认同度 ----
    if interviews:
        hit = sum(1 for r in interviews if len(r["pain_points"] or []) >= 3)
        rep.add("M5", _ratio(hit, len(interviews)),
                f"认同 ≥3 个痛点 {hit} / {len(interviews)}", thresholds, "interviews.csv",
                sample_advisory)
    else:
        rep.gap("M5", "interviews.csv 为空")

    # ---- M6–M9 企业侧 ----
    if companies:
        n = len(companies)
        rep.add("M6", _ratio(sum(1 for r in companies if r["interested_in_platform"]), n),
                f"愿意使用专门平台 {sum(1 for r in companies if r['interested_in_platform'])} / {n}",
                thresholds, "companies.csv", sample_advisory)
        diff = [r["difficulty_score"] for r in companies if r["difficulty_score"] is not None]
        rep.add("M7", _mean(diff), f"招聘难度均值（{len(diff)} 家有评分）", thresholds,
                "companies.csv", sample_advisory)
        committed = sum(1 for r in companies if r["committed_to_post"])
        rep.add("M8", _ratio(committed, n), f"承诺发布职位 {committed} / {n}", thresholds,
                "companies.csv", sample_advisory)
        rep.add("M9", _ratio(sum(1 for r in companies if r["has_budget"]), n),
                f"有预算 {sum(1 for r in companies if r['has_budget'])} / {n}", thresholds,
                "companies.csv", sample_advisory)
    else:
        for k, why in [("M6", "companies.csv 为空"), ("M7", "companies.csv 为空"),
                       ("M8", "companies.csv 为空"), ("M9", "companies.csv 为空")]:
            rep.gap(k, why)

    # ---- M10 竞品满意度 ----
    scores = [r["satisfaction_score"] for r in comps if r["satisfaction_score"] is not None]
    if scores:
        rep.add("M10", _mean(scores), f"满意度均值（{len(scores)} 个平台，越低越好）",
                thresholds, "competitors.csv")
    else:
        rep.gap("M10", "competitors.csv 无有效 satisfaction_score")

    # ---- M11 差异化需求 ----
    # 2026-10-11 裁定：数据源由 competitors.csv（平台级）改为问卷（用户级）——
    # M11 的统计单元是「用户」，competitors.csv 一行一平台，两者不匹配。
    answered11 = [r for r in survey if r["differentiation_needs"]]
    if answered11:
        hit11 = sum(1 for r in answered11 if len(r["differentiation_needs"]) >= 3)
        rep.add("M11", _ratio(hit11, len(answered11)),
                f"提出 ≥3 项差异化需求 {hit11} / 有效作答 {len(answered11)}",
                thresholds, "survey_responses.csv", sample_advisory)
    else:
        rep.gap("M11", "survey_responses.csv 无 differentiation_needs。"
                       "该列由任务 16 [A1.3] 的问卷题项产出——漏做此题项将导致 M11 永久无数据源")

    # ---- M12 价值认同度 ----
    m12 = [r for r in survey if r["m12_answer"]]
    if m12:
        agree = sum(1 for r in m12 if r["m12_answer"] in ("agree", "strongly_agree"))
        rep.add("M12", _ratio(agree, len(m12)),
                f"认同（agree + strongly_agree）{agree} / {len(m12)}", thresholds,
                "survey_responses.csv", sample_advisory)
    else:
        rep.gap("M12", "survey_responses.csv 无有效 m12_answer")

    # ---- D1 差异化功能点 ----
    points: set[str] = set()
    for r in comps:
        for p in r["differentiation"] or []:
            if p:
                points.add(p)
    if points:
        rep.add("D1", float(len(points)), f"去重后差异化功能点 {len(points)} 个",
                thresholds, "competitors.csv")
        rep.notes.append(
            f"D1 样本：{'；'.join(sorted(points))}"
        )
    else:
        rep.gap("D1", "competitors.csv 的 differentiation 列无数据")

    # ---- D2 成功职位匹配 ----
    # 2026-10-11 裁定：D2 判定阶段为平台期，验证期不评估——这不是异常，是预期行为。
    # 明确不用 H2.2 的 seeding 就绪度作代理：那是意向证据，冒充终端证据会使
    # risk-analysis.md 风险 4 的防护逻辑失效。
    rep.gap("D2", "D2 判定阶段为平台期，验证窗口内平台不存在（requirements.md「窗口区分」），"
                   "验证期按裁定不评估。属预期行为，非异常。"
                   "H5.1 的结论须标注「未含 D2 终端证据，结论建立在意向证据之上」",
            expected=True)

    return rep


# --------------------------------------------------------------------------
# 结论
# --------------------------------------------------------------------------


def conclude(rep: Report) -> tuple[str, list[str]]:
    notes: list[str] = []
    evaluated = [r for r in rep.results if r.verdict != NO_DATA]
    unevaluated = [r for r in rep.results if r.verdict == NO_DATA]

    # D2 在验证期不评估是设计预期（判定阶段为平台期），不是数据缺口，
    # 故不计入「暂定」警告，但其缺席必须始终在结论中声明。
    d2_result = next((r for r in rep.results if r.key == "D2"), None)
    d2_evaluated = d2_result is not None and d2_result.verdict != NO_DATA
    gaps = [r for r in unevaluated if r.key != "D2"]

    fails = [r for r in evaluated if r.verdict == FAIL]
    not_met = [r for r in evaluated if r.verdict == NOT_MET]

    # D2 声明必须在任何提前返回之前发出——命中失败值时恰恰最需要说明
    # 本次判定缺乏终端证据这一前提
    if not d2_evaluated:
        notes.append(
            "本次判定未含 D2 终端证据（D2 判定阶段为平台期，验证期按裁定不评估），"
            "结论建立在意向证据之上"
        )
    if gaps:
        notes.append(
            f"有 {len(gaps)} 项指标因数据源缺失未评估："
            f"{', '.join(r.key for r in gaps)}——结论为暂定，补齐数据后须重跑"
        )

    if fails:
        return "验证失败（命中失败值）", notes

    if not evaluated:
        return "无法判定（所有指标均无数据源）", notes

    if not not_met:
        conclusion = "强力验证" if all(r.verdict == IDEAL for r in evaluated) else "验证通过"
        if not d2_evaluated:
            notes.append("结论为通过，但缺 D2 终端证据：开发期上线后须优先促成首个匹配")
        return conclusion, notes

    # 未达标
    if d2_evaluated and d2_result.value is not None and d2_result.value >= 1:
        notes.append("D2 ≥ 1：终端证据成立，可单独支撑「继续」决策")
        return "未达标（但有终端证据，继续）", notes

    # 风险 4：验证期按「D2 缺席」触发，平台期按「D2 = 0」触发
    m_not_met = [r for r in not_met if r.key.startswith("M")]
    if len(m_not_met) >= 3:
        state = f"D2 = {d2_result.value:g}" if d2_evaluated else "D2 缺席"
        notes.append(
            f"{state} 且 M1–M12 中有 {len(m_not_met)} 项未达标"
            f"（{', '.join(r.key for r in m_not_met)}）→ 触发 risk-analysis.md 风险 4：双边市场冷启动。"
            f"缓解路径见该文档的 seeding / 单边突破 / 人工撮合三条"
        )
    notes.append("按「决策点」调整验证策略后继续，最长延长 1 周；不追加功能开发")
    return "未达标（信号不足，调整策略后继续）", notes


# --------------------------------------------------------------------------
# 输出
# --------------------------------------------------------------------------

MARK = {IDEAL: "★", PASS: "✓", NOT_MET: "!", FAIL: "✗", NO_DATA: "—"}


def format_value(r: Result) -> str:
    if r.value is None:
        return "—"
    t = r.threshold
    if t and t.kind == "ratio":
        return f"{r.value:.1%}"
    if t and t.kind == "score":
        return f"{r.value:.2f}/10"
    return f"{r.value:g}"


def render(rep: Report) -> str:
    lines: list[str] = []
    lines.append("=" * 100)
    lines.append("AgentJobs 验证指标打分表")
    lines.append("阈值来源：validation-metrics.md「判定阶梯」（运行时解析，非硬编码）")
    lines.append("=" * 100)
    header = f"{'编号':<14}{'实测值':>12}  {'判定':<6}{'指标':<26}明细"
    lines.append(header)
    lines.append("-" * 100)

    for r in rep.results:
        t = r.threshold
        name = t.name if t else "—"
        thr = f"（{t.raw}）" if t else ""
        lines.append(f"{r.key:<14}{format_value(r):>12}  {MARK[r.verdict]} {r.verdict:<4}  {name}{thr}")
        lines.append(f"{'':<14}{'':>12}    └─ {r.detail}")
        if r.advisory:
            lines.append(f"{'':<14}{'':>12}    ⚠ {r.advisory}")

    lines.append("-" * 100)
    for n in rep.notes:
        lines.append(f"ℹ {n}")
    for w in rep.warnings:
        lines.append(f"⚠ {w}")

    conclusion, extra = conclude(rep)
    lines.append("")
    lines.append(f"【判定结论】{conclusion}")
    for e in extra:
        lines.append(f"  {e}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AgentJobs 验证指标计算器")
    ap.add_argument("--data-dir", type=Path, required=True, help="5 份 CSV 所在目录")
    ap.add_argument("--thresholds", type=Path, default=DEFAULT_THRESHOLDS, help="validation-metrics.md 路径")
    ap.add_argument("--window-start", type=date.fromisoformat, help="验证窗口起点 YYYY-MM-DD（默认取最早订阅日）")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = ap.parse_args(argv)

    try:
        thresholds = load_thresholds(args.thresholds)
        rep = compute(args.data_dir, thresholds, args.window_start)
    except SchemaError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    conclusion, extra = conclude(rep)

    if args.json:
        print(json.dumps({
            "conclusion": conclusion,
            "conclusionNotes": extra + rep.notes + rep.warnings,
            "metrics": [
                {
                    "id": r.key,
                    "name": r.threshold.name if r.threshold else None,
                    "value": r.value,
                    "verdict": r.verdict,
                    "detail": r.detail,
                    "source": r.source,
                    "advisory": r.advisory or None,
                }
                for r in rep.results
            ],
        }, ensure_ascii=False, indent=2))
    else:
        print(render(rep))

    return 1 if conclusion.startswith("验证失败") else 0


if __name__ == "__main__":
    raise SystemExit(main())