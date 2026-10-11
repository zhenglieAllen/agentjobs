"""subscribers 表与按变体的访问计数 —— 任务 14 [A1.1]。

表结构对齐 `design.md` 第 151 行的 `subscribers` 定义；导出的 CSV 列名与
`validation/schemas/subscribers.csv` 严格一致，二者是硬契约：
列名一旦不一致，M1 就无法由 `validation/compute_metrics.py` 聚合。
"""

from __future__ import annotations

import csv
import io
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

VARIANTS = ("A", "B", "C")

# 导出契约：顺序与列名均不得改动
EXPORT_COLUMNS = (
    "email",
    "source_channel",
    "ab_variant",
    "subscribed_at",
    "confirmed_at",
    "unsubscribed_at",
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+\.[^@\s]+$")

SCHEMA = """
CREATE TABLE IF NOT EXISTS subscribers (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  email           TEXT NOT NULL UNIQUE COLLATE NOCASE,
  source_channel  TEXT NOT NULL,
  ab_variant      TEXT NOT NULL CHECK (ab_variant IN ('A','B','C')),
  subscribed_at   TEXT NOT NULL,
  confirmed_at    TEXT,
  unsubscribed_at TEXT
);

CREATE TABLE IF NOT EXISTS page_views (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  ab_variant TEXT NOT NULL CHECK (ab_variant IN ('A','B','C')),
  viewed_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_subscribers_variant ON subscribers(ab_variant);
CREATE INDEX IF NOT EXISTS idx_page_views_variant  ON page_views(ab_variant);
"""


class ValidationError(ValueError):
    """输入不合法。调用方须返回 400 而不是静默接受。"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def validate_email(raw: str) -> str:
    email = (raw or "").strip()
    if not email:
        raise ValidationError("邮箱不能为空")
    if len(email) > 254:
        raise ValidationError("邮箱过长")
    if not EMAIL_RE.match(email):
        raise ValidationError("邮箱格式无效")
    return email


def validate_channel(raw: str) -> str:
    channel = (raw or "").strip()
    if not channel:
        raise ValidationError("source_channel 不能为空")
    if len(channel) > 100:
        raise ValidationError("source_channel 过长")
    return channel


def validate_variant(raw: str, active: tuple[str, ...]) -> str:
    variant = (raw or "").strip().upper()
    if variant not in VARIANTS:
        raise ValidationError(f"ab_variant 必须是 A/B/C，收到 {raw!r}")
    # 降级后仍可写入历史变体的订阅（此前活跃过的变体不应丢失归因）
    return variant


def insert_subscriber(
    conn: sqlite3.Connection,
    *,
    email: str,
    source_channel: str,
    ab_variant: str,
) -> tuple[bool, str]:
    """插入一条订阅。返回 (是否新增, 说明)。

    同一邮箱重复提交不报错，返回 (False, "already_subscribed")——M1 统计的是
    唯一订阅人数，重复提交不应抬高计数。
    """
    email = validate_email(email)
    source_channel = validate_channel(source_channel)
    ab_variant = validate_variant(ab_variant, VARIANTS)

    try:
        conn.execute(
            "INSERT INTO subscribers (email, source_channel, ab_variant, subscribed_at)"
            " VALUES (?, ?, ?, ?)",
            (email, source_channel, ab_variant, now_iso()),
        )
        conn.commit()
        return True, "subscribed"
    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "already_subscribed"


def record_view(conn: sqlite3.Connection, ab_variant: str) -> None:
    conn.execute(
        "INSERT INTO page_views (ab_variant, viewed_at) VALUES (?, ?)",
        (validate_variant(ab_variant, VARIANTS), now_iso()),
    )
    conn.commit()


def view_counts(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT ab_variant, COUNT(*) AS n FROM page_views GROUP BY ab_variant"
    ).fetchall()
    return {r["ab_variant"]: r["n"] for r in rows}


def subscriber_counts(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT ab_variant, COUNT(*) AS n FROM subscribers GROUP BY ab_variant"
    ).fetchall()
    return {r["ab_variant"]: r["n"] for r in rows}


def total_subscribers(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) AS n FROM subscribers").fetchone()["n"]


def degraded_variants(
    counts: dict[str, int], active: tuple[str, ...], threshold: int
) -> list[str]:
    """样本量不足（访问数 < threshold）的活跃变体——应考虑降级停止分流。"""
    return [v for v in active if counts.get(v, 0) < threshold]


def export_subscribers_csv(conn: sqlite3.Connection) -> str:
    """导出为 CSV。列名与 validation/schemas/subscribers.csv 完全一致。"""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(EXPORT_COLUMNS)
    for row in conn.execute(
        "SELECT email, source_channel, ab_variant, subscribed_at, confirmed_at,"
        " unsubscribed_at FROM subscribers ORDER BY subscribed_at, id"
    ):
        writer.writerow([row[c] or "" for c in EXPORT_COLUMNS])
    return buf.getvalue()