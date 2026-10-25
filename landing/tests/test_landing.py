"""着陆页测试 —— 任务 14 [A1.1]。

运行::

    python3 -m unittest discover -s landing/tests -v
"""

import csv
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import db  # noqa: E402
import server  # noqa: E402


class TestDb(unittest.TestCase):
    """subscribers 表与导出契约。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self.tmp.name) / "t.db")
        db.init_db(self.conn)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_insert_and_dedupe(self):
        ok1, r1 = db.insert_subscriber(self.conn, email="a@x.com",
                                      source_channel="reddit", ab_variant="A")
        ok2, r2 = db.insert_subscriber(self.conn, email="A@X.com",
                                      source_channel="github", ab_variant="B")
        self.assertTrue(ok1)
        self.assertEqual(r1, "subscribed")
        self.assertFalse(ok2, "同一邮箱重复提交不应抬高 M1 计数")
        self.assertEqual(r2, "already_subscribed")
        self.assertEqual(db.total_subscribers(self.conn), 1)

    def test_invalid_inputs_rejected(self):
        for kwargs, frag in [
            (dict(email="", source_channel="r", ab_variant="A"), "邮箱"),
            (dict(email="notanemail", source_channel="r", ab_variant="A"), "格式"),
            (dict(email="a@x.com", source_channel="", ab_variant="A"), "source_channel"),
            (dict(email="a@x.com", source_channel="r", ab_variant="Z"), "ab_variant"),
        ]:
            with self.assertRaises(db.ValidationError) as ctx:
                db.insert_subscriber(self.conn, **kwargs)
            self.assertIn(frag, str(ctx.exception))

    def test_export_matches_validation_schema(self):
        """导出列名与顺序必须与 validation/schemas/subscribers.csv 完全一致。

        这是跨模块硬契约：列名一旦不一致，M1 就无法由 compute_metrics.py 聚合。
        """
        db.insert_subscriber(self.conn, email="a@x.com",
                             source_channel="reddit", ab_variant="A")
        text = db.export_subscribers_csv(self.conn)
        header = text.splitlines()[0].split(",")
        self.assertEqual(header, list(db.EXPORT_COLUMNS))

        template = (ROOT.parent / "validation" / "schemas" / "templates"
                    / "subscribers.csv").read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(
            ",".join(header),
            template.strip(),
            "导出的表头必须与 validation 的模板逐字相同",
        )

    def test_export_roundtrips_through_validation_loader(self):
        """导出的 CSV 必须能被 validation/compute_metrics.py 直接加载。"""
        for i in range(3):
            db.insert_subscriber(self.conn, email=f"u{i}@x.com",
                                 source_channel="reddit", ab_variant="ABC"[i])
        data_dir = Path(self.tmp.name) / "data"
        data_dir.mkdir()
        (data_dir / "subscribers.csv").write_text(
            db.export_subscribers_csv(self.conn), encoding="utf-8"
        )

        sys.path.insert(0, str(ROOT.parent / "validation"))
        import compute_metrics as cm

        rows = cm.load_csv(data_dir, "subscribers")
        self.assertEqual(len(rows), 3)
        self.assertEqual({r["ab_variant"] for r in rows}, {"A", "B", "C"})

    def test_downloaded_csv_with_bom_still_loads(self):
        """实际下载到的文件带 UTF-8 BOM（为 Excel 兼容）。

        若 compute_metrics 忘了剥 BOM，首列名会变成 '﻿email'，
        报「缺少必需列」——这条路径必须单独覆盖。
        """
        db.insert_subscriber(self.conn, email="bom@x.com",
                             source_channel="reddit", ab_variant="A")
        data_dir = Path(self.tmp.name) / "data2"
        data_dir.mkdir()
        (data_dir / "subscribers.csv").write_bytes(
            db.export_subscribers_csv(self.conn).encode("utf-8-sig")
        )

        sys.path.insert(0, str(ROOT.parent / "validation"))
        import compute_metrics as cm

        rows = cm.load_csv(data_dir, "subscribers")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["email"], "bom@x.com")

    def test_degrade_detection(self):
        db.record_view(self.conn, "A")
        db.record_view(self.conn, "B")
        counts = db.view_counts(self.conn)
        self.assertEqual(counts, {"A": 1, "B": 1})
        weak = db.degraded_variants(counts, ("A", "B", "C"), threshold=100)
        self.assertEqual(weak, ["A", "B", "C"], "三者样本都不足时应全部提示降级")


class TestVariantAssignment(unittest.TestCase):
    """服务端分流与降级。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _config(self, active=None):
        return server.Config(None, active)

    def test_random_split_covers_all_variants(self):
        cfg = self._config()
        self.assertEqual(cfg.active, ("A", "B", "C"))
        picks = {cfg.pick(None) for _ in range(300)}
        self.assertEqual(picks, {"A", "B", "C"}, "1:1:1 分流应覆盖全部变体")

    def test_cookie_is_sticky(self):
        """同一访客必须始终命中同一变体，否则按变体归因不可信。"""
        cfg = self._config()
        for _ in range(20):
            self.assertEqual(cfg.pick("B"), "B")

    def test_degrade_to_two_variants(self):
        cfg = self._config("A,B")
        self.assertEqual(cfg.active, ("A", "B"))
        self.assertEqual({cfg.pick(None) for _ in range(200)}, {"A", "B"})

    def test_degraded_variant_cookie_is_reassigned(self):
        """降级后带着 C cookie 的访客须被重新分配，而不是继续看 C。"""
        cfg = self._config("A,B")
        self.assertIn(cfg.pick("C"), ("A", "B"))

    def test_unknown_variant_flag_raises(self):
        with self.assertRaises(ValueError):
            self._config("A,X")

    def test_render_escapes_and_injects(self):
        cfg = self._config()
        html = server.render("<h1>{{HEADLINE}}</h1>{{POINTS}}", cfg.variants["B"])
        self.assertIn("Stop explaining", html)
        self.assertNotIn("{{", html)


class TestHttp(unittest.TestCase):
    """端到端 HTTP 行为。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.tmp.name) / "t.db"
        conn = db.connect(cls.db_path)
        db.init_db(conn)
        conn.close()

        server.Handler.config = server.Config(None, None)
        server.Handler.db_path = cls.db_path
        server.Handler.limiter = server.RateLimiter(1000)
        cls.token = server.Handler.config.admin_token

        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.tmp.cleanup()

    def _req(self, method, path, body=None, headers=None, token=None):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        h = dict(headers or {})
        if token:
            h["X-Admin-Token"] = token
        if body is not None:
            h.setdefault("Content-Type", "application/json")
        conn.request(method, path, json.dumps(body).encode() if body is not None else None, h)
        r = conn.getresponse()
        data = r.read()
        status = r.status
        hdrs = dict(r.getheaders())
        conn.close()
        return status, data, hdrs

    def test_landing_sets_variant_cookie(self):
        status, body, hdrs = self._req("GET", "/")
        self.assertEqual(status, 200)
        cookie = hdrs.get("Set-Cookie", "")
        self.assertIn("aj_var=", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("Vary", hdrs)

    def test_landing_renders_server_side(self):
        """变体必须在服务端渲染进 HTML，不能依赖客户端 JS 决定。"""
        _, body, _ = self._req("GET", "/")
        html = body.decode()
        self.assertNotIn("{{", html, "模板占位符未被替换")
        self.assertIn("aj-variant", html)

    def test_subscribe_requires_valid_payload(self):
        for payload, status in [
            ({}, 400),
            ({"email": "bad", "source_channel": "r", "ab_variant": "A"}, 400),
            ({"email": "a@x.com", "source_channel": "", "ab_variant": "A"}, 400),
            ({"email": "a@x.com", "source_channel": "r", "ab_variant": "Z"}, 400),
        ]:
            status, _, _ = self._req("POST", "/api/subscribers", payload)
            self.assertEqual(status, status, msg=payload)

    def test_subscribe_success(self):
        status, data, _ = self._req("POST", "/api/subscribers", {
            "email": "http-ok@x.com", "source_channel": "reddit", "ab_variant": "A"})
        self.assertEqual(status, 201)
        self.assertTrue(json.loads(data)["created"])

    def test_honeypot_silently_accepted_but_not_stored(self):
        status, data, _ = self._req("POST", "/api/subscribers", {
            "email": "bot@x.com", "source_channel": "spam", "ab_variant": "A",
            "company": "Acme"})
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(data)["ok"], "不给机器人反馈")
        status, data, _ = self._req("GET", "/api/subscribers/export", token=self.token)
        self.assertNotIn(b"bot@x.com", data, "蜜罐提交不得落库")

    def test_export_requires_token(self):
        status, _, _ = self._req("GET", "/api/subscribers/export")
        self.assertEqual(status, 401, "导出含全量邮箱，必须鉴权")
        status, _, _ = self._req("GET", "/api/subscribers/export", token="wrong")
        self.assertEqual(status, 401)

    def test_export_with_token(self):
        status, data, hdrs = self._req("GET", "/api/subscribers/export", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("attachment", hdrs.get("Content-Disposition", ""))
        rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
        self.assertEqual(rows[0], list(db.EXPORT_COLUMNS))

    def test_stats_requires_token_and_reports_per_variant(self):
        status, _, _ = self._req("GET", "/api/stats")
        self.assertEqual(status, 401)
        status, data, _ = self._req("GET", "/api/stats", token=self.token)
        self.assertEqual(status, 200)
        payload = json.loads(data)
        self.assertEqual(payload["active"], ["A", "B", "C"])
        self.assertIn("A", payload["variants"])
        self.assertIn("visits", payload["variants"]["A"])
        self.assertIn("m1_total_subscribers", payload)

    def test_privacy_page_states_cookie_use(self):
        status, body, _ = self._req("GET", "/privacy")
        self.assertEqual(status, 200)
        text = body.decode()
        self.assertIn("aj_var", text)
        self.assertIn("A/B", text)

    def test_unknown_path_404(self):
        status, _, _ = self._req("GET", "/nope")
        self.assertEqual(status, 404)


class TestProductionConfig(unittest.TestCase):
    """生产部署配置 —— 见 landing/DEPLOY.md。

    这些项配错时服务**看起来一切正常**但指标会失效（cookie 无 Secure、
    数据写到临时盘、变体归因丢失），因此必须有测试钉住。
    """

    def test_bind_defaults_to_localhost(self):
        host, port, db = server.resolve_bind({})
        self.assertEqual(host, "127.0.0.1")
        self.assertEqual(port, 8000)
        self.assertTrue(db.name.endswith(".db"))

    def test_bind_reads_container_env(self):
        host, port, db = server.resolve_bind({
            "HOST": "0.0.0.0",
            "PORT": "8080",
            "DB_PATH": "/data/landing.db",
        })
        self.assertEqual(host, "0.0.0.0")
        self.assertEqual(port, 8080)
        self.assertEqual(str(db), "/data/landing.db")

    def test_bind_ignores_non_numeric_port(self):
        _, port, _ = server.resolve_bind({"PORT": "not-a-port"})
        self.assertEqual(port, 8000, "非法 PORT 应回退默认而非崩溃")

    def test_secure_cookie_flag_reads_env(self):
        with mock.patch.dict(os.environ, {"AGENTJOBS_SECURE_COOKIES": "1"}):
            self.assertTrue(server.Config(None, None).secure_cookies)
        with mock.patch.dict(os.environ, {"AGENTJOBS_SECURE_COOKIES": "true"}):
            self.assertTrue(server.Config(None, None).secure_cookies)
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(server.Config(None, None).secure_cookies)

    def test_admin_token_comes_from_env(self):
        with mock.patch.dict(os.environ, {"AGENTJOBS_ADMIN_TOKEN": "fixed-token"}):
            self.assertEqual(server.Config(None, None).admin_token, "fixed-token")


class TestSecurityHeaders(unittest.TestCase):
    """生产环境的安全响应头。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.tmp.name) / "t.db"
        conn = db.connect(cls.db_path)
        db.init_db(conn)
        conn.close()

        server.Handler.config = server.Config(None, None, secure_cookies=True)
        server.Handler.db_path = cls.db_path
        server.Handler.limiter = server.RateLimiter(1000)

        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.tmp.cleanup()

    def _get(self, path):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", path)
        r = conn.getresponse()
        data = r.read()
        status = r.status
        hdrs = dict(r.getheaders())
        conn.close()
        return status, data, hdrs

    def test_secure_cookie_flagged_when_enabled(self):
        _, _, hdrs = self._get("/")
        cookie = hdrs.get("Set-Cookie", "")
        self.assertIn("aj_var=", cookie)
        self.assertIn("Secure", cookie, "HTTPS 环境下 cookie 必须带 Secure")
        self.assertIn("HttpOnly", cookie)

    def test_hsts_only_when_secure_enabled(self):
        _, _, hdrs = self._get("/")
        self.assertIn("Strict-Transport-Security", hdrs)

    def test_csp_present_and_blocks_inline_script(self):
        _, _, hdrs = self._get("/")
        csp = hdrs.get("Content-Security-Policy", "")
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        # 严格 CSP 下内联脚本会被拦，故页面不得含内联 <script>
        self.assertNotIn("unsafe-inline", csp)

    def test_frame_options_deny(self):
        _, _, hdrs = self._get("/")
        self.assertEqual(hdrs.get("X-Frame-Options"), "DENY")

    def test_variant_delivered_via_meta_not_inline_script(self):
        """变体 ID 必须走 <meta>，这样 CSP 才能用 script-src 'self' 而无需 nonce。"""
        status, body, _ = self._get("/")
        html = body.decode()
        self.assertEqual(status, 200)
        self.assertRegex(html, r'<meta name="aj-variant" content="[ABC]">')
        self.assertNotIn("window.AJ_VARIANT", html, "不得再有内联脚本注入变体")
        self.assertNotIn("<script>", html)

    def test_app_js_reads_variant_from_meta(self):
        js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn('meta[name="aj-variant"]', js)
        self.assertNotIn("window.AJ_VARIANT", js, "app.js 不得再依赖内联脚本的全局变量")


if __name__ == "__main__":
    unittest.main(verbosity=2)