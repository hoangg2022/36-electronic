# models/database.py
import mysql.connector
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",  # Nên sử dụng biến môi trường trong production
            database="36_electronic_shop"
        )
    except mysql.connector.Error as err:
        logger.error(f"Lỗi kết nối cơ sở dữ liệu: {err}")
        raise

def close_db_connection(db, cursor=None):
    if cursor:
        cursor.close()
    if db:
        db.close()