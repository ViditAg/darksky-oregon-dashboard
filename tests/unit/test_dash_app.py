import unittest

class TestDashAppSmoke(unittest.TestCase):
    def test_app_import_and_create(self):
        """
        Smoke test: Import the Dash app and check if app can be created.
        """
        try:
            import dash_app.app
            app = dash_app.app.app if hasattr(dash_app.app, "app") else dash_app.app
            assert app is not None
        except Exception as e:
            self.fail(f"Dash app failed to import or create: {e}")

if __name__ == "__main__":
    unittest.main()
