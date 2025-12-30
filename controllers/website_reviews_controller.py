from flask import Blueprint, request, jsonify, session
from models.website_review import WebsiteReview
from models.database import get_db_connection, close_db_connection
import logging

# --- ĐÃ XÓA DÒNG IMPORT MYSQL ---

website_bp = Blueprint('website', __name__)
logger = logging.getLogger(__name__)

@website_bp.route('/api/website-reviews', methods=['GET'])
def get_website_reviews():
    """Fetch all website reviews."""
    try:
        reviews = WebsiteReview.get_all_reviews()
        return jsonify({'reviews': reviews})
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        return jsonify({'reviews': []}), 500

@website_bp.route('/api/website-reviews', methods=['POST'])
def add_website_review():
    """Submit a new website review."""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập để gửi đánh giá.'}), 401

    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')

    if rating is None:
        return jsonify({'success': False, 'message': 'Rating is required.'}), 400
    
    try:
        rating = int(rating)
    except ValueError:
        return jsonify({'success': False, 'message': 'Rating must be an integer.'}), 400

    if not comment or not comment.strip():
        return jsonify({'success': False, 'message': 'Comment is required.'}), 400

    if WebsiteReview.create(user_id, rating, comment):
        return jsonify({'success': True, 'message': 'Đánh giá đã được gửi thành công!'})
    else:
        return jsonify({'success': False, 'message': 'Lỗi khi gửi đánh giá.'}), 500

@website_bp.route('/api/check_login', methods=['GET'])
def check_login():
    user_id = session.get('user_id')
    if user_id:
        try:
            db = get_db_connection()
            # Bỏ tham số dictionary=True vì PostgreSQL đã dùng RealDictCursor mặc định
            cursor = db.cursor()
            
            cursor.execute("SELECT full_name FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            close_db_connection(db, cursor)
            return jsonify({'logged_in': True, 'user_id': user_id, 'full_name': user['full_name'] if user else 'User'})
        except Exception as err:
            logger.error(f"Error checking login: {err}")
            return jsonify({'logged_in': False}), 500
    return jsonify({'logged_in': False})