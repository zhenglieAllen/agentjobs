"""问卷题项校验器的测试 —— 任务 16 [A1.3]。

校验器本身若不能抓出漂移就毫无价值，故此处全部用例都是「故意破坏 → 必须报错」。

运行::

    python3 -m unittest discover -s survey/tests -v
"""

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "validation"))

import check_instrument as ci  # noqa: E402

BASE = ci.load()


def mutate(fn):
    """返回一份被 fn 破坏的问卷副本。"""
    instr = copy.deepcopy(BASE)
    fn(instr)
    return instr


def q(instr, qid):
    return next(x for x in instr["questions"] if x["id"] == qid)


class TestBaseline(unittest.TestCase):
    def test_current_instrument_is_valid(self):
        self.assertEqual(ci.check(BASE), [], "基准问卷必须零问题")

    def test_questions_json_and_markdown_stay_in_sync(self):
        """questions.json 与 survey-instrument.md 是同一份问卷的两个视图。

        校验器只读 JSON，故须额外确认 Markdown 没漏掉题号——
        否则投放者照着 Markdown 录入时会漏题。
        """
        md = (ROOT / "survey-instrument.md").read_text(encoding="utf-8")
        for question in BASE["questions"]:
            self.assertIn(f"**{question['id']}.**", md, f"{question['id']} 未出现在 Markdown 中")

    def test_enums_match_schema_choices(self):
        """枚举一致是硬契约：多一个值 load_csv 会报错，少一个值该选项静默归入「其他」。"""
        import compute_metrics as cm

        for field, qid in (("m4_answer", "Q8"), ("m12_answer", "Q10")):
            expected = set(cm.SCHEMAS["survey_responses"].by_name()[field].choices)
            actual = {o["value"] for o in q(BASE, qid)["options"]}
            self.assertEqual(actual, expected)


class TestDriftDetection(unittest.TestCase):
    """每条用例破坏一处，必须被抓出。"""

    def _assert_caught(self, instr, fragment):
        problems = ci.check(instr)
        self.assertTrue(problems, "校验器未发现问题 —— 守卫失效")
        self.assertTrue(
            any(fragment in p for p in problems),
            f"预期含 {fragment!r} 的问题，实际：{problems}",
        )

    def test_detects_missing_m11_question(self):
        """M11 只有这一个数据源，删题等于永久失去该指标。"""
        self._assert_caught(
            mutate(lambda i: i["questions"].remove(q(i, "Q9"))), "M11"
        )

    def test_detects_m11_limited_choices(self):
        self._assert_caught(
            mutate(lambda i: q(i, "Q9").update(unlimited_choices=False)), "不限项"
        )

    def test_detects_m11_wrong_type(self):
        self._assert_caught(
            mutate(lambda i: q(i, "Q9").update(type="single")), "多选"
        )

    def test_detects_m4_numerator_change(self):
        """M4 分子改为「比较需要」——阈值含义被篡改。"""
        def break_it(i):
            for o in q(i, "Q8")["options"]:
                o["numerator"] = o["value"] == "somewhat_needed"
        self._assert_caught(mutate(break_it), "M4")

    def test_detects_m4_extra_enum_value(self):
        """新增一个 schema 未定义的选项 → compute_metrics.load_csv 会报错。"""
        def break_it(i):
            q(i, "Q8")["options"].append(
                {"label": "看情况", "value": "depends", "numerator": False})
        self._assert_caught(mutate(break_it), "schema 未定义")

    def test_detects_m4_missing_enum_value(self):
        def break_it(i):
            q(i, "Q8")["options"] = [o for o in q(i, "Q8")["options"]
                                      if o["value"] != "not_at_all"]
        self._assert_caught(mutate(break_it), "缺少取值")

    def test_detects_m12_numerator_change(self):
        """M12 分子只剩 strongly_agree，口径被悄悄收窄。"""
        def break_it(i):
            for o in q(i, "Q10")["options"]:
                o["numerator"] = o["value"] == "strongly_agree"
        self._assert_caught(mutate(break_it), "M12")

    def test_detects_missing_start_instrumentation(self):
        """没有开始埋点 = M3 的分母不存在 = 该指标不可计算。"""
        self._assert_caught(mutate(lambda i: i.update(M3_requires_start_event=False)), "M3")

    def test_detects_disabled_randomization(self):
        self._assert_caught(mutate(lambda i: i.update(randomize_all_options=False)), "随机化")

    def test_detects_missing_intro(self):
        self._assert_caught(mutate(lambda i: i.update(intro="")), "开头说明")

    def test_detects_stale_metric_annotation(self):
        """题还在，但 metric 标注丢了 —— 提示后续维护者重新绑定。"""
        self._assert_caught(mutate(lambda i: q(i, "Q8").update(metric=None)), "M4")

    def test_detects_export_field_removal(self):
        """题还在但不再导出 → 指标拿不到数据。"""
        self._assert_caught(mutate(lambda i: q(i, "Q10").pop("export_field")), "m12_answer")


class TestStyleConstraints(unittest.TestCase):
    def test_length_within_five_minutes(self):
        """任务 Restrictions：5 分钟内完成。"""
        self.assertLessEqual(len(BASE["questions"]), 20)

    def test_intro_discloses_purpose(self):
        """开头须交代背景，否则受访者会猜测立场并给出讨好答案。"""
        intro = BASE["intro"]
        self.assertIn("不会用于招聘筛选", intro)
        self.assertIn("邮箱", intro)


if __name__ == "__main__":
    unittest.main(verbosity=2)