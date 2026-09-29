"""fdp_fundamentals — 네트워크 없이 가공 로직만."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import fdp_fundamentals as ff  # noqa: E402

FUND = {
    "financials": {
        "income": {"annual": {"columns": ["item", "2025-12-31", "2024-12-31"], "data": [
            ["total_revenue", 1000.0, 800.0],
            ["diluted_earnings_per_share", 2.0, -1.0],
            ["weighted_average_diluted_shares_outstanding", 10.0, 10.0],
            ["ebitda", 200.0, 100.0],
        ]}},
        "balance": {"annual": {"columns": ["item", "2025-12-31", "2024-12-31"], "data": [
            ["common_stock_equity", 100.0, 100.0],
            ["long_term_debt", 50.0, None],
            ["cash_and_cash_equivalents", 30.0, 20.0],
        ]}},
    },
    "insider": {"days": 180, "columns": ["trade_date", "insider", "title", "code", "shares", "price", "value", "shares_after", "is_10b5_1"],
                "data": [
                    ["2026-09-01", "A", "CEO", "S", 10, 10, 100.0, 0, True],
                    ["2026-09-02", "B", None, "S", 10, 10, 300.0, 0, False],
                    ["2026-09-03", "C", "CFO", "P", 5, 10, 50.0, 0, None],
                    ["2026-09-04", "A", "CEO", "A", 5, 0, 0.0, 0, None],
                ]},
}


class FdpFundamentalsTest(unittest.TestCase):
    def test_ttm_needs_four_quarters(self):
        self.assertEqual(ff.ttm([1, 2, 3, 4, 5]), 10)
        self.assertIsNone(ff.ttm([1, 2, None, 4]))
        self.assertIsNone(ff.ttm([1, 2, 3]))

    def test_close_on_uses_last_close_before_day(self):
        prices = [("2024-12-30", 9.0), ("2024-12-31", 10.0), ("2025-12-30", 20.0), ("2026-01-02", 25.0)]
        self.assertEqual(ff.close_on(prices, "2025-12-31"), 20.0)
        self.assertIsNone(ff.close_on(prices, "2020-01-01"))

    def test_valuation_history(self):
        prices = [("2024-12-31", 10.0), ("2025-12-31", 20.0)]
        (y1, px1, pe1, evr1, eve1, pb1), (y0, _, pe0, evr0, _, _) = ff.valuation_history(FUND, prices)
        self.assertEqual((y1, px1), ("2025", 20.0))
        self.assertAlmostEqual(pe1, 10.0)               # 20 / 2
        self.assertAlmostEqual(evr1, (200 + 50 - 30) / 1000)
        self.assertAlmostEqual(eve1, 220 / 200)
        self.assertAlmostEqual(pb1, 2.0)                # 시총 200 / 자본 100
        self.assertIsNone(pe0)                          # 적자 해는 P/E 없음
        self.assertAlmostEqual(evr0, (100 - 20) / 800)  # 부채 없음

    def test_insider_summary(self):
        text = "\n".join(ff.insider_summary(FUND))
        self.assertIn("장내 매수 1건", text)
        self.assertIn("장내 매도 2건 $400", text)
        self.assertIn("10b5-1 계획 매도 1건 $100", text)
        self.assertTrue(text.index("B $300") < text.index("A (CEO) $100"))

    def test_korean_ticker_goes_to_web(self):
        self.assertEqual(ff.main(["005930"]), 2)


if __name__ == "__main__":
    unittest.main()
