# app.py or relevant file
from flask import Blueprint, request, jsonify, session
from models.website_review import WebsiteReview  # Adjust import path
import logging
import mysql.connector

website_bp = Blueprint('website', __name__)
logger = logging.getLogger(__name__)

@website_bp.route('/api/website-reviews', methods=['GET'])
def get_website_reviews():
    """Fetch all website reviews."""
    reviews = WebsiteReview.get_all_reviews()
    return jsonify({'reviews': reviews})

@website_bp.route('/api/website-reviews', methods=['POST'])
def add_website_review():
    """Submit a new website review.
    Requires the user to be logged in to get user_id from session."""
    # Get user_id from session (assuming Flask-Login or session is configured)
    user_id = session.get('user_id')  # Adjust based on your session key

    if not user_id:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập để gửi đánh giá.'}), 401

    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')

    if rating is None or not isinstance(rating, int):
        return jsonify({'success': False, 'message': 'Rating is required and must be an integer.'}), 400
    if not comment or not comment.strip():
        return jsonify({'success': False, 'message': 'Comment is required.'}), 400

    if WebsiteReview.create(user_id, rating, comment):
        return jsonify({'success': True, 'message': 'Đánh giá đã được gửi thành công!'})
    else:
        return jsonify({'success': False, 'message': 'Lỗi khi gửi đánh giá.'}), 500


# Example /api/check_login endpoint (if not already defined)
@website_bp.route('/api/check_login', methods=['GET'])
def check_login():
    user_id = session.get('user_id')
    if user_id:
        from models.database import get_db_connection, close_db_connection
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT full_name FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            return jsonify({'logged_in': True, 'user_id': user_id, 'full_name': user['full_name'] if user else 'User'})
        except mysql.connector.Error as err:
            logger.error(f"Error checking login: {err}")
            return jsonify({'logged_in': False}), 500
        finally:
            close_db_connection(db, cursor)
    return jsonify({'logged_in': False})