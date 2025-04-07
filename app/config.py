import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://root:(Lugovaya34)@localhost/hr')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'c220ad2e00bc2136562ff19040718452a949c08d58cc84e6071f8184394f71b5')