from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash
from models.user import User
import logging
import traceback # Thêm thư viện này để soi lỗi kỹ hơn

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 1. Lấy dữ liệu từ Form hoặc JSON
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            is_api = True
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            is_api = False

        try:
            # 2. Tìm user trong DB
            user = User.get_by_username(username)
            
            # Log để kiểm tra (Xóa sau khi fix xong)
            if user:
                logger.info(f"Tìm thấy user: {user.get('username')}, ID: {user.get('id')}")
            else:
                logger.warning(f"Không tìm thấy user: {username}")

            # 3. Kiểm tra mật khẩu
            # Lưu ý: user phải là Dictionary và có key 'password'
            if user and user.get('password') and check_password_hash(user['password'], password):
                # Đăng nhập thành công -> Lưu Session
                session['user_id'] = user['id']
                session['role'] = user.get('role', 'customer') # Mặc định là customer nếu thiếu
                session['full_name'] = user.get('full_name', '')
                
                if is_api:
                    return jsonify({'success': True, 'message': 'Đăng nhập thành công!', 'redirect': url_for('index')})
                else:
                    return redirect(url_for('index'))
            else:
                msg = 'Tên đăng nhập hoặc mật khẩu không đúng.'
                if is_api:
                    return jsonify({'success': False, 'message': msg}), 401
                else:
                    flash(msg, 'danger')

        except Exception as e:
            # In ra lỗi chi tiết để debug
            logger.error(f"Lỗi đăng nhập nghiêm trọng: {str(e)}")
            logger.error(traceback.format_exc()) # In toàn bộ vết lỗi
            
            msg = 'Lỗi hệ thống khi đăng nhập. Vui lòng thử lại.'
            if is_api:
                return jsonify({'success': False, 'message': msg}), 500
            else:
                flash(msg, 'danger')

    return render_template('login/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            is_api = True
        else:
            data = request.form
            is_api = False
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        birth_date = data.get('birth_date')

        try:
            if User.get_by_username(username):
                msg = 'Tên đăng nhập đã tồn tại.'
                return jsonify({'success': False, 'message': msg}) if is_api else flash(msg, 'danger') or render_template('login/register.html')
            
            if User.check_email_exists(email):
                msg = 'Email đã tồn tại.'
                return jsonify({'success': False, 'message': msg}) if is_api else flash(msg, 'danger') or render_template('login/register.html')

            if User.create(username, email, password, full_name, birth_date):
                msg = 'Đăng ký thành công! Vui lòng đăng nhập.'
                if is_api:
                    return jsonify({'success': True, 'message': msg, 'redirect': url_for('auth.login')})
                else:
                    flash(msg, 'success')
                    return redirect(url_for('auth.login'))
            else:
                msg = 'Đăng ký thất bại. Vui lòng thử lại.'
                return jsonify({'success': False, 'message': msg}) if is_api else flash(msg, 'danger') or render_template('login/register.html')

        except Exception as e:
            logger.error(f"Lỗi đăng ký: {e}")
            logger.error(traceback.format_exc())
            msg = 'Lỗi hệ thống.'
            return jsonify({'success': False, 'message': msg}) if is_api else flash(msg, 'danger') or render_template('login/register.html')

    return render_template('login/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))