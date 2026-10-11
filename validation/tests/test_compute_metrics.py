"""compute_metrics.py 的测试。

运行::

    python3 -m unittest discover -s validation/tests -v
"""

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import compute_metrics as cm  # noqa: E402

THRESHOLDS_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / ".spec-workflow" / "specs" / "agentjobs" / "validation-metrics.md"
)

T = cm.load_thresholds(THRESHOLDS_PATH)

HEADERS = {name: ",".join(s.names) for name, s in cm.SCHEMAS.items()}


def write_data(base: Path, *, subscribers=None, interviews=None, companies=None,
               survey=None, social=None, competitors=None, drop_column=None):
    """写出一套 6 份 CSV。drop_column 用于模拟缺列。"""
    fixtures = {
        "subscribers": subscribers or [],
        "interviews": interviews or [],
        "companies": companies or [],
        "survey_responses": survey or [],
        "social_posts": social or [],
        "competitors": competitors or [],
    }
    base.mkdir(parents=True, exist_ok=True)
    for name, rows in fixtures.items():
        header = HEADERS[name]
        if drop_column == name:
            header = ",".join(h for h in header.split(",") if h != "strong_need")
        text = header + "\n" + "".join(
            ",".join(str(r.get(h, "")) for h in header.split(",")) + "\n" for r in rows
        )
        (base / f"{name}.csv").write_text(text, encoding="utf-8")
    return base


def ideal_survey(n=200):
    """全部达理想值的问卷数据（用于构造不会提前失败的场景）。"""
    return [
        {
            "respondent_id": f"s{i}", "submitted_at": "2026-10-08", "source_channel": "r",
            "m4_answer": "very_needed", "m12_answer": "agree",
            "differentiation_needs": "a;b;c", "survey_started": "true",
        }
        for i in range(n)
    ]


class TestThresholdParsing(unittest.TestCase):
    """阈值必须来自 validation-metrics.md，而非硬编码。"""

    def test_parses_every_ladder_row(self):
        # M1 两行（首周/次周累计）+ M2-M12 共 11 行 + S1-S3 + D1-D2 = 18
        self.assertEqual(len(T), 18, "判定阶梯应解析出 18 行")

    def test_m1_split_into_two_keys(self):
        self.assertIn("M1.首周", T)
        self.assertIn("M1.次周累计", T)

    def test_percent_metrics_are_ratio(self):
        self.assertEqual(T["M4"].kind, "ratio")
        self.assertEqual(T["M4"].ideal.value, 0.80)
        self.assertEqual(T["M4"].passed.value, 0.60)
        self.assertEqual(T["M4"].fail.value, 0.20)

    def test_count_metrics_are_count(self):
        self.assertEqual(T["S1"].kind, "count")
        self.assertEqual(T["S1"].passed.value, 10)

    def test_score_metrics_detected_from_slash_ten(self):
        """M7 / M10 写作「≥ 8/10」，必须识别为 score 而非 count。"""
        self.assertEqual(T["M7"].kind, "score")
        self.assertEqual(T["M7"].passed.value, 7.0)
        self.assertEqual(T["M10"].kind, "score")

    def test_m10_is_lower_is_better(self):
        """M10 失败值写作「≥ 7/10」，方向须自动识别为低优。"""
        self.assertTrue(T["M10"].lower_is_better)
        self.assertFalse(T["M7"].lower_is_better)
        self.assertFalse(T["M4"].lower_is_better)

    def test_zero_floor_becomes_equality(self):
        """M8 / D1 的失败值写作「0 家」「0 个」，语义为 == 0。"""
        self.assertEqual(T["M8"].fail.op, "=")
        self.assertEqual(T["D1"].fail.op, "=")

    def test_thresholds_follow_document_changes(self):
        """改文档阈值 → 解析结果随之改变，证明未硬编码。"""
        import re

        original = THRESHOLDS_PATH.read_text(encoding="utf-8")
        mutated = original.replace("| M4 | 强需求表达比例 | ≥ 80% | ≥ 60% | < 20% |",
                                   "| M4 | 强需求表达比例 | ≥ 90% | ≥ 70% | < 10% |")
        self.assertNotEqual(original, mutated, "测试前提：判定阶梯行文本须匹配")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "v.md"
            p.write_text(mutated, encoding="utf-8")
            self.assertEqual(cm.load_thresholds(p)["M4"].passed.value, 0.70)


class TestJudge(unittest.TestCase):
    """判定阶梯四档判定。"""

    def test_four_bands_higher_is_better(self):
        t = T["M4"]  # 理想 ≥80% / 通过 ≥60% / 失败 <20%
        self.assertEqual(cm.judge(0.85, t), cm.IDEAL)
        self.assertEqual(cm.judge(0.60, t), cm.PASS)
        self.assertEqual(cm.judge(0.30, t), cm.NOT_MET)
        self.assertEqual(cm.judge(0.10, t), cm.FAIL)

    def test_four_bands_lower_is_better(self):
        t = T["M10"]  # 理想 ≤4 / 通过 ≤5 / 失败 ≥7
        self.assertEqual(cm.judge(3.5, t), cm.IDEAL)
        self.assertEqual(cm.judge(5.0, t), cm.PASS)
        self.assertEqual(cm.judge(6.0, t), cm.NOT_MET)
        self.assertEqual(cm.judge(7.5, t), cm.FAIL)

    def test_equality_fail_floor(self):
        """M8 失败值为 == 0：0 失败，>0 不失败。"""
        t = T["M8"]
        self.assertEqual(cm.judge(0.0, t), cm.FAIL)
        self.assertEqual(cm.judge(0.1, t), cm.NOT_MET)
        self.assertEqual(cm.judge(0.2, t), cm.PASS)
        self.assertEqual(cm.judge(0.4, t), cm.IDEAL)

    def test_none_is_no_data_not_zero(self):
        """缺数据必须是无数据源，不得按 0 处理（否则会被误判为失败）。"""
        self.assertEqual(cm.judge(None, T["M4"]), cm.NO_DATA)


class TestSchemaValidation(unittest.TestCase):
    """缺列 / 枚举非法 / 越界 必须明确报错。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_required_column_raises(self):
        write_data(self.dir, interviews=[{
            "respondent_id": "d1", "skill_tags": "LangChain", "job_search_status": "active",
            "pain_points": "a;b;c", "needs": "x", "strong_need": "true",
            "interview_date": "2026-10-08", "channel": "github",
        }], drop_column="interviews")
        with self.assertRaises(cm.SchemaError) as ctx:
            cm.load_csv(self.dir, "interviews")
        self.assertIn("strong_need", str(ctx.exception))

    def test_illegal_enum_raises(self):
        write_data(self.dir, subscribers=[{
            "email": "a@b.com", "source_channel": "x", "ab_variant": "Z",
            "subscribed_at": "2026-10-07", "confirmed_at": "", "unsubscribed_at": "",
        }])
        with self.assertRaises(cm.SchemaError) as ctx:
            cm.load_csv(self.dir, "subscribers")
        self.assertIn("ab_variant", str(ctx.exception))
        self.assertIn("'Z'", str(ctx.exception))

    def test_illegal_bool_raises(self):
        write_data(self.dir, interviews=[{
            "respondent_id": "d1", "skill_tags": "LangChain", "job_search_status": "active",
            "pain_points": "a;b;c", "needs": "x", "strong_need": "maybe",
            "interview_date": "2026-10-08", "channel": "github",
        }])
        with self.assertRaises(cm.SchemaError):
            cm.load_csv(self.dir, "interviews")

    def test_out_of_range_score_raises(self):
        write_data(self.dir, competitors=[{
            "platform": "LinkedIn", "job_types_covered": "a", "agent_job_availability": "few",
            "skill_tag_support": "weak", "differentiation": "x", "satisfaction_score": "12",
            "evidence_url": "https://x",
        }])
        with self.assertRaises(cm.SchemaError) as ctx:
            cm.load_csv(self.dir, "competitors")
        self.assertIn("越界", str(ctx.exception))

    def test_bad_date_raises(self):
        write_data(self.dir, subscribers=[{
            "email": "a@b.com", "source_channel": "x", "ab_variant": "A",
            "subscribed_at": "07/10/2026", "confirmed_at": "", "unsubscribed_at": "",
        }])
        with self.assertRaises(cm.SchemaError):
            cm.load_csv(self.dir, "subscribers")

    def test_missing_file_raises_with_hint(self):
        self.dir.mkdir(exist_ok=True)
        with self.assertRaises(cm.SchemaError) as ctx:
            cm.load_csv(self.dir, "competitors")
        self.assertIn("templates/competitors.csv", str(ctx.exception))


class TestCompute(unittest.TestCase):
    """指标计算与判定规则。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _rep(self, **kw):
        write_data(self.dir, **kw)
        return cm.compute(self.dir, T, window_start=date(2026, 10, 7))

    def test_m1_week_windows(self):
        rep = self._rep(subscribers=[
            {"email": "a@x.com", "source_channel": "r", "ab_variant": "A",
             "subscribed_at": "2026-10-07T10:00:00", "confirmed_at": "", "unsubscribed_at": ""},
            {"email": "b@x.com", "source_channel": "r", "ab_variant": "B",
             "subscribed_at": "2026-10-10T10:00:00", "confirmed_at": "", "unsubscribed_at": ""},
            # 第 3 周，必须落在两个窗口之外
            {"email": "c@x.com", "source_channel": "r", "ab_variant": "C",
             "subscribed_at": "2026-10-25T10:00:00", "confirmed_at": "", "unsubscribed_at": ""},
        ])
        got = {r.key: r.value for r in rep.results}
        self.assertEqual(got["M1.首周"], 2)
        self.assertEqual(got["M1.次周累计"], 2)

    def test_m3_completion_rate(self):
        rep = self._rep(survey=[
            {"respondent_id": "s1", "submitted_at": "2026-10-08", "source_channel": "reddit",
             "m4_answer": "very_needed", "m12_answer": "agree", "survey_started": "true"},
            {"respondent_id": "s2", "submitted_at": "", "source_channel": "reddit",
             "m4_answer": "", "m12_answer": "", "survey_started": "true"},
            {"respondent_id": "s3", "submitted_at": "", "source_channel": "reddit",
             "m4_answer": "", "m12_answer": "", "survey_started": "false"},
        ])
        got = {r.key: r.value for r in rep.results}
        self.assertAlmostEqual(got["M3"], 0.5)  # 1 提交 / 2 开始

    def test_m5_counts_three_or_more_pain_points(self):
        rep = self._rep(interviews=[
            {"respondent_id": "d1", "skill_tags": "L", "job_search_status": "active",
             "pain_points": "a;b;c", "needs": "x", "strong_need": "true",
             "interview_date": "2026-10-08", "channel": "gh"},
            {"respondent_id": "d2", "skill_tags": "L", "job_search_status": "active",
             "pain_points": "a;b", "needs": "x", "strong_need": "false",
             "interview_date": "2026-10-08", "channel": "gh"},
        ])
        got = {r.key: r.value for r in rep.results}
        self.assertAlmostEqual(got["M5"], 0.5)

    def test_m4_prefers_survey_over_interviews(self):
        rep = self._rep(
            interviews=[{"respondent_id": "d1", "skill_tags": "L", "job_search_status": "a",
                         "pain_points": "a;b;c", "needs": "x", "strong_need": "false",
                         "interview_date": "2026-10-08", "channel": "gh"}],
            survey=[{"respondent_id": "s1", "submitted_at": "2026-10-08", "source_channel": "r",
                     "m4_answer": "very_needed", "m12_answer": "agree", "survey_started": "true"}],
        )
        got = {r.key: r.value for r in rep.results}
        self.assertAlmostEqual(got["M4"], 1.0)
        self.assertTrue(any("交叉校验" in n for n in rep.notes))

    def test_m10_mean_satisfaction(self):
        rep = self._rep(competitors=[
            {"platform": "A", "job_types_covered": "x", "agent_job_availability": "y",
             "skill_tag_support": "z", "differentiation": "标签筛选;Agent岗位专区",
             "satisfaction_score": "4", "evidence_url": "https://a"},
            {"platform": "B", "job_types_covered": "x", "agent_job_availability": "y",
             "skill_tag_support": "z", "differentiation": "标签筛选",
             "satisfaction_score": "6", "evidence_url": "https://b"},
        ])
        got = {r.key: r.value for r in rep.results}
        self.assertAlmostEqual(got["M10"], 5.0)
        self.assertEqual(got["D1"], 2)  # 去重后 2 个差异化点

    def test_sample_shortfall_advisory_not_failure(self):
        """S1 未达标时不得判失败，且 M5 应带样本量提示。"""
        rep = self._rep(interviews=[{
            "respondent_id": "d1", "skill_tags": "L", "job_search_status": "active",
            "pain_points": "a;b;c", "needs": "x", "strong_need": "true",
            "interview_date": "2026-10-08", "channel": "gh",
        }])
        s1 = next(r for r in rep.results if r.key == "S1")
        self.assertEqual(s1.verdict, cm.FAIL)
        m5 = next(r for r in rep.results if r.key == "M5")
        self.assertNotEqual(m5.verdict, cm.FAIL)
        self.assertIn("样本量", m5.advisory)

    def test_structural_gap_is_D2_only(self):
        """填满全部 6 份 schema 后，唯一无数据源的应是 D2（验证期按裁定不评估）。"""
        rep = self._rep(
            subscribers=[{"email": "a@x.com", "source_channel": "r", "ab_variant": "A",
                          "subscribed_at": "2026-10-07", "confirmed_at": "", "unsubscribed_at": ""}],
            interviews=[{"respondent_id": "d1", "skill_tags": "L", "job_search_status": "a",
                         "pain_points": "a;b;c", "needs": "x", "strong_need": "true",
                         "interview_date": "2026-10-08", "channel": "gh"}],
            companies=[{"company_id": "c1", "agent_projects": "p", "hiring_challenge": "h",
                        "required_skills": "L", "interested_in_platform": "true",
                        "has_budget": "true", "committed_to_post": "true",
                        "difficulty_score": "8", "interview_date": "2026-10-08"}],
            survey=[{"respondent_id": "s1", "submitted_at": "2026-10-08", "source_channel": "r",
                     "m4_answer": "very_needed", "m12_answer": "agree",
                     "differentiation_needs": "a;b;c", "survey_started": "true"}],
            social=[{"platform": "reddit", "post_url": "https://r/1", "published_at": "2026-10-07",
                     "impressions": "1000", "likes": "50", "comments": "10", "shares": "5"}],
            competitors=[{"platform": "A", "job_types_covered": "x", "agent_job_availability": "y",
                          "skill_tag_support": "z", "differentiation": "标签筛选",
                          "satisfaction_score": "4", "evidence_url": "https://a"}],
        )
        gaps = {r.key for r in rep.results if r.verdict == cm.NO_DATA}
        self.assertEqual(gaps, {"D2"})

    # ---- M2 社媒互动率（2026-10-11 裁定新增 social_posts.csv）----

    def test_m2_averages_per_post_rates(self):
        """M2 = 逐条互动率的算术平均，不是总量比。"""
        rep = self._rep(social=[
            {"platform": "reddit", "post_url": "https://r/1", "published_at": "2026-10-07",
             "impressions": "1000", "likes": "50", "comments": "10", "shares": "5"},  # 6.5%
            {"platform": "reddit", "post_url": "https://r/2", "published_at": "2026-10-08",
             "impressions": "100", "likes": "0", "comments": "0", "shares": "0"},    # 0%
        ])
        m2 = next(r for r in rep.results if r.key == "M2")
        self.assertAlmostEqual(m2.value, (0.065 + 0.0) / 2)  # 3.25%，非 65/1100

    def test_m2_skips_zero_impression_posts(self):
        """impressions=0 必须跳过并提示，不得按 0 计入均值。"""
        rep = self._rep(social=[
            {"platform": "x", "post_url": "https://x/1", "published_at": "2026-10-07",
             "impressions": "1000", "likes": "100", "comments": "0", "shares": "0"},  # 10%
            {"platform": "x", "post_url": "https://x/2", "published_at": "2026-10-07",
             "impressions": "0", "likes": "0", "comments": "0", "shares": "0"},       # 跳过
        ])
        m2 = next(r for r in rep.results if r.key == "M2")
        self.assertAlmostEqual(m2.value, 0.10, msg="不得因 0 曝光帖子而拉低均值")
        self.assertIn("跳过 1 条", m2.detail)

    def test_m2_negative_count_rejected(self):
        write_data(self.dir, social=[{"platform": "x", "post_url": "u", "published_at": "2026-10-07",
                                      "impressions": "100", "likes": "-5", "comments": "0",
                                      "shares": "0"}])
        with self.assertRaises(cm.SchemaError):
            cm.load_csv(self.dir, "social_posts")

    # ---- M11 差异化需求（2026-10-11 裁定改为问卷口径）----

    def test_m11_from_survey_counts_three_or_more(self):
        rep = self._rep(survey=[
            {"respondent_id": "s1", "submitted_at": "2026-10-08", "source_channel": "r",
             "m4_answer": "very_needed", "m12_answer": "agree",
             "differentiation_needs": "a;b;c", "survey_started": "true"},   # 3 项 → 计入
            {"respondent_id": "s2", "submitted_at": "2026-10-08", "source_channel": "r",
             "m4_answer": "very_needed", "m12_answer": "agree",
             "differentiation_needs": "a;b", "survey_started": "true"},      # 2 项 → 不计入
            {"respondent_id": "s3", "submitted_at": "2026-10-08", "source_channel": "r",
             "m4_answer": "very_needed", "m12_answer": "agree",
             "differentiation_needs": "a;b;c;d", "survey_started": "true"}, # 4 项 → 计入
        ])
        m11 = next(r for r in rep.results if r.key == "M11")
        self.assertAlmostEqual(m11.value, 2 / 3)

    def test_m11_ignores_competitors_csv(self):
        """M11 已裁定改用问卷；competitors.csv 的数据不得再影响它。"""
        rep = self._rep(
            survey=[{"respondent_id": "s1", "submitted_at": "2026-10-08", "source_channel": "r",
                     "m4_answer": "very_needed", "m12_answer": "agree",
                     "differentiation_needs": "a", "survey_started": "true"}],
            competitors=[{"platform": "A", "job_types_covered": "x", "agent_job_availability": "y",
                          "skill_tag_support": "z", "differentiation": "a;b;c;d;e",
                          "satisfaction_score": "4", "evidence_url": "https://a"}],
        )
        m11 = next(r for r in rep.results if r.key == "M11")
        self.assertAlmostEqual(m11.value, 0.0)  # 问卷只勾 1 项
        d1 = next(r for r in rep.results if r.key == "D1")
        self.assertEqual(d1.value, 5)  # D1 仍由 competitors 产出

    def test_m11_absent_when_question_omitted(self):
        rep = self._rep(survey=[{"respondent_id": "s1", "submitted_at": "2026-10-08",
                                 "source_channel": "r", "m4_answer": "very_needed",
                                 "m12_answer": "agree", "differentiation_needs": "",
                                 "survey_started": "true"}])
        m11 = next(r for r in rep.results if r.key == "M11")
        self.assertEqual(m11.verdict, cm.NO_DATA)
        self.assertIn("A1.3", m11.detail)

    # ---- D2 验证期不评估（2026-10-11 裁定）----

    def test_d2_absence_is_not_a_provisional_gap(self):
        """D2 缺席是设计预期，不应把结论标为「暂定」，但必须声明未含终端证据。"""
        rep = self._rep(
            subscribers=[{"email": f"u{i}@x.com", "source_channel": "r", "ab_variant": "A",
                          "subscribed_at": "2026-10-07", "confirmed_at": "",
                          "unsubscribed_at": ""} for i in range(120)],
            interviews=[{"respondent_id": f"d{i}", "skill_tags": "L", "job_search_status": "a",
                         "pain_points": "a;b;c", "needs": "x", "strong_need": "true",
                         "interview_date": "2026-10-08", "channel": "gh"} for i in range(15)],
            companies=[{"company_id": f"c{i}", "agent_projects": "p", "hiring_challenge": "h",
                        "required_skills": "L", "interested_in_platform": "true",
                        "has_budget": "true", "committed_to_post": "true",
                        "difficulty_score": "9", "interview_date": "2026-10-08"}
                       for i in range(8)],
            survey=ideal_survey(),
            social=[{"platform": "reddit", "post_url": "https://r/1", "published_at": "2026-10-07",
                     "impressions": "1000", "likes": "100", "comments": "20", "shares": "10"}],
            competitors=[{"platform": "A", "job_types_covered": "x", "agent_job_availability": "y",
                          "skill_tag_support": "z", "differentiation": "标签筛选;Agent专区;社区",
                          "satisfaction_score": "3", "evidence_url": "https://a"}],
        )
        conclusion, notes = cm.conclude(rep)
        joined = " ".join(notes)
        self.assertNotIn("结论为暂定", joined, "D2 缺席不应触发暂定警告")
        self.assertIn("未含 D2 终端证据", joined)
        self.assertIn(conclusion, ("验证通过", "强力验证"))
        self.assertIn("优先促成首个匹配", joined)

    def test_risk4_fires_on_d2_absence_plus_three_not_met(self):
        """风险 4 告警须按「D2 缺席」触发，而非「D2 = 0」——否则会漏报。

        数据刻意取在「未达标」区间（S 与多项 M），但**不命中任何失败值**，
        以确保走到未达标分支而非提前返回。
        """
        rep = self._rep(
            subscribers=[{"email": f"u{i}@x.com", "source_channel": "r", "ab_variant": "A",
                          "subscribed_at": "2026-10-07", "confirmed_at": "",
                          "unsubscribed_at": ""} for i in range(30)],
            # S1=6（未达标 5~9）；M5=50%（未达标 50~69）
            interviews=[{"respondent_id": f"d{i}", "skill_tags": "L", "job_search_status": "a",
                         "pain_points": "a;b;c" if i < 3 else "a;b", "needs": "x",
                         "strong_need": "false", "interview_date": "2026-10-08",
                         "channel": "gh"} for i in range(6)],
            # S2=3（未达标 2~4）；M6=33%（未达标 10~39）；M7=6.0（未达标 5~6.9）
            companies=[{"company_id": f"c{i}", "agent_projects": "p", "hiring_challenge": "h",
                        "required_skills": "L", "interested_in_platform": "true" if i == 0 else "false",
                        "has_budget": "true" if i < 2 else "false",
                        "committed_to_post": "true" if i == 0 else "false",
                        "difficulty_score": "6.0", "interview_date": "2026-10-08"}
                       for i in range(3)],
            # S3=60（未达标 50~99）；M4=30%（未达标 20~59）；M11=40%（未达标 40~69）
            survey=[{
                "respondent_id": f"s{i}", "submitted_at": "2026-10-08", "source_channel": "r",
                "m4_answer": "very_needed" if i < 18 else "not_needed",
                "m12_answer": "agree" if i < 42 else "neutral",
                "differentiation_needs": "a;b;c" if i < 24 else "a",
                "survey_started": "true",
            } for i in range(60)],
            social=[{"platform": "reddit", "post_url": "https://r/1", "published_at": "2026-10-07",
                     "impressions": "1000", "likes": "50", "comments": "10", "shares": "5"}],
            # M10=6.5（未达标 5.1~6.9）；D1=1（未达标，失败值为 0）
            competitors=[{"platform": "A", "job_types_covered": "x", "agent_job_availability": "y",
                          "skill_tag_support": "z", "differentiation": "标签筛选",
                          "satisfaction_score": "6.5", "evidence_url": "https://a"}],
        )
        self.assertFalse([r for r in rep.results if r.verdict == cm.FAIL], "数据不应命中失败值")
        conclusion, notes = cm.conclude(rep)
        joined = " ".join(notes)
        self.assertIn("未达标", conclusion)
        self.assertIn("D2 缺席", joined)
        self.assertIn("风险 4", joined)

    def test_empty_data_never_silently_zeroes_percentages(self):
        """空数据集时：计数类指标 S1/S2/S3 = 0 判失败（语义正确）；
        百分比类指标分母为 0，必须是「无数据源」而非按 0 处理后误判。"""
        rep = self._rep()
        by_key = {r.key: r for r in rep.results}

        for k in ("S1", "S2", "S3"):
            self.assertEqual(by_key[k].value, 0)
            self.assertEqual(by_key[k].verdict, cm.FAIL, "零份访谈确实命中失败值")

        for k in ("M3", "M4", "M5", "M6", "M7", "M9", "M11", "M12", "M2"):
            self.assertIsNone(by_key[k].value, f"{k} 分母为 0 时不得返回 0")
            self.assertEqual(by_key[k].verdict, cm.NO_DATA, f"{k} 不得因分母为 0 而判失败")

    def test_d1_zero_with_no_data_is_no_data(self):
        """D1 无 differentiation 数据时是无数据源；D1=0 才是失败（完全无法识别差异化点）。"""
        rep = self._rep(competitors=[{
            "platform": "A", "job_types_covered": "x", "agent_job_availability": "y",
            "skill_tag_support": "z", "differentiation": "", "satisfaction_score": "4",
            "evidence_url": "https://a",
        }])
        d1 = next(r for r in rep.results if r.key == "D1")
        self.assertEqual(d1.verdict, cm.NO_DATA)

    def test_conclusion_failure_on_any_fail_value(self):
        rep = self._rep(companies=[{
            "company_id": "c1", "agent_projects": "p", "hiring_challenge": "h",
            "required_skills": "L", "interested_in_platform": "false",
            "has_budget": "false", "committed_to_post": "false",
            "difficulty_score": "3", "interview_date": "2026-10-08",
        }])
        conclusion, _ = cm.conclude(rep)
        self.assertTrue(conclusion.startswith("验证失败"))


if __name__ == "__main__":
    unittest.main(verbosity=2)