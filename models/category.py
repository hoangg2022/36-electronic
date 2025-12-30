# models/category.py
from .database import get_db_connection, close_db_connection
import logging

logger = logging.getLogger(__name__)

class Category:
    @staticmethod
    def get_all():
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT id, name, image_url FROM categories")
            categories = cursor.fetchall()
            close_db_connection(db, cursor)
            return categories
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách danh mục: {e}")
            return None