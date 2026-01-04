import os
from dotenv import load_dotenv

def load_env():
    if os.getenv("ENVIRONMENT") != "production":
        try:
            load_dotenv("src/.env.local")
            print("Loaded .env.local for non-production environment.")
            print("Environment variables:")
            print("Database URL:", os.getenv("DATABASE_URL"))
        except RuntimeError as e:
            print("Error loading .env.local:", e)
            raise e
    else:
        try:
            load_dotenv("src/.env")
            print("Loaded .env for production environment.")
        except RuntimeError as e:
            print("Error loading .env:", e)
            raise e