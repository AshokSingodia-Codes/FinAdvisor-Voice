import unittest
import json
import uuid
from sqlalchemy import text
from core.memory import (
    init_db,
    get_db_connection,
    create_conversation,
    get_conversation,
    get_conversation_continuity,
    save_conversation_continuity,
    delete_conversation,
    create_user,
    _get_utc_now,
)
from core.auth import hash_password

class TestDatabaseMigrationSafety(unittest.TestCase):
    def setUp(self):
        # Create a real user so FK constraint on conversations.user_id is satisfied
        _email = f"test_migration_{uuid.uuid4().hex[:8]}@test.com"
        user_rec = create_user(_email, hash_password("Migr@tion1!"))
        self.user_id = user_rec["id"]
        self.conv_id = f"legacy_conv_{uuid.uuid4().hex[:8]}"

        # 1. Create a base conversation
        create_conversation(title="Legacy Chat", user_id=self.user_id, conversation_id=self.conv_id)

        # 2. Simulate a legacy pre-migration row where active_entities & conversation_topic are NULL
        with get_db_connection() as conn:
            conn.execute(
                text("""
                    UPDATE conversation_memory
                    SET summary = :summary, facts = :facts, active_entities = NULL, conversation_topic = NULL, updated_at = :now
                    WHERE conversation_id = :id
                """),
                {
                    "id": self.conv_id,
                    "summary": "Existing conversation summary from before migration",
                    "facts": json.dumps({"risk_profile": "moderate", "annual_income": "15L"}),
                    "now": _get_utc_now(),
                },
            )
            conn.commit()

    def tearDown(self):
        delete_conversation(self.conv_id, user_id=self.user_id)
        # Clean up test user
        with get_db_connection() as conn:
            conn.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": self.user_id})
            conn.commit()

    def test_null_tolerant_get_conversation(self):
        """Confirm get_conversation safely handles NULL active_entities & conversation_topic without crashing."""
        conv = get_conversation(self.conv_id, user_id=self.user_id)
        self.assertIsNotNone(conv)
        self.assertEqual(conv["active_entities"], {}, "NULL active_entities must default to empty dict")
        self.assertEqual(conv["conversation_topic"], "", "NULL conversation_topic must default to empty string")
        self.assertEqual(conv["summary"], "Existing conversation summary from before migration")
        self.assertEqual(conv["facts"].get("risk_profile"), "moderate")

    def test_null_tolerant_get_conversation_continuity(self):
        """Confirm get_conversation_continuity safely handles legacy NULL rows."""
        continuity = get_conversation_continuity(self.conv_id, user_id=self.user_id)
        self.assertEqual(continuity["active_entities"], {})
        self.assertEqual(continuity["conversation_topic"], "")

    def test_idempotent_init_db_rerun(self):
        """Confirm running init_db() multiple times is completely idempotent and does not fail on existing columns."""
        try:
            init_db()
            init_db()
        except Exception as e:
            self.fail(f"init_db() raised unexpected exception on rerun: {e}")

    def test_update_legacy_row_preserves_facts_and_summary(self):
        """Confirm updating continuity on a legacy row updates new columns while preserving old facts/summary."""
        new_entities = {"company": "Infosys", "ticker": "INFY.NS"}
        success = save_conversation_continuity(
            self.conv_id,
            active_entities=new_entities,
            conversation_topic="Infosys Analysis",
            user_id=self.user_id
        )
        self.assertTrue(success)

        # Re-fetch and verify both old and new data coexist correctly
        conv = get_conversation(self.conv_id, user_id=self.user_id)
        self.assertEqual(conv["active_entities"], new_entities)
        self.assertEqual(conv["conversation_topic"], "Infosys Analysis")
        self.assertEqual(conv["summary"], "Existing conversation summary from before migration")
        self.assertEqual(conv["facts"].get("annual_income"), "15L")

if __name__ == "__main__":
    unittest.main()
