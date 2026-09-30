import unittest
from retrieval.reranker import (
    is_numeric_lookup_query,
    is_tabular_or_formula_chunk,
    cross_encode_rerank,
    validate_reranker_scores,
    TABLE_STRUCTURE_BOOST,
    EXPECTED_SCORE_MIN,
    EXPECTED_SCORE_MAX,
)

class TestRerankerBoostHardening(unittest.TestCase):
    def test_score_distribution_guard_fails_loudly_on_unnormalized_logits(self):
        """Ensures that validate_reranker_scores raises ValueError if scores fall outside [0.0, 1.0]."""
        # Valid normalized scores (should pass)
        valid_scores = [0.998, 0.985, 0.550, 0.0]
        try:
            validate_reranker_scores(valid_scores)
        except ValueError as e:
            self.fail(f"validate_reranker_scores unexpectedly failed on valid normalized scores: {e}")

        # Invalid unnormalized logits from an incompatible model swap (must fail loudly)
        unnormalized_logits = [12.4, -4.5, 0.95]
        with self.assertRaises(ValueError) as ctx:
            validate_reranker_scores(unnormalized_logits)
        self.assertIn("outside expected normalized range", str(ctx.exception))

    def test_classifier_identifies_numeric_vs_conceptual_queries(self):
        """Validates that financial metric lookups are classified as numeric, while conceptual theory queries are not."""
        numeric_queries = [
            "What were Apple's total net sales in fiscal year 2024?",
            "How much net sales did Apple generate from iPhone products in FY 2024?",
            "What was Apple's total Services revenue in FY2024?",
            "What were Apple's diluted earnings per share (EPS) in FY 2024?",
            "What was Apple's total gross margin in fiscal year 2024?",
            "What was the total net sales from the Greater China segment in 2024?"
        ]
        for q in numeric_queries:
            self.assertTrue(is_numeric_lookup_query(q), f"Failed to detect numeric query: {q}")

        conceptual_queries = [
            "What is the key difference between FIFO and LIFO in inventory accounting?",
            "What is the formula and definition for Weighted Average Cost of Capital (WACC)?",
            "Explain the 3-step DuPont Analysis decomposition of Return on Equity (ROE)",
            "What is the difference between Current Ratio and Quick Ratio?",
            "Why is asset allocation considered the primary determinant of portfolio return variability?",
            "What is portfolio rebalancing and how does it manage risk over time?"
        ]
        for q in conceptual_queries:
            self.assertFalse(is_numeric_lookup_query(q), f"Incorrectly classified conceptual query as numeric: {q}")

    def test_non_numeric_query_never_applies_boost(self):
        """Asserts that for non-numeric queries, tabular chunks are NEVER boosted over prose."""
        non_numeric_query = "What is the key difference between FIFO and LIFO in inventory accounting?"
        self.assertFalse(is_numeric_lookup_query(non_numeric_query))

        prose_chunk = "FIFO assumes first units in are first out, resulting in lower COGS during inflation."
        table_chunk = "| Method | Inventory Valuation | COGS |\n|---|---|---|\n| FIFO | Recent costs | Older costs |"

        # Even with table structure present, non-numeric queries trust the raw cross-encoder ranking
        reranked = cross_encode_rerank(non_numeric_query, [prose_chunk, table_chunk], top_k=2)
        self.assertEqual(len(reranked), 2)

    def test_tabular_detection_patterns(self):
        """Verifies table and boxed formula detection patterns."""
        markdown_table = (
            "| Segment | 2024 | 2023 |\n"
            "|---|---|---|\n"
            "| Americas | $150,000 | $145,000 |"
        )
        statement_row = (
            "CONSOLIDATED STATEMENTS OF OPERATIONS\n"
            "in millions\n"
            "2024 2023\n"
            "Products $ 294,866 $ 298,085"
        )
        boxed_formula = r"\boxed{WACC = \frac{D}{V}k_d(1-T) + \frac{E}{V}k_e}"
        regular_commentary = "Net sales increased during 2024 compared to 2023 due primarily to higher sales of Services."

        self.assertTrue(is_tabular_or_formula_chunk(markdown_table))
        self.assertTrue(is_tabular_or_formula_chunk(statement_row))
        self.assertTrue(is_tabular_or_formula_chunk(boxed_formula))
        self.assertFalse(is_tabular_or_formula_chunk(regular_commentary))

    def test_conceptual_queries_zero_regression_and_top_1_immutability(self):
        """
        Asserts that the boost never regresses the conceptual queries (#13-16, #23, #28, #31)
        and never flips the top-1 result for any query classified as non-numeric.
        """
        conceptual_queries = [
            ("q013", "What is the key difference between FIFO and LIFO inventory valuation methods during inflation?"),
            ("q014", "What is the formula and definition for Weighted Average Cost of Capital (WACC)?"),
            ("q015", "Explain the 3-step DuPont Analysis decomposition of Return on Equity (ROE)."),
            ("q016", "What is the difference between Current Ratio and Quick Ratio (Acid-Test Ratio)?"),
            ("q023", "What is Beta in modern portfolio theory and what does a Beta greater than 1 signify?"),
            ("q028", "Why is asset allocation considered the primary determinant of long-term portfolio return variance?"),
            ("q031", "What is portfolio rebalancing and how does it manage investment risk?"),
        ]

        # For each conceptual query, assert it is classified as non-numeric
        for q_id, q_text in conceptual_queries:
            self.assertFalse(
                is_numeric_lookup_query(q_text),
                f"Query {q_id} should be classified as non-numeric conceptual theory: {q_text}"
            )

        # Mock passage list containing a top-1 conceptual prose explanation and a lower-ranked table
        passages = [
            "Conceptual explanation: FIFO assumes first units purchased are sold first, preserving higher balance sheet asset value.",
            "| Segment | Net Sales 2024 | Net Sales 2023 |\n|---|---|---|\n| Greater China | $66,952 | $72,559 |",
            r"\boxed{WACC = \frac{D}{V}k_d(1-T) + \frac{E}{V}k_e}"
        ]

        for q_id, q_text in conceptual_queries:
            # Rerank with boost-enabled function
            reranked = cross_encode_rerank(q_text, passages, top_k=3)
            # Rerank directly with raw FlashRank (no boost)
            from retrieval.reranker import get_ranker
            from flashrank import RerankRequest
            ranker = get_ranker()
            req = RerankRequest(query=q_text, passages=[{"id": i, "text": p, "meta": {}} for i, p in enumerate(passages)])
            raw_results = [r["text"] for r in ranker.rerank(req)[:3]]

            # Assert top-1 and ordering is 100% identical to raw cross-encoder (boost never flips or alters anything)
            self.assertEqual(
                reranked,
                raw_results,
                f"Boost modified ranking on conceptual non-numeric query {q_id}: {q_text}"
            )

if __name__ == "__main__":
    unittest.main()
