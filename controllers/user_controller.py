# controllers/user_controller.py
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from models.user import User
from models.order import Order
from datetime import datetime
import logging
from models.database import get_db_connection, close_db_connection

user_bp = Blueprint('user', __name__)
logger = logging.getLogger(__name__)

@user_bp.route('/user')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('user/profile.html')

@user_bp.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('user/cart.html')

@user_bp.route('/api/check_login')
def check_login():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'full_name': session.get('full_name', 'Người dùng')})
    return jsonify({'logged_in': False})

@user_bp.route('/api/user')
def get_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Người dùng chưa đăng nhập'}), 401

    user = User.get_by_id(session['user_id'])
    if user:
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[3],
            'birth_date': str(user[4])
        }
        return jsonify(user_data)
    logger.warning(f"Không tìm thấy người dùng với user_id: {session['user_id']}")
    return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404

@user_bp.route('/api/update_user', methods=['POST'])
def update_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Người dùng chưa đăng nhập'}), 401

    try:
        data = request.get_json()
        full_name = data.get('full_name')
        email = data.get('email')
        birth_date = data.get('birth_date')
        password = data.get('password')

        if not full_name or not email or not birth_date:
            logger.error("Thiếu các trường bắt buộc trong yêu cầu update_user")
            return jsonify({'success': False, 'message': 'Thiếu các trường bắt buộc'}), 400

        try:
            datetime.strptime(birth_date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Định dạng ngày sinh không hợp lệ: {birth_date}")
            return jsonify({'success': False, 'message': 'Định dạng ngày sinh không hợp lệ. Sử dụng YYYY-MM-DD.'}), 400

        if User.check_email_exists(email, session['user_id']):
            logger.warning(f"Email đã tồn tại: {email}")
            return jsonify({'success': False, 'message': 'Email đã tồn tại'}), 400

        if User.update(session['user_id'], full_name, email, birth_date, password):
            session['full_name'] = full_name
            logger.info(f"Người dùng {session['user_id']} cập nhật hồ sơ thành công")
            return jsonify({'success': True, 'message': 'Thông tin người dùng được cập nhật thành công'})
        return jsonify({'success': False, 'message': 'Không thể cập nhật thông tin người dùng'}), 500
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật người dùng: {e}")
        return jsonify({'success': False, 'message': 'Lỗi, vui lòng thử lại sau'}), 500

@user_bp.route('/api/user/profile')
def get_user_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Người dùng chưa đăng nhập'}), 401

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "SELECT username, email, full_name, birth_date FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        if not user:
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404

        user_info = {
            'username': user[0],
            'email': user[1],
            'full_name': user[2],
            'birth_date': str(user[3])
        }

        cursor.execute(
            "SELECT COUNT(*) FROM cart WHERE user_id = %s",
            (session['user_id'],)
        )
        cart_count = cursor.fetchone()[0]

        cursor.execute(
            "SELECT SUM(quantity) FROM order_activities WHERE user_id = %s",
            (session['user_id'],)
        )
        purchased_count = cursor.fetchone()[0] or 0

        orders = Order.get_by_user_id(session['user_id'])
        orders_data = [{
            'order_id': order[0],
            'product_id': order[1],
            'quantity': order[2],
            'total_price': float(order[3]),
            'status': order[4],
            'date': order[5].strftime('%Y-%m-%d %H:%M')
        } for order in orders] if orders else []

        cursor.execute(
            "SELECT COALESCE(SUM(total_price), 0) FROM order_activities WHERE user_id = %s",
            (session['user_id'],)
        )
        total_spent = cursor.fetchone()[0]

        profile_data = {
            'user_info': user_info,
            'cart_count': cart_count,
            'purchased_count': purchased_count,
            'orders': orders_data,
            'total_spent': float(total_spent)
        }

        close_db_connection(db, cursor)
        return jsonify({'success': True, 'data': profile_data})
    except Exception as e:
        logger.error(f"Lỗi khi lấy hồ sơ người dùng: {e}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Lỗi, vui lòng thử lại sau'}), 500