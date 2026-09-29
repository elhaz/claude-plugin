"""analysis_history — 이력 보관·링크."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import analysis_history as ah  # noqa: E402

DOC = """---
tags:
  - 종목분석
  - 기술
ticker: TEST
updated: 2026-03-26
---

# 테스트 (TEST)

본문 종목분석 단어는 그대로.

---
**태그**: #종목분석 #기술 #종목분석가
"""

INLINE = "---\ntags: [종목분석, 반도체]\nupdated: 2026-07-19\n---\n본문\n"


class AnalysisHistoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.doc = self.dir / "테스트.md"
        self.doc.write_text(DOC, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_archive_retags_and_names_by_date(self):
        out = ah.archive(self.doc)
        self.assertEqual(out, self.dir / "이력" / "테스트" / "2026-03-26.md")
        text = out.read_text(encoding="utf-8")
        self.assertIn("  - 종목분석이력\n", text)
        self.assertIn("#종목분석이력 #기술 #종목분석가", text)
        self.assertIn("본문 종목분석 단어는 그대로", text)
        self.assertIn("[[테스트]]", text)

    def test_inline_tags(self):
        self.doc.write_text(INLINE, encoding="utf-8")
        text = ah.archive(self.doc).read_text(encoding="utf-8")
        self.assertIn("tags: [종목분석이력, 반도체]", text)

    def test_archive_same_version_twice_is_noop(self):
        a, b = ah.archive(self.doc), ah.archive(self.doc)
        self.assertEqual(a, b)
        self.assertEqual(len(list((self.dir / "이력" / "테스트").iterdir())), 1)

    def test_archive_different_version_same_date_gets_suffix(self):
        ah.archive(self.doc)
        self.doc.write_text(DOC.replace("본문", "새 본문"), encoding="utf-8")
        self.assertEqual(ah.archive(self.doc).name, "2026-03-26-2.md")

    def test_link_rewrites_section(self):
        ah.archive(self.doc)
        self.assertEqual(ah.link(self.doc), 1)
        self.assertEqual(ah.link(self.doc), 1)   # 두 번 불러도 절은 하나
        text = self.doc.read_text(encoding="utf-8")
        self.assertEqual(text.count("## 이전 분석"), 1)
        self.assertIn("- [[이력/테스트/2026-03-26|2026-03-26]]", text)

    def test_new_doc_archive_returns_none(self):
        self.assertIsNone(ah.archive(self.dir / "없음.md"))


if __name__ == "__main__":
    unittest.main()
