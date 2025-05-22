from flask import Flask
from models import db
from api import api
from config import Config
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app, db)
    app.register_blueprint(api)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
