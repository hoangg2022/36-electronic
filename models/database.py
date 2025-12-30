import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        # Lấy đường dẫn Database từ biến môi trường của Render
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            # Fallback cho chạy local (nếu bạn muốn test máy nhà thì điền link postgres local vào đây)
            # Ví dụ: 'postgresql://user:pass@localhost/dbname'
            raise ValueError("DATABASE_URL chưa được thiết lập trong Environment Variables!")
            
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as err:
        logger.error(f"Lỗi kết nối cơ sở dữ liệu: {err}")
        raise

def close_db_connection(db, cursor=None):
    if cursor:
        cursor.close()
    if db:
        db.close()