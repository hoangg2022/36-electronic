from flask import Blueprint, request, session, jsonify
from models.database import get_db_connection, close_db_connection
import logging

cart_bp = Blueprint('cart', __name__)
logger = logging.getLogger(__name__)

# Lấy danh sách giỏ hàng từ CSDL
@cart_bp.route('/api/cart', methods=['GET'])
def get_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT c.product_id, c.quantity, p.name, p.price, p.image_url
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (session['user_id'],))
        rows = cursor.fetchall()

        items = [{
            'product_id': row[0],
            'quantity': row[1],
            'name': row[2],
            'price': float(row[3]) * 25000,  # tuỳ theo tỷ giá
            'image_url': row[4] or '/static/img/default_product.jpg',
            'selected': False
        } for row in rows]

        close_db_connection(db, cursor)
        return jsonify({'success': True, 'items': items})
    except Exception as e:
        logger.error(f"Lỗi khi lấy giỏ hàng: {e}")
        return jsonify({'success': False, 'message': 'Lỗi máy chủ'}), 500

# Thêm sản phẩm vào giỏ hàng (hoặc cập nhật số lượng)
@cart_bp.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401

    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))

        if not product_id or quantity < 1:
            return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400

        db = get_db_connection()
        cursor = db.cursor()

        # Kiểm tra số lượng tồn kho
        cursor.execute("SELECT stock_quantity FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if not product or product[0] < quantity:
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại hoặc không đủ hàng'}), 400

        # Kiểm tra đã có trong giỏ chưa
        cursor.execute("SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s",
                       (session['user_id'], product_id))
        existing = cursor.fetchone()

        if existing:
            new_quantity = existing[0] + quantity
            if product[0] < new_quantity:
                close_db_connection(db, cursor)
                return jsonify({'success': False, 'message': 'Vượt quá số lượng tồn kho'}), 400

            cursor.execute("UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
                           (new_quantity, session['user_id'], product_id))
        else:
            cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                           (session['user_id'], product_id, quantity))

        db.commit()
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'message': 'Đã thêm vào giỏ hàng'})
    except Exception as e:
        logger.error(f"Lỗi khi thêm sản phẩm: {e}")
        return jsonify({'success': False, 'message': 'Lỗi máy chủ'}), 500

# Xoá sản phẩm khỏi giỏ hàng
@cart_bp.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401

    try:
        data = request.get_json()
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({'success': False, 'message': 'Thiếu product_id'}), 400

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s",
                       (session['user_id'], product_id))

        db.commit()
        close_db_connection(db, cursor)

        return jsonify({'success': True, 'message': 'Đã xoá khỏi giỏ hàng'})
    except Exception as e:
        logger.error(f"Lỗi khi xoá khỏi giỏ: {e}")
        return jsonify({'success': False, 'message': 'Lỗi máy chủ'}), 500

# Thanh toán

