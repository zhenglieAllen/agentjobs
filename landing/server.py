#!/usr/bin/env python3
"""AgentJobs 着陆页 —— 任务 14 [A1.1]。

零依赖：Python 3 标准库（http.server + sqlite3）。不引入用户系统、不实现
落地页以外的任何功能（任务明确禁止）。

关键设计（对应任务 Requirements）：

* **服务端分流**：变体在服务端决定并渲染进 HTML，不依赖客户端 JS，也不依赖
  构建期。SEO 爬虫与 CDN 缓存拿到的是与真实访客一致的变体，不会出现变体错乱。
* **粘性归因**：变体写入 `aj_var` cookie（HttpOnly），同一访客多次访问命中同一
  变体——否则 M1 的按变体归因不可信。
* **降级分流**：`--active A,B` 或编辑 variants.json 的 `active` 数组即可只跑两变体。
* **自建 subscribers 表**：不依赖第三方 ESP，因为 ESP 无法按变体归因，
  `risk-analysis.md` 实验 1 的结论将不可用。
* **管理端令牌**：`/api/subscribers/export` 与 `/api/stats` 会暴露全量邮箱，
  必须持令牌访问。令牌取自环境变量 `AGENTJOBS_ADMIN_TOKEN`，未设置时启动时随机
  生成并打印。

运行::

    python3 landing/server.py                      # 默认 http://127.0.0.1:8000
    python3 landing/server.py --port 9000
    python3 landing/server.py --active A,B         # 降级为两变体
    python3 landing/server.py --db /tmp/test.db    # 指定数据库
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import secrets
import sys
import threading
import time
from collections import defaultdict, deque
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db  # noqa: E402

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
VARIANT_COOKIE = "aj_var"
COOKIE_MAX_AGE = 60 * 60 * 24 * 90  # 90 天，覆盖整个 30 天验证窗口

# 每个 IP 每小时最多提交的订阅数（防刷）
RATE_LIMIT_PER_HOUR = 10


def load_variants(path: Path | None = None) -> tuple[dict, tuple[str, ...], int]:
    cfg = json.loads((path or ROOT / "variants.json").read_text(encoding="utf-8"))
    variants = cfg["variants"]
    active = tuple(v for v in cfg.get("active", []) if v in variants)
    if not active:
        raise ValueError("variants.json 的 active 为空或全部无效")
    for v in active:
        if v not in variants:
            raise ValueError(f"active 中的 {v} 在 variants 中没有定义")
    return cfg, active, int(cfg.get("min_visits_before_degrade", 100))


class Config:
    def __init__(self, variants_path: Path | None, active_override: str | None):
        self.cfg, active, self.min_visits = load_variants(variants_path)
        if active_override:
            picked = tuple(v.strip().upper() for v in active_override.split(",") if v.strip())
            bad = [v for v in picked if v not in self.cfg["variants"]]
            if bad:
                raise ValueError(f"--active 含未定义变体：{bad}")
            if not picked:
                raise ValueError("--active 为空")
            active = picked
        self.active = active
        self.variants = self.cfg["variants"]
        self.admin_token = os.environ.get("AGENTJOBS_ADMIN_TOKEN") or secrets.token_urlsafe(24)

    def pick(self, cookie_value: str | None) -> str:
        """决定本次访问的变体：cookie 有效则沿用，否则在活跃变体中随机。"""
        if cookie_value in self.active:
            return cookie_value
        return secrets.choice(self.active)


class RateLimiter:
    def __init__(self, limit: int, window: int = 3600):
        self.limit = limit
        self.window = window
        self.hits: dict[str, deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self.lock:
            q = self.hits[key]
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True


def escape(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def render(template: str, variant: dict) -> str:
    """服务端渲染：把变体内容注入 HTML 模板。"""
    points = "\n".join(
        f'          <li>{escape(p)}</li>' for p in variant["points"]
    )
    return (
        template.replace("{{HEADLINE}}", escape(variant["headline"]))
        .replace("{{SUBHEADLINE}}", escape(variant["subheadline"]))
        .replace("{{POINTS}}", points)
        .replace("{{CTA}}", escape(variant["cta"]))
        .replace("{{VARIANT_ID}}", variant["id"])
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "AgentJobsLanding/1.0"
    config: Config
    db_path: Path
    limiter: RateLimiter

    # ---------- 基础响应 ----------

    def _send(self, status: HTTPStatus, body: bytes, content_type: str,
              extra_headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: HTTPStatus, payload: dict) -> None:
        self._send(
            status,
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _text(self, status: HTTPStatus, msg: str) -> None:
        self._send(status, msg.encode("utf-8"), "text/plain; charset=utf-8")

    def _authorized(self) -> bool:
        """管理端令牌校验。支持 X-Admin-Token 头或 ?token= 查询参数。"""
        supplied = self.headers.get("X-Admin-Token")
        if not supplied:
            supplied = parse_qs(urlparse(self.path).query).get("token", [""])[0]
        return bool(supplied) and hmac.compare_digest(supplied, self.config.admin_token)

    def _require_admin(self) -> bool:
        if self._authorized():
            return True
        self._json(HTTPStatus.UNAUTHORIZED, {"error": "需要管理令牌"})
        return False

    # ---------- 路由 ----------

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            self._serve_landing()
        elif path == "/api/stats":
            self._serve_stats()
        elif path == "/api/subscribers/export":
            self._serve_export()
        elif path == "/privacy":
            self._serve_static("privacy.html", "text/html; charset=utf-8")
        elif path in ("/styles.css", "/app.js"):
            ct = "text/css; charset=utf-8" if path.endswith(".css") else "application/javascript"
            self._serve_static(path.lstrip("/"), ct)
        elif path == "/healthz":
            self._json(HTTPStatus.OK, {"ok": True})
        else:
            self._text(HTTPStatus.NOT_FOUND, "404")

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/subscribers":
            self._subscribe()
        else:
            self._text(HTTPStatus.NOT_FOUND, "404")

    # ---------- 处理器 ----------

    def _serve_static(self, name: str, content_type: str) -> None:
        f = STATIC / name
        if not f.is_file():
            self._text(HTTPStatus.NOT_FOUND, "404")
            return
        self._send(HTTPStatus.OK, f.read_bytes(), content_type,
                   {"Cache-Control": "no-cache"})

    def _serve_landing(self) -> None:
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        existing = cookie[VARIANT_COOKIE].value if VARIANT_COOKIE in cookie else None
        variant_id = self.config.pick(existing)
        variant = self.config.variants[variant_id]

        conn = db.connect(self.db_path)
        try:
            db.record_view(conn, variant_id)
        finally:
            conn.close()

        html = render((STATIC / "index.html").read_text(encoding="utf-8"), variant)
        # 变体随 HTML 一起下发并缓存，保证同一访客不会因 CDN 缓存串变体
        self._send(
            HTTPStatus.OK,
            html.encode("utf-8"),
            "text/html; charset=utf-8",
            {
                "Set-Cookie": (
                    f"{VARIANT_COOKIE}={variant_id}; Path=/; Max-Age={COOKIE_MAX_AGE};"
                    f" HttpOnly; SameSite=Lax"
                ),
                "Cache-Control": "private, no-cache",
                "Vary": "Cookie",
            },
        )

    def _serve_export(self) -> None:
        if not self._require_admin():
            return
        conn = db.connect(self.db_path)
        try:
            csv_text = db.export_subscribers_csv(conn)
        finally:
            conn.close()
        self._send(
            HTTPStatus.OK,
            csv_text.encode("utf-8-sig"),  # BOM：让 Excel 正确识别 UTF-8
            "text/csv; charset=utf-8",
            {"Content-Disposition": 'attachment; filename="subscribers.csv"'},
        )

    def _serve_stats(self) -> None:
        if not self._require_admin():
            return
        conn = db.connect(self.db_path)
        try:
            views = db.view_counts(conn)
            subs = db.subscriber_counts(conn)
            total = db.total_subscribers(conn)
            weak = db.degraded_variants(views, self.config.active, self.config.min_visits)
        finally:
            conn.close()

        payload = {
            "active": list(self.config.active),
            "variants": {
                v: {
                    "angle": self.config.variants[v].get("angle"),
                    "visits": views.get(v, 0),
                    "subscribers": subs.get(v, 0),
                }
                for v in self.config.variants
            },
            "m1_total_subscribers": total,
            "min_visits_before_degrade": self.config.min_visits,
            "under_sampled": weak,
            "degrade_suggestion": (
                f"变体 {', '.join(weak)} 访问数不足 {self.config.min_visits}，"
                f"建议用 --active 降级分流"
                if weak
                else None
            ),
        }
        self._json(HTTPStatus.OK, payload)

    def _subscribe(self) -> None:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > 8 * 1024:
            self._json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "请求体过大"})
            return
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "请求体不是合法 JSON"})
            return
        if not isinstance(payload, dict):
            self._json(HTTPStatus.BAD_REQUEST, {"error": "请求体必须是 JSON 对象"})
            return

        # 蜜罐：真实用户看不到该字段，填了就是机器人。静默接受但不落库，
        # 不给机器人反馈。
        if (payload.get("company") or "").strip():
            self._json(HTTPStatus.OK, {"ok": True, "variant": payload.get("ab_variant", "")})
            return

        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        if not self.limiter.allow(ip):
            self._json(HTTPStatus.TOO_MANY_REQUESTS, {"error": "提交过于频繁，请稍后再试"})
            return

        conn = db.connect(self.db_path)
        try:
            created, reason = db.insert_subscriber(
                conn,
                email=payload.get("email", ""),
                source_channel=payload.get("source_channel", ""),
                ab_variant=payload.get("ab_variant", ""),
            )
        except db.ValidationError as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return
        finally:
            conn.close()

        self._json(HTTPStatus.CREATED if created else HTTPStatus.OK,
                   {"ok": True, "created": created, "message": reason})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AgentJobs 着陆页（任务 14 / A1.1）")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--db", type=Path, default=ROOT / "landing.db")
    ap.add_argument("--variants", type=Path, default=None, help="variants.json 路径")
    ap.add_argument("--active", default=None, help="覆盖分流变体，如 A,B（降级分流用）")
    ap.add_argument("--print-token", action="store_true", help="启动后打印管理令牌")
    args = ap.parse_args(argv)

    try:
        Handler.config = Config(args.variants, args.active)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 2

    Handler.db_path = args.db
    Handler.limiter = RateLimiter(RATE_LIMIT_PER_HOUR)
    args.db.parent.mkdir(parents=True, exist_ok=True)
    conn = db.connect(args.db)
    db.init_db(conn)
    conn.close()

    # 管理令牌只在此处输出，且 stdout 重定向到文件时会被缓冲——
    # 必须显式 flush，否则用户拿不到访问 /api/* 所需的令牌。
    for line in (
        f"活跃变体：{', '.join(Handler.config.active)}",
        f"数据库：{args.db}",
        f"管理端令牌：{Handler.config.admin_token}",
        f"  -> 导出 CSV：curl -H 'X-Admin-Token: <token>' http://{args.host}:{args.port}/api/subscribers/export",
        f"  -> M1 计数：  curl -H 'X-Admin-Token: <token>' http://{args.host}:{args.port}/api/stats",
        f"\n着陆页：http://{args.host}:{args.port}/",
    ):
        print(line, flush=True)

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())