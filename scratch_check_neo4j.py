from core.db import kg
import json

results = kg.query("MATCH (c:PersonalChunk) RETURN c.user_id, c.document_id, c.conversation_id LIMIT 5")
print(json.dumps(results, indent=2))
