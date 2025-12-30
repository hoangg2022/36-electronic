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
            
            # Sửa: last_review là dict nên dùng key 'created_at', không dùng index [0]
            if last_review:
                last_time = last_review['created_at']
                if datetime.utcnow() - last_time.replace(tzinfo=None) < timedelta(seconds=1):
                    logger.warning("Duplicate review detected, skipping insertion")
                    return True

            query = "INSERT INTO website_reviews (user_id, rating, comment) VALUES (%s, %s, %s)"
            cursor.execute(query, (user_id, rating, comment))
            db.commit()
            logger.info(f"Review created for user_id: {user_id} with rating: {rating}")
            return True
        except Exception as err:
            logger.error(f"Error creating review: {err}")
            db.rollback()
            return False
        finally:
            close_db_connection(db, cursor)

    @staticmethod
    def get_all_reviews():
        """Fetch all website reviews with user full_name."""
        db = get_db_connection()
        # Không truyền dictionary=True vì đã cấu hình RealDictCursor mặc định
        cursor = db.cursor()
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
        except Exception as err:
            logger.error(f"Error fetching reviews: {err}")
            return []
        finally:
            close_db_connection(db, cursor)