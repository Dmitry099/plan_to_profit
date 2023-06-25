from os import environ, path, getenv
from dotenv import load_dotenv

base_dir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(base_dir, ".env"))

# App settings
SECRET_KEY = environ.get("SECRET_KEY")
CLIENTS_PER_PAGE = int(environ.get("CLIENTS_PER_PAGE", "3"))
PLACES_PER_PAGE = int(getenv("PLACES_PER_PAGE", "3"))

# DB Settings
SQLALCHEMY_DATABASE_URI = "sqlite:///" + path.join(base_dir, "app.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Mail Settings
MAIL_SERVER = environ.get("MAIL_SERVER")
MAIL_PORT = environ.get("MAIL_PORT")
MAIL_USE_TLS = int(environ.get("MAIL_USE_TLS"))
MAIL_USERNAME = environ.get("MAIL_USERNAME")
MAIL_PASSWORD = environ.get("MAIL_PASSWORD")
ADMINS = environ.get("ADMINS")
