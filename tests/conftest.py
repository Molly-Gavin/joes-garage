import os
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

os.environ["GARAGE_PASSWORD"] = "test-password"
os.environ["GARAGE_SECRET"] = "test-secret-key-for-tests-only"

fake_identify = types.ModuleType("identify")
fake_identify.identify_make = lambda photo_path: "TestMake"
sys.modules["identify"] = fake_identify