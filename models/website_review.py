# models/website_review.py
import mysql.connector
from datetime import datetime, timedelta
from models.database import get_db_connection, close_db_connection
import logging

logger = logging.getLogger(__name__)

class WebsiteReview:
    @staticmethod
    def create(user_id, rating, comment):
        """Create a new website review."""
        db = get_db_connection()
        cursor = db.cursor()
        try:
            if not 1 <= rating <= 5:
                logger.error("Invalid rating: Must be between 1 and 5")
                return False
            if not comment or not comment.strip():
                logger.error("Comment cannot be empty")
                return False

            # Check for duplicate within the last 1 second
            cursor.execute(
                "SELECT created_at FROM website_reviews WHERE user_id = %s AND rating = %s AND comment = %s ORDER BY created_at DESC LIMIT 1",
                (user_id, rating, comment)
            )
            last_review = cursor.fetchone()
            if last_review and datetime.utcnow() - last_review[0].replace(tzinfo=None) < timedelta(seconds=1):
                logger.warning("Duplicate review detected, skipping insertion")
                return True  # Return success to avoid client retry

            query = "INSERT INTO website_reviews (user_id, rating, comment) VALUES (%s, %s, %s)"
            cursor.execute(query, (user_id, rating, comment))
            db.commit()
            logger.info(f"Review created for user_id: {user_id} with rating: {rating}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"Error creating review: {err}")
            db.rollback()
            return False
        finally:
            close_db_connection(db, cursor)

    @staticmethod
    def get_all_reviews():
        """Fetch all website reviews with user full_name."""
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            query = """
                SELECT wr.id, wr.rating, wr.comment, wr.created_at, u.full_name
                FROM website_reviews wr
                LEFT JOIN users u ON wr.user_id = u.id
                ORDER BY wr.created_at DESC;
            """
            cursor.execute(query)
            reviews = cursor.fetchall()
            return [{
                'id': review['id'],
                'rating': review['rating'],
                'comment': review['comment'],
                'created_at': review['created_at'].isoformat() if review['created_at'] else None,
                'full_name': review['full_name'] or 'Ẩn danh'
            } for review in reviews]
        except mysql.connector.Error as err:
            logger.error(f"Error fetching reviews: {err}")
            return []
        finally:
            close_db_connection(db, cursor)