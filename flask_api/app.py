"""
Flask entrypoint for Oregon Dark Sky Dashboard.
"""
from flask import Flask
from routes import register_routes

def create_app():
    """Create and configure the Flask application."""
    # Create the Flask application
    app = Flask(__name__)
    # Configure the application and register routes
    register_routes(app)
    return app

# Run the app if this file is executed directly
if __name__ == "__main__":
    # Create the Flask application
    app = create_app()
    # Run the Flask development server
    app.run(debug=True)
