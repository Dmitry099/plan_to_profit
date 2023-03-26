from flask import Flask

# from flasgger import Swagger
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from plan_to_profit.routes import plan_to_profit


def create_app():
    app = Flask(__name__)
    # plan_to_profit.config['SWAGGER'] = {
    #     'title': 'Flask API Starter Kit',
    # }
    # swagger = Swagger(plan_to_profit)
    # ## Initialize Config
    app.config.from_pyfile("config.py")
    app.register_blueprint(plan_to_profit, url_prefix="/")
    return app


def connect_to_db(app):
    db = SQLAlchemy(app)
    Migrate(app, db)
    return db


if __name__ == "__main__":
    app = create_app()
    db = connect_to_db(app)
