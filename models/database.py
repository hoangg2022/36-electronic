import mysql.connector
import logging
import os

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        # Railway cung cấp các biến môi trường này tự động
        return mysql.connector.connect(
            host=os.environ.get('MYSQLHOST', 'localhost'),
            user=os.environ.get('MYSQLUSER', 'root'),
            password=os.environ.get('MYSQLPASSWORD', '123456'),
            database=os.environ.get('MYSQLDATABASE', 'railway'), # Railway thường đặt tên mặc định là railway
            port=int(os.environ.get('MYSQLPORT', 3306))
        )
    except mysql.connector.Error as err:
        logger.error(f"Lỗi kết nối cơ sở dữ liệu: {err}")
        raise

def close_db_connection(db, cursor=None):
    if cursor:
        cursor.close()
    if db:
        db.close()