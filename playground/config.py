import os
from dotenv import load_dotenv

# Load .env.local file and specify relative path
load_dotenv(dotenv_path="./playground/.env.local") 

class BaseConfig():
    DEBUG = False
    SECRET_KEY = "mysecretkey"

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLITE_URI", "")

class ProductionConfig(BaseConfig):
    pass