import pathlib

p = pathlib.Path('tests/test_daily_snapshot_job.py')
content = p.read_text(encoding='utf-8')
content = content.replace(
    'code = "TEST_MF_NEAREST_001"',
    'import uuid\n    code = "TEST_MF_NEAREST_" + str(uuid.uuid4())[:8]'
)
p.write_text(content, encoding='utf-8')
print("Successfully patched test_daily_snapshot_job.py")
