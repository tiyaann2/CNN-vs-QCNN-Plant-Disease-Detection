from flask import Flask
from routes import register_routes

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
