"""
Unit test for Streamlit app.py
"""

import unittest

class TestStreamlitAppSmoke(unittest.TestCase):
    def test_app_import_and_run(self):
        """
        Smoke test: Import the Streamlit app and check if main function runs without error.
        """
        try:
            import streamlit_app.app
            if hasattr(streamlit_app.app, "main"):
                streamlit_app.app.main()
        except Exception as e:
            self.fail(f"Streamlit app failed to import or run: {e}")

if __name__ == "__main__":
    unittest.main()