# controllers/auth_controller.py
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models.user import User
from models.database import get_db_connection, close_db_connection
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            logger.debug(f"Nhận dữ liệu đăng nhập: {{'username': {username}, 'password': '[REDACTED]'}}")

            user = User.get_by_username(username)
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['full_name'] = user[3]
                session['role'] = user[4]
                redirect_url = url_for('admin.dashboard') if user[4] == 'admin' else url_for('index')
                response = {
                    'success': True,
                    'message': 'Đăng nhập thành công',
                    'redirect': redirect_url,
                    'full_name': user[3]
                }
                logger.info(f"Người dùng {username} đăng nhập thành công với vai trò {user[4]}")
            else:
                response = {'success': False, 'message': 'Tên đăng nhập hoặc mật khẩu không đúng'}
                logger.warning(f"Thử đăng nhập thất bại cho username: {username}")
            return jsonify(response)
        except Exception as e:
            logger.error(f"Lỗi khi đăng nhập: {e}")
            return jsonify({'success': False, 'message': 'Lỗi, vui lòng thử lại sau'}), 500
    return render_template('login/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            full_name = request.form['full_name']
            birth_date = request.form['birth_date']

            if User.create(username, email, password, full_name, birth_date):
                logger.info(f"Người dùng {username} đăng ký thành công")
                return jsonify({
                    'success': True,
                    'message': 'Đăng ký thành công! Vui lòng đăng nhập.',
                    'redirect': url_for('auth.login')
                })
            else:
                logger.warning(f"Tên đăng nhập hoặc email đã tồn tại: {username}, {email}")
                return jsonify({'success': False, 'message': 'Tên đăng nhập hoặc email đã tồn tại'}), 400
        except Exception as e:
            logger.error(f"Lỗi khi đăng ký: {e}")
            return jsonify({'success': False, 'message': 'Lỗi, vui lòng thử lại sau'}), 500
    return render_template('login/register.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            full_name = request.form['full_name']
            birth_date = request.form['birth_date']
            logger.debug(f"Nhận dữ liệu quên mật khẩu: {{'username': {username}, 'email': {email}}}")

            try:
                datetime.strptime(birth_date, '%Y-%m-%d')
            except ValueError:
                logger.error(f"Định dạng ngày sinh không hợp lệ: {birth_date}")
                return jsonify({'success': False, 'message': 'Định dạng ngày sinh không hợp lệ. Sử dụng YYYY-MM-DD.'}), 400

            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = %s AND email = %s AND full_name = %s AND birth_date = %s",
                (username, email, full_name, birth_date)
            )
            user = cursor.fetchone()
            if user:
                new_password = generate_password_hash('newpassword123')
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user[0]))
                db.commit()
                response = {
                    'success': True,
                    'message': 'Mật khẩu đã được đặt lại thành "newpassword123". Vui lòng đăng nhập.',
                    'redirect': url_for('auth.login')
                }
                logger.info(f"Đặt lại mật khẩu thành công cho người dùng: {username}")
            else:
                response = {'success': False, 'message': 'Không tìm thấy tài khoản với thông tin đã cung cấp'}
                logger.warning(f"Thử đặt lại mật khẩu thất bại cho username: {username}")
            close_db_connection(db, cursor)
            return jsonify(response)
        except Exception as e:
            logger.error(f"Lỗi khi đặt lại mật khẩu: {e}")
            return jsonify({'success': False, 'message': 'Lỗi, vui lòng thử lại sau'}), 500
    return render_template('login/forgot_password.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    username = session.get('full_name', 'Unknown')
    session.pop('user_id', None)
    session.pop('full_name', None)
    session.pop('role', None)
    logger.info(f"Người dùng {username} đăng xuất thành công")
    return jsonify({'success': True, 'message': 'Đăng xuất thành công', 'redirect': url_for('index')})