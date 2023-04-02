import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_bootstrap import Bootstrap

from plan_to_profit.email import mail
from plan_to_profit.models import db, migrate, login
from plan_to_profit.routes import plan_to_profit

bootstrap = Bootstrap()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    app.register_blueprint(plan_to_profit, url_prefix="/")
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()

    if not app.debug:
        mail.init_app(app)
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/plan_to_profit.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s "
                "[in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Plan to profit started")
