"""역산 DCF — 투자원칙 v2 2절 예시 표와 같은 값이 나오는지."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import reverse_dcf as rd  # noqa: E402


class ReverseDcfTest(unittest.TestCase):
    def test_v2_example_table(self):
        # 주당 현금흐름 $1, 할인율 10%, 10년, 이후 15배
        for price, want in [(25, 10.0), (36, 15.0), (60, 21.8), (100, 28.9)]:
            self.assertAlmostEqual(rd.required_growth(price, 1.0) * 100, want, delta=0.15, msg=price)

    def test_verdicts(self):
        self.assertEqual(rd.judge(10.0, 15)["verdict"], "사유형")
        self.assertEqual(rd.judge(21.8, 15)["verdict"], "사유형")      # 1.45배 — 배수 미달
        self.assertEqual(rd.judge(28.9, 15)["verdict"], "적정가형")    # 1.93배 · +13.9%p
        self.assertEqual(rd.judge(3.0, 2)["verdict"], "사유형")        # 1.5배지만 차이 1%p

    def test_non_positive_cash_flow(self):
        self.assertIsNone(rd.required_growth(50, -0.3))
        self.assertEqual(rd.judge(None, 20)["verdict"], "계산 불가")

    def test_cli_json(self):
        self.assertEqual(rd.main(["--price", "100", "--per-share", "1", "--actual-growth", "15", "--json"]), 0)


if __name__ == "__main__":
    unittest.main()
