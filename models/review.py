# models/review.py
from .database import get_db_connection, close_db_connection
import logging

logger = logging.getLogger(__name__)

class Review:
    @staticmethod
    def get_all():
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                SELECT r.id, r.user_id, r.product_id, r.comment, r.rating, u.full_name
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                ORDER BY r.created_at DESC
            """)
            reviews = cursor.fetchall()
            close_db_connection(db, cursor)
            return reviews
        except Exception as e:
            logger.error(f"Error fetching all reviews: {e}")
            return None

    @staticmethod
    def get_by_product(product_id):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                SELECT r.id, r.user_id, r.product_id, r.comment, r.rating, u.full_name
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.product_id = %s
                ORDER BY r.created_at DESC
            """, (product_id,))
            reviews = cursor.fetchall()
            close_db_connection(db, cursor)
            return reviews
        except Exception as e:
            logger.error(f"Error fetching reviews for product {product_id}: {e}")
            return None

    @staticmethod
    def create(user_id, product_id, comment, rating):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO reviews (user_id, product_id, comment, rating, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (user_id, product_id, comment, rating))
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Error creating review: {e}")
            db.rollback()
            close_db_connection(db, cursor)
            return False