
import unittest
import uuid
from unittest.mock import patch, MagicMock
from graph.state import AgentState
from nodes.router import route_question, Route
from core.memory import (
    create_conversation,
    delete_conversation,
    save_conversation_continuity,
    get_conversation_continuity,
    create_user,
    get_db_connection,
)
from sqlalchemy import text
from core.auth import hash_password

class TestConversationalContinuity(unittest.TestCase):
    def setUp(self):
        # Create unique test users so FK constraint on conversations.user_id is satisfied
        self.user_a = f"test_continuity_a_{uuid.uuid4().hex[:8]}"
        self.user_b = f"test_continuity_b_{uuid.uuid4().hex[:8]}"
        user_a_rec = create_user(f"{self.user_a}@test.com", hash_password("Test1234!"))
        user_b_rec = create_user(f"{self.user_b}@test.com", hash_password("Test1234!"))
        # Use the real UUIDs assigned by create_user for FK compliance
        self.user_a = user_a_rec["id"]
        self.user_b = user_b_rec["id"]
        self.conv_a = create_conversation(title="Conv A", user_id=self.user_a)
        self.conv_b = create_conversation(title="Conv B", user_id=self.user_b)

    def tearDown(self):
        delete_conversation(self.conv_a, user_id=self.user_a)
        delete_conversation(self.conv_b, user_id=self.user_b)
        # Clean up test users
        with get_db_connection() as conn:
            conn.execute(text("DELETE FROM users WHERE id IN (:a, :b)"),
                         {"a": self.user_a, "b": self.user_b})
            conn.commit()

    @patch("nodes.router.router_chain")
    def test_case_1_pronoun_resolution(self, mock_router_chain):
        """Case 1: Pronoun resolution ('what about its revenue') resolves using active_entities."""
        # Setup initial state with active entity
        initial_entities = {"company": "Reliance Industries", "ticker": "RELIANCE.NS"}
        save_conversation_continuity(self.conv_a, initial_entities, "Reliance Financials", user_id=self.user_a)

        mock_router_chain.invoke.return_value = Route(
            decision="hybrid_search",
            resolved_query="What was Reliance Industries' total revenue in FY 2024?",
            is_topic_change=False,
            extracted_entities={"metric": "revenue"},
            conversation_topic="Reliance Financials"
        )

        state: AgentState = {
            "original_question": "what about its revenue?",
            "conversation_id": self.conv_a,
            "user_id": self.user_a,
            "memory_context": "User: What is Reliance's P/E?\nAssistant: 28.5"
        }

        result = route_question(state)

        # Assert resolved_query resolved the pronoun 'its'
        self.assertIn("Reliance", result["resolved_query"])
        self.assertEqual(result["active_entities"].get("company"), "Reliance Industries")
        self.assertEqual(result["active_entities"].get("metric"), "revenue")
        self.assertEqual(result["routing_decision"], "hybrid_search")

        # Verify DB persistence
        db_continuity = get_conversation_continuity(self.conv_a, user_id=self.user_a)
        self.assertEqual(db_continuity["active_entities"].get("company"), "Reliance Industries")

    @patch("nodes.router.router_chain")
    def test_case_2_implicit_followup(self, mock_router_chain):
        """Case 2: Implicit follow-up ('and this one's return') resolves mutual fund entity."""
        initial_entities = {"mutual_fund": "SBI Small Cap Fund", "metric": "NAV"}
        save_conversation_continuity(self.conv_a, initial_entities, "SBI Small Cap Performance", user_id=self.user_a)

        mock_router_chain.invoke.return_value = Route(
            decision="calculation",
            resolved_query="What is the 3-year return of SBI Small Cap Fund?",
            is_topic_change=False,
            extracted_entities={"metric": "3-year return"},
            conversation_topic="SBI Small Cap Performance"
        )

        state: AgentState = {
            "original_question": "and this one's return?",
            "conversation_id": self.conv_a,
            "user_id": self.user_a,
            "memory_context": "User: Tell me about SBI Small Cap Fund NAV.\nAssistant: NAV is 165.2 INR"
        }

        result = route_question(state)

        self.assertIn("SBI Small Cap Fund", result["resolved_query"])
        self.assertEqual(result["active_entities"].get("mutual_fund"), "SBI Small Cap Fund")
        self.assertEqual(result["active_entities"].get("metric"), "3-year return")

    @patch("nodes.router.router_chain")
    def test_case_3_topic_change_reset(self, mock_router_chain):
        """Case 3 (ADVERSARIAL): Topic change MUST reset active entities and NOT poison unrelated questions."""
        # Prior turn was entity-heavy on Reliance
        initial_entities = {"company": "Reliance Industries", "ticker": "RELIANCE.NS", "metric": "P/E ratio"}
        save_conversation_continuity(self.conv_a, initial_entities, "Reliance Stock Analysis", user_id=self.user_a)

        # Unrelated subsequent question: compound interest formula
        mock_router_chain.invoke.return_value = Route(
            decision="calculation",
            resolved_query="How do I calculate compound interest?",
            is_topic_change=True,
            extracted_entities={},
            conversation_topic="Compound Interest Formula"
        )

        state: AgentState = {
            "original_question": "how do I calculate compound interest?",
            "conversation_id": self.conv_a,
            "user_id": self.user_a,
            "memory_context": "User: What is Reliance's P/E ratio?\nAssistant: 28.5"
        }

        result = route_question(state)

        # ADVERSARIAL ASSERTIONS:
        # 1. Reliance MUST NOT appear in the resolved query
        self.assertNotIn("Reliance", result["resolved_query"])
        self.assertNotIn("RELIANCE.NS", result["resolved_query"])
        # 2. active_entities MUST NOT contain Reliance
        self.assertNotIn("company", result["active_entities"])
        self.assertNotIn("ticker", result["active_entities"])
        self.assertEqual(result["active_entities"], {})
        # 3. Topic updated away from Reliance
        self.assertEqual(result["conversation_topic"], "Compound Interest Formula")

        # 4. DB store verified reset
        db_continuity = get_conversation_continuity(self.conv_a, user_id=self.user_a)
        self.assertNotIn("company", db_continuity["active_entities"])

    def test_case_4_cross_session_isolation(self):
        """Case 4: Cross-session / cross-user isolation: entities in Conv A never leak into Conv B."""
        # Set entities in User A's conversation
        save_conversation_continuity(
            self.conv_a,
            {"company": "Tata Consultancy Services", "ticker": "TCS.NS"},
            "TCS Overview",
            user_id=self.user_a
        )

        # Retrieve for User B in Conv B
        continuity_b = get_conversation_continuity(self.conv_b, user_id=self.user_b)
        self.assertEqual(continuity_b["active_entities"], {})
        self.assertEqual(continuity_b["conversation_topic"], "")

        # Try unauthorized access by User B into Conv A
        unauthorized = get_conversation_continuity(self.conv_a, user_id=self.user_b)
        self.assertEqual(unauthorized["active_entities"], {})

if __name__ == "__main__":
    unittest.main()
