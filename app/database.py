import psycopg2
from psycopg2 import OperationalError
from app.config import Config

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )
        return conn
    except OperationalError:
        # Raise a custom error for Flask to catch
        raise ConnectionError("⚠️ Unable to connect to Wamie_Tech's Servers. Please check your internet or try again later.")
