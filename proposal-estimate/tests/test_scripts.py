"""스크립트 시험 — 배율 계산 · 노트 채우기 · 금액 거르기 · 레인 그림."""

import copy
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import estimate_config  # noqa: E402
import fill_note  # noqa: E402
import lane_diagram  # noqa: E402
import ppt_extract  # noqa: E402
import real_effort  # noqa: E402

EXAMPLE = json.loads((ROOT / "examples" / "pm_estimate_example.json").read_text(encoding="utf-8"))
CFG = estimate_config.load(ROOT / "config" / "settings.json")


class RoundTest(unittest.TestCase):
    def test_half_up(self):
        # 0.25 는 0.5 로, 1.125 는 1.0 으로 (짝수 반올림이 아니다)
        self.assertEqual(estimate_config.round_md(0.25), 0.5)
        self.assertEqual(estimate_config.round_md(1.125), 1.0)
        self.assertEqual(estimate_config.round_md(2.75), 3.0)
        self.assertEqual(estimate_config.round_md(5 * 0.45), 2.5)


class RealEffortTest(unittest.TestCase):
    def test_example_totals(self):
        r = real_effort.compute(EXAMPLE, CFG)
        self.assertEqual(r["total_est"], 54.5)
        self.assertEqual(r["total_real"], 36.0)
        self.assertEqual(r["amount_est"], round(54.5 * 378250))
        self.assertIn("F05-0", r["by_kind"]["logic"])
        # 섹션 기본 kind 가 행에 내려간다
        self.assertIn("A1", r["by_kind"]["analysis"])

    def test_missing_kind_stops(self):
        d = copy.deepcopy(EXAMPLE)
        del d["rows"][2]["kind"]
        with self.assertRaises(ValueError) as cm:
            real_effort.compute(d, CFG)
        self.assertIn("F02-2", str(cm.exception))

    def test_unknown_section_stops(self):
        d = copy.deepcopy(EXAMPLE)
        d["rows"][0]["section"] = "ZZ"
        with self.assertRaises(ValueError):
            real_effort.compute(d, CFG)


class FillNoteTest(unittest.TestCase):
    def setUp(self):
        self.res = real_effort.compute(EXAMPLE, CFG)
        self.vals = fill_note.build(EXAMPLE, self.res, CFG)

    def test_reduce_rejected_not_counted(self):
        self.assertEqual(self.vals["reduce_total"], "−1.0")
        self.assertEqual(self.vals["reduce_after"], "53.5")
        self.assertIn("~~F02-2 여유율 수동 조정 미룸~~", self.vals["reduce"])

    def test_options_and_schedule(self):
        self.assertEqual(self.vals["opt_total"], "29.0")
        self.assertEqual(self.vals["wk1"], "8")   # 36.0 / 5 = 7.2 -> 8주
        self.assertEqual(self.vals["wk2"], "4")

    def test_tilde_escaped_in_tables(self):
        self.assertIn("4\\~10", self.vals["uncertain"])
        self.assertNotRegex(self.vals["options"], r"(?<!\\)~")

    def test_template_slots_all_known(self):
        tpl = (ROOT / "skills" / "proposal-estimate-workflow" / "references" / "estimate-note-template.md").read_text(encoding="utf-8")
        slots = set(fill_note.SLOT.findall(tpl))
        self.assertTrue(slots)
        self.assertEqual(slots - set(self.vals), set())

    def test_prose_left_stops(self):
        with self.assertRaises(KeyError):
            fill_note.fill("<<적을 것: 가정>>\n{{total_est}}", self.vals)
        self.assertEqual(fill_note.fill("{{total_est}} MD", self.vals), "54.5 MD")


class MoneyFilterTest(unittest.TestCase):
    def test_drop_money_lines(self):
        lines = ["견적 초안 49,962,000원", "총 사업비 3억원", "화면 12 · 입고 목록", "과제 (1,200천원) 중 일부", "원칙 3가지"]
        kept, dropped = ppt_extract.filter_lines(lines, drop_money=True)
        self.assertEqual(kept, ["화면 12 · 입고 목록", "과제  중 일부", "원칙 3가지"])
        self.assertEqual(len(dropped), 3)

    def test_drop_effort_lines(self):
        kept, dropped = ppt_extract.filter_lines(["고급 34 M/D", "총 127 M/D", "MTO 작성", "설치 위치 ±10mm"], drop_effort=True)
        self.assertEqual(kept, ["MTO 작성", "설치 위치 ±10mm"])

    def test_parse_pages(self):
        self.assertEqual(ppt_extract.parse_pages("1-3,7"), {1, 2, 3, 7})
        self.assertIsNone(ppt_extract.parse_pages(""))


class LaneTest(unittest.TestCase):
    def test_example_renders(self):
        spec = json.loads((ROOT / "examples" / "lane_spec_example.json").read_text(encoding="utf-8"))
        page, vw, vh = lane_diagram.render(spec)
        self.assertIn("<svg", page)
        self.assertEqual(page.count('rx="6" fill="#f5f5f5"'), len(spec["nodes"]))
        self.assertEqual(len(re.findall(r"marker-end", page)), len(spec["edges"]) + 4)  # 선 + 범례 4개

    def test_bad_edge_stops(self):
        spec = {"lanes": [{"key": "a", "name": "A"}], "nodes": [{"id": "x", "name": "X", "lane": "a", "col": 0}],
                "edges": [{"from": "x", "to": "y"}]}
        with self.assertRaises(ValueError):
            lane_diagram.render(spec)


if __name__ == "__main__":
    unittest.main()
