from flask import Blueprint, request, jsonify, session
from models.review import ReviewModel
from config import logger

review_bp = Blueprint('review', __name__)

@review_bp.route('/api/reviews/add', methods=['POST'])
def add_review():
    if 'user_id' not in session:
        logger.warning("Thử thêm đánh giá không được phép")
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập để đánh giá'}), 401
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        comment = data.get('comment')
        rating = data.get('rating')
        success, message = ReviewModel.add_review(session['user_id'], product_id, comment, rating)
        if success:
            logger.info(f"Đánh giá được thêm cho sản phẩm {product_id} bởi người dùng {session['user_id']}")
            return jsonify({'success': True, 'message': 'Đánh giá đã được gửi thành công'}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
    except (ValueError, TypeError) as e:
        logger.error(f"Dữ liệu không hợp lệ trong add_review: {str(e)}")
        return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400