# -*- coding: utf-8 -*-
import os

class Config:
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'mentorlink_db'
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres123'
    DB_OPTIONS = "-c client_encoding=UTF8"
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    SECRET_KEY = 'ta-cle-secrete-tres-longue-2026'
    JWT_SECRET_KEY = 'jwt-cle-secrete-2026'
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../frontend/assets/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

config = Config()
