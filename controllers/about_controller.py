from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash
from models.user import User
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # API Login (Fetch/AJAX)
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Hỗ trợ cả JSON và Form Data
                data = request.get_json() if request.is_json else request.form
                username = data.get('username')
                password = data.get('password')

                user = User.get_by_username(username)

                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['role'] = user['role']
                    session['full_name'] = user['full_name']
                    return jsonify({'success': True, 'message': 'Đăng nhập thành công!', 'redirect': url_for('index')})
                else:
                    return jsonify({'success': False, 'message': 'Tên đăng nhập hoặc mật khẩu không đúng.'}), 401
            except Exception as e:
                logger.error(f"Lỗi khi đăng nhập API: {e}")
                return jsonify({'success': False, 'message': 'Lỗi máy chủ.'}), 500
        
        # Form Login (Truyền thống)
        username = request.form['username']
        password = request.form['password']
        try:
            user = User.get_by_username(username)
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                return redirect(url_for('index'))
            else:
                flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
        except Exception as e:
            logger.error(f"Lỗi khi đăng nhập Form: {e}")
            flash('Có lỗi xảy ra, vui lòng thử lại.', 'danger')

    return render_template('login/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # API Register
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = request.get_json() if request.is_json else request.form
                username = data.get('username')
                email = data.get('email')
                password = data.get('password')
                full_name = data.get('full_name')
                birth_date = data.get('birth_date')

                if User.get_by_username(username):
                     return jsonify({'success': False, 'message': 'Tên đăng nhập đã tồn tại.'}), 400
                
                if User.check_email_exists(email):
                     return jsonify({'success': False, 'message': 'Email đã tồn tại.'}), 400

                if User.create(username, email, password, full_name, birth_date):
                    logger.info(f"Người dùng {username} đăng ký thành công")
                    return jsonify({'success': True, 'message': 'Đăng ký thành công!', 'redirect': url_for('auth.login')})
                else:
                    return jsonify({'success': False, 'message': 'Đăng ký thất bại. Vui lòng thử lại.'}), 500
            except Exception as e:
                logger.error(f"Lỗi đăng ký API: {e}")
                return jsonify({'success': False, 'message': str(e)}), 500

        # Form Register
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        birth_date = request.form['birth_date']
        
        try:
            if User.create(username, email, password, full_name, birth_date):
                flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Đăng ký thất bại.', 'danger')
        except Exception as e:
            logger.error(f"Lỗi đăng ký Form: {e}")
            flash('Lỗi hệ thống.', 'danger')

    return render_template('login/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))