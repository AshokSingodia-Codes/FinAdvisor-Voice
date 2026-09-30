import unittest
import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from core.auth import get_current_user, hash_password
from core.memory import create_user, get_db_connection
from core.rate_limiter import chat_rate_limiter
from sqlalchemy import text

class TestFastPathsBypassLLM(unittest.TestCase):
    def setUp(self):
        chat_rate_limiter.users.clear()
        # Create a real user so conversations.user_id FK is satisfied when
        # the chat endpoint calls create_conversation internally.
        _email = f"fastpath_{uuid.uuid4().hex[:8]}@test.com"
        _user_rec = create_user(_email, hash_password("FastPath1!"))
        self._test_user_id = _user_rec["id"]
        self.mock_user = {"id": self._test_user_id, "email": _email}
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        # Clean up test user
        with get_db_connection() as conn:
            conn.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": self._test_user_id})
            conn.commit()

    @patch("main.app_graph.stream")
    def test_pure_arithmetic_bypasses_graph(self, mock_graph_stream):
        """Pure math expressions must evaluate deterministically without invoking LangGraph."""
        arithmetic_queries = [
            "2*4*8+150",
            "8/2",
            "(4+4)*2",
            "17654487464+64465454",
            "5% of 2020",
            "3/4 of 500"
        ]
        for query in arithmetic_queries:
            with self.subTest(query=query):
                mock_graph_stream.reset_mock()
                response = self.client.post("/api/chat", json={"message": query})
                self.assertEqual(response.status_code, 200, f"Failed on {query}: {response.text}")
                data = response.json()
                self.assertTrue(len(data.get("answer", "")) > 0)
                mock_graph_stream.assert_not_called()

    @patch("main.app_graph.stream")
    def test_greeting_and_chitchat_bypasses_graph(self, mock_graph_stream):
        """Standard greetings and chitchat must return immediately without invoking LangGraph."""
        greeting_queries = [
            "hi",
            "hello",
            "good morning",
            "how are you",
            "who created you",
            "thank you",
            "bye"
        ]
        for query in greeting_queries:
            with self.subTest(query=query):
                mock_graph_stream.reset_mock()
                response = self.client.post("/api/chat", json={"message": query})
                self.assertEqual(response.status_code, 200, f"Failed on {query}: {response.text}")
                data = response.json()
                self.assertTrue(len(data.get("answer", "")) > 0)
                mock_graph_stream.assert_not_called()

    @patch("main.app_graph.stream")
    def test_fast_paths_streaming_bypasses_graph(self, mock_graph_stream):
        """Streaming mode for fast paths must also yield events without invoking LangGraph."""
        mock_graph_stream.reset_mock()
        response = self.client.post("/api/chat", json={"message": "hello", "stream": True})
        self.assertEqual(response.status_code, 200)
        content = response.text
        self.assertIn("event: step", content)
        self.assertIn("greeting_handler", content)
        self.assertIn("event: done", content)
        mock_graph_stream.assert_not_called()

        mock_graph_stream.reset_mock()
        response = self.client.post("/api/chat", json={"message": "100 + 250", "stream": True})
        self.assertEqual(response.status_code, 200)
        content = response.text
        self.assertIn("event: step", content)
        self.assertIn("fast_math", content)
        self.assertIn("350", content)
        mock_graph_stream.assert_not_called()

    @patch("main.app_graph.stream")
    def test_category_l_compound_greeting_and_query_invokes_graph(self, mock_graph_stream):
        """Category L (greeting + substantive financial query) MUST NOT be swallowed by fast path."""
        mock_graph_stream.return_value = iter([
            {"router": {"routing_decision": "market_data"}},
            {"market_data": {"draft_answer": "Reliance P/E ratio is ~28.5", "final_answer": "Reliance P/E ratio is ~28.5"}}
        ])
        
        compound_queries = [
            "Hi, what is the P/E ratio of Reliance?",
            "Hello, how does compound interest work?",
            "Good morning, analyze Apple's risk factors",
            "Hey, tell me about SIP vs Lump Sum investment",
            "What was the total gross merchandise volume of Cyberdyne Systems in 2020?"
        ]
        for query in compound_queries:
            with self.subTest(query=query):
                mock_graph_stream.reset_mock()
                response = self.client.post("/api/chat", json={"message": query})
                self.assertEqual(response.status_code, 200, f"Failed on {query}: {response.text}")
                mock_graph_stream.assert_called_once()

    @patch("main.app_graph.stream")
    def test_category_i_typo_fuzzy_greetings_bypass_graph(self, mock_graph_stream):
        """Category I (fuzzy/typo greetings) must evaluate deterministically without invoking LangGraph."""
        fuzzy_queries = ["hllo", "heyyy", "gud mrng", "thanx", "thx"]
        for query in fuzzy_queries:
            with self.subTest(query=query):
                mock_graph_stream.reset_mock()
                response = self.client.post("/api/chat", json={"message": query})
                self.assertEqual(response.status_code, 200, f"Failed on {query}: {response.text}")
                mock_graph_stream.assert_not_called()

    @patch("main.app_graph.stream")
    def test_category_j_hinglish_greetings_bypass_graph(self, mock_graph_stream):
        """Category J (Hinglish/regional greetings) must evaluate deterministically without invoking LangGraph."""
        hinglish_queries = ["namaste", "kem cho", "kaise ho", "kya chal raha hai", "radhe radhe"]
        for query in hinglish_queries:
            with self.subTest(query=query):
                mock_graph_stream.reset_mock()
                response = self.client.post("/api/chat", json={"message": query})
                self.assertEqual(response.status_code, 200, f"Failed on {query}: {response.text}")
                mock_graph_stream.assert_not_called()

    @patch("main.app_graph.stream")
    def test_category_k_emoji_minimal_input_bypasses_graph(self, mock_graph_stream):
        """Category K (emoji minimal input) must evaluate deterministically without invoking LangGraph."""
        emoji_queries = ["👋", "🙏"]
        for query in emoji_queries:
            with self.subTest(query=query):
                mock_graph_stream.reset_mock()
                response = self.client.post("/api/chat", json={"message": query})
                self.assertEqual(response.status_code, 200, f"Failed on {query}: {response.text}")
                mock_graph_stream.assert_not_called()

    @patch("main.app_graph.stream")
    def test_complex_financial_queries_invoke_graph(self, mock_graph_stream):
        """General financial queries must route to LangGraph StateGraph execution."""
        mock_graph_stream.return_value = iter([
            {"router": {"routing_decision": "market_data"}},
            {"market_data": {"draft_answer": "Reliance is trading at 2950 INR", "final_answer": "Reliance is trading at 2950 INR"}}
        ])
        
        response = self.client.post("/api/chat", json={"message": "What is the stock price of Reliance?"})
        self.assertEqual(response.status_code, 200)
        mock_graph_stream.assert_called_once()

    @patch("main.app_graph.stream")
    def test_bare_year_in_factual_question_must_invoke_graph(self, mock_graph_stream):
        """
        REGRESSION TEST — fast-path false positive (found via eval_trap_questions.py).

        Problem shape: a real factual question contains an isolated year (e.g. "2020")
        or other bare number with NO arithmetic operator. The fast-path gate must NOT
        intercept it and return a fabricated bare number.

        Correct behaviour: query reaches LangGraph (mock_graph_stream is called) so the
        graph can answer properly or abstain safely.

        Failure mode: fast-path returns is_math=True, graph is never called, the system
        fabricates a confident number for a fictional company — a hallucination-adjacent
        bug. This is the exact shape caught in eval_trap_questions.py that Category L
        coverage previously did not include.
        """
        mock_graph_stream.return_value = iter([
            {"router": {"routing_decision": "graph_rag"}},
            {"answer_generation": {
                "draft_answer": "No information available about Cyberdyne Systems.",
                "final_answer": "No information available about Cyberdyne Systems."
            }}
        ])

        # Original failing case: fictional company + bare year, no operator
        bare_year_queries = [
            "What was the total gross merchandise volume of Cyberdyne Systems in 2020?",
            "What was Apple's revenue in 2024?",
            "How much did Reliance earn in FY2023?",
            "What was HDFC Bank's net profit in Q3 2022?",
        ]
        for query in bare_year_queries:
            with self.subTest(query=query):
                mock_graph_stream.reset_mock()
                mock_graph_stream.return_value = iter([
                    {"router": {"routing_decision": "graph_rag"}},
                    {"answer_generation": {
                        "draft_answer": "No information available.",
                        "final_answer": "No information available."
                    }}
                ])
                response = self.client.post("/api/chat", json={"message": query})
                self.assertEqual(response.status_code, 200,
                                 f"Failed on {query}: {response.text}")
                mock_graph_stream.assert_called_once(), (
                    f"REGRESSION: factual query with bare year was caught by the "
                    f"fast-path gate instead of reaching the graph.\\n"
                    f"  Query: {query!r}\\n"
                    f"  This means the system may have returned a fabricated number "
                    f"with no LLM/RAG validation."
                )

if __name__ == "__main__":
    unittest.main()

