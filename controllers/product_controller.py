# controllers/product_controller.py
from flask import Blueprint, request, jsonify, render_template, session
from models.product import Product
from models.category import Category
from models.review import Review
import logging

product_bp = Blueprint('product', __name__)
logger = logging.getLogger(__name__)

@product_bp.route('/products')
def products():
    category_id = request.args.get('category_id')
    return render_template('products/products.html', category_id=category_id)

@product_bp.route('/product-detail')
def product_detail():
    product_id = request.args.get('id')
    return render_template('products/product-detail.html', product_id=product_id)

@product_bp.route('/api/categories')
def get_categories():
    categories = Category.get_all()
    if categories:
        return jsonify([{"id": row[0], "name": row[1], "image_url": row[2]} for row in categories])
    return jsonify({'success': False, 'message': 'Lỗi khi lấy danh mục'}), 500

@product_bp.route('/api/products', methods=['GET'])
def get_products():
    try:
        category_id = request.args.get('category_id')
        search_query = request.args.get('search')
        discount = request.args.get('discount', 'false') == 'true'
        sort = request.args.get('sort')
        price_range = request.args.get('price_range')
        products = Product.get_all(category_id, search_query, discount, sort, price_range)
        if products:
            exchange_rate = 25000
            result = [
                {
                    "id": row[0],
                    "category_id": row[1],
                    "name": row[2],
                    "description": row[3],
                    "price": float(row[4]) * exchange_rate if row[4] is not None else 0.0,
                    "discount_percentage": float(row[5]) if row[5] is not None else 0.0,
                    "discounted_price": float(row[6]) * exchange_rate if row[6] is not None else 0.0,
                    "image_url": row[7],
                    "sold": row[8] if row[8] is not None else 0,
                    "stock_quantity": row[9] if row[9] is not None else 0,
                    "avg_rating": float(row[10]) if row[10] is not None else 0.0,
                    "review_count": row[11] if row[11] is not None else 0,
                    "student_price": float(row[6]) * 0.95 * exchange_rate if row[6] is not None else 0.0,
                    "installment": "0% qua thẻ tín dụng kỳ hạn 3-6..."
                } for row in products
            ]
            return jsonify(result)
        return jsonify([])
    except Exception as e:
        logger.error(f"Lỗi khi lấy sản phẩm: {e}")
        return jsonify({'success': False, 'message': 'Lỗi, vui lòng thử lại sau'}), 500

@product_bp.route('/api/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.get_by_id(product_id)
        if product:
            exchange_rate = 25000
            reviews = Review.get_by_product(product_id)
            review_list = []
            if reviews:
                review_list = [
                    {
                        'rating': row[4],
                        'comment': row[3],
                        'user_name': row[5]
                    } for row in reviews
                ]
            return jsonify({
                'success': True,
                'id': product[0],
                'category_id': product[1],
                'name': product[2],
                'description': product[3],
                'price': float(product[4]) * exchange_rate if product[4] is not None else 0.0,
                'discount_percentage': float(product[5]) if product[5] is not None else 0.0,
                'discounted_price': float(product[6]) * exchange_rate if product[6] is not None else 0.0,
                'image_url': product[7],
                'sold': product[8] if product[8] is not None else 0,
                'stock_quantity': product[9] if product[9] is not None else 0,
                'avg_rating': float(product[10]) if product[10] is not None else 0.0,
                'review_count': product[11] if product[11] is not None else 0,
                'student_price': float(product[6]) * 0.95 * exchange_rate if product[6] is not None else 0.0,
                'installment': "0% qua thẻ tín dụng kỳ hạn 3-6...",
                'reviews': review_list
            })
        logger.error(f"Product not found: product_id={product_id}")
        return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại'}), 404
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        return jsonify({'success': False, 'message': 'Lỗi, vui lòng thử lại sau'}), 500

@product_bp.route('/api/reviews/add', methods=['POST'])
def add_review():
    if 'user_id' not in session:
        logger.warning("Thử thêm đánh giá không được phép")
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập để đánh giá'}), 401
    try:
        data = request.get_json()
        product_id = int(data.get('product_id'))
        comment = data.get('comment')
        rating = int(data.get('rating'))
        if not all([product_id, comment, rating]):
            logger.error("Thiếu thông tin đánh giá")
            return jsonify({'success': False, 'message': 'Thiếu thông tin đánh giá'}), 400
        if rating < 1 or rating > 5:
            logger.error(f"Giá trị đánh giá không hợp lệ: {rating}")
            return jsonify({'success': False, 'message': 'Điểm đánh giá phải từ 1 đến 5'}), 400
        if len(comment.strip()) == 0:
            logger.error("Bình luận trống trong đánh giá")
            return jsonify({'success': False, 'message': 'Bình luận không được để trống'}), 400
        if Review.create(session['user_id'], product_id, comment, rating):
            logger.info(f"Đánh giá được thêm cho sản phẩm {product_id} bởi người dùng {session['user_id']}")
            return jsonify({'success': True, 'message': 'Đánh giá đã được gửi thành công'})
        return jsonify({'success': False, 'message': 'Lỗi khi gửi đánh giá'}), 500
    except Exception as e:
        logger.error(f"Lỗi khi thêm đánh giá: {e}")
        return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400