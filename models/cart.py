# models/cart.py
from .database import get_db_connection, close_db_connection
import logging

logger = logging.getLogger(__name__)

class Cart:
    @staticmethod
    def add(user_id, product_id, quantity):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantity = quantity + %s",
                (user_id, product_id, quantity, quantity)
            )
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi thêm vào giỏ hàng: {e}")
            return False

    @staticmethod
    def get_by_user_id(user_id):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                SELECT c.product_id, p.name, p.discounted_price, c.quantity, p.image_url
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = %s
            """, (user_id,))
            cart_items = cursor.fetchall()
            close_db_connection(db, cursor)
            return cart_items
        except Exception as e:
            logger.error(f"Lỗi khi lấy giỏ hàng cho user_id {user_id}: {e}")
            return None

    @staticmethod
    def remove(user_id, product_id):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
                (user_id, product_id)
            )
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa sản phẩm khỏi giỏ hàng: {e}")
            return False