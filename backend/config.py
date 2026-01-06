import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @property
    def database_url(self):
        return os.getenv('DB_URL')