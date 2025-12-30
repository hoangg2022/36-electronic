from flask import Blueprint, request, jsonify, session, render_template,redirect,url_for
from werkzeug.utils import secure_filename
import os
import logging
from models.user import User
from models.database import get_db_connection, close_db_connection
from models.product import Product
from models.order import Order
from datetime import datetime

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

# Hàm kiểm tra loại tệp cho phép
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Hàm kiểm tra yêu cầu AJAX
def is_ajax_request():
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

# Route cho trang dashboard admin
@admin_bp.route('/admin')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào bảng điều khiển admin")
        if is_ajax_request():
            return jsonify({'success': False, 'message': 'Không được phép, vui lòng đăng nhập với tài khoản admin'}), 401
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')

# Route cho trang quản lý người dùng
@admin_bp.route('/admin/users')
def manage_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào quản lý người dùng")
        if is_ajax_request():
            return jsonify({'success': False, 'message': 'Không được phép, vui lòng đăng nhập với tài khoản admin'}), 401
        return redirect(url_for('auth.login'))
    return render_template('admin/manage_users.html')

# Route cho trang quản lý sản phẩm
@admin_bp.route('/admin/products')
def manage_products():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào quản lý sản phẩm")
        if is_ajax_request():
            return jsonify({'success': False, 'message': 'Không được phép, vui lòng đăng nhập với tài khoản admin'}), 401
        return redirect(url_for('auth.login'))
    return render_template('admin/manage_products.html')

# Route cho trang quản lý đơn hàng
@admin_bp.route('/admin/orders')
def manage_orders():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào quản lý đơn hàng")
        if is_ajax_request():
            return jsonify({'success': False, 'message': 'Không được phép, vui lòng đăng nhập với tài khoản admin'}), 401
        return redirect(url_for('auth.login'))
    return render_template('admin/manage_orders.html')

# API lấy thống kê admin
@admin_bp.route('/api/admin/stats')
def get_admin_stats():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào thống kê admin")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_activities")
        total_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(total_price), 0) FROM order_activities")
        total_revenue = cursor.fetchone()[0]

        close_db_connection(db, cursor)
        return jsonify({
            'success': True,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue) 
        })
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê admin: {e}")
        if 'db' in locals() and 'cursor' in locals():
            close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API lấy danh sách người dùng
@admin_bp.route('/api/admin/users')
def get_admin_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào danh sách người dùng admin")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT u.id, u.full_name, u.email, u.birth_date, u.role, COALESCE(SUM(o.total_price), 0), COUNT(o.id)
            FROM users u
            LEFT JOIN order_activities o ON u.id = o.user_id
            GROUP BY u.id
        """)
        users = [{
            'id': row[0],
            'full_name': row[1],
            'email': row[2],
            'birth_date': row[3].isoformat() if row[3] else None,  # Convert DATE to YYYY-MM-DD string
            'role': row[4],
            'total_spent': float(row[5]),
            'order_count': row[6]
        } for row in cursor.fetchall()]
        close_db_connection(db, cursor)
        return jsonify(users)
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách người dùng: {e}")
        if 'db' in locals() and 'cursor' in locals():
            close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API thêm người dùng mới
@admin_bp.route('/api/admin/add_user', methods=['POST'])
def add_admin_user():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Thử thêm người dùng không được phép")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        data = request.get_json()
        username = data['username']
        email = data['email']
        password = data['password']
        full_name = data['full_name']
        birth_date = data['birth_date']
        role = data['role']

        if not all([username, email, password, full_name, birth_date, role]):
            return jsonify({'success': False, 'message': 'Thiếu thông tin bắt buộc'}), 400

        if role not in ['customer', 'admin']:
            logger.error(f"Vai trò không hợp lệ: {role}")
            return jsonify({'success': False, 'message': 'Vai trò không hợp lệ'}), 400

        try:
            datetime.strptime(birth_date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Định dạng ngày sinh không hợp lệ: {birth_date}")
            return jsonify({'success': False, 'message': 'Định dạng ngày sinh phải là YYYY-MM-DD'}), 400

        if User.check_email_exists(email):
            logger.warning(f"Email đã tồn tại: {email}")
            return jsonify({'success': False, 'message': 'Email đã được sử dụng'}), 400

        if User.get_by_username(username):
            logger.warning(f"Tên đăng nhập đã tồn tại: {username}")
            return jsonify({'success': False, 'message': 'Tên đăng nhập đã tồn tại'}), 400

        if User.create(username, email, password, full_name, birth_date,role):
            logger.info(f"Admin đã thêm người dùng: {username}")
            return jsonify({'success': True, 'message': 'Thêm người dùng thành công'})
        return jsonify({'success': False, 'message': 'Không thể thêm người dùng'}), 500
    except KeyError as e:
        logger.error(f"Thiếu trường dữ liệu: {e}")
        return jsonify({'success': False, 'message': f'Thiếu trường: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Lỗi khi thêm người dùng: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API cập nhật thông tin người dùng
@admin_bp.route('/api/admin/update_user/<int:user_id>', methods=['PUT'])
def update_admin_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Thử cập nhật người dùng không được phép")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        data = request.get_json()
        print(data)
        full_name = data.get('full_name')
        email = data.get('email')
        birth_date = data.get('birth_date')
        password = data.get('password')
        role = data.get('role')
        print(role)
        if not all([full_name, email, birth_date, role]):
            logger.error("Thiếu các trường bắt buộc")
            return jsonify({'success': False, 'message': 'Thiếu thông tin bắt buộc'}), 400

        try:
            datetime.strptime(birth_date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Định dạng ngày sinh không hợp lệ: {birth_date}")
            return jsonify({'success': False, 'message': 'Định dạng ngày sinh phải là YYYY-MM-DD'}), 400

        if role not in ['customer', 'admin']:
            logger.error(f"Vai trò không hợp lệ: {role}")
            return jsonify({'success': False, 'message': 'Vai trò không hợp lệ'}), 400

        if User.check_email_exists(email, user_id):
            logger.warning(f"Email đã tồn tại: {email}")
            return jsonify({'success': False, 'message': 'Email đã được sử dụng'}), 400

        if User.update(user_id, full_name, email, birth_date, password,role):
            logger.info(f"Admin đã cập nhật người dùng ID: {user_id}")
            return jsonify({'success': True, 'message': 'Cập nhật người dùng thành công'})
        return jsonify({'success': False, 'message': 'Không thể cập nhật người dùng'}), 500
    except KeyError as e:
        logger.error(f"Thiếu trường dữ liệu: {e}")
        return jsonify({'success': False, 'message': f'Thiếu trường: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật người dùng: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API xóa người dùng
@admin_bp.route('/api/admin/delete_user/<int:user_id>', methods=['DELETE'])
def delete_admin_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Thử xóa người dùng không được phép")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        if User.delete(user_id):
            logger.info(f"Admin đã xóa người dùng ID: {user_id}")
            return jsonify({'success': True, 'message': 'Xóa người dùng thành công'})
        return jsonify({'success': False, 'message': 'Không thể xóa người dùng'}), 500
    except Exception as e:
        logger.error(f"Lỗi khi xóa người dùng: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API lấy danh sách sản phẩm
@admin_bp.route('/api/admin/products')
def get_admin_products():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào danh sách sản phẩm")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        search_query = request.args.get('search', '')
        sort = request.args.get('sort', 'id_asc')
        products = Product.get_all(search_query=search_query, sort=sort)
        if products:
            return jsonify([{
                'id': row[0],
                'name': row[2],
                'category_name': row[1],
                'price': float(row[4])*25000 ,
                'discount_percentage': float(row[5]),
                'stock_quantity': row[9],
                'sold': row[8]
            } for row in products])
        return jsonify({'success': False, 'message': 'Không tìm thấy sản phẩm'}), 404
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách sản phẩm: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API thêm sản phẩm mới
@admin_bp.route('/api/admin/add_product', methods=['POST'])
def add_admin_product():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Thử thêm sản phẩm không được phép")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        name = request.form['name']
        category_id = request.form['category_id']
        description = request.form['description']
        price = float(request.form['price'])
        discount_percentage = float(request.form['discount_percentage'])
        stock_quantity = int(request.form['stock_quantity'])

        if 'image' not in request.files:
            logger.error("Không có tệp hình ảnh")
            return jsonify({'success': False, 'message': 'Vui lòng tải lên hình ảnh'}), 400

        file = request.files['image']
        if file.filename == '':
            logger.error("Không chọn tệp hình ảnh")
            return jsonify({'success': False, 'message': 'Vui lòng chọn hình ảnh'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('static/uploads', filename)
            file.save(file_path)
            image_url = f"/{file_path}"

            if Product.create(category_id, name, description, price, discount_percentage, image_url, stock_quantity):
                logger.info(f"Admin đã thêm sản phẩm: {name}")
                return jsonify({'success': True, 'message': 'Thêm sản phẩm thành công'})
            return jsonify({'success': False, 'message': 'Không thể thêm sản phẩm'}), 500
        logger.error(f"Loại tệp không được phép: {file.filename}")
        return jsonify({'success': False, 'message': 'Chỉ chấp nhận png, jpg, jpeg, gif'}), 400
    except KeyError as e:
        logger.error(f"Thiếu trường dữ liệu: {e}")
        return jsonify({'success': False, 'message': f'Thiếu trường: {str(e)}'}), 400
    except ValueError as e:
        logger.error(f"Dữ liệu không hợp lệ: {e}")
        return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400
    except Exception as e:
        logger.error(f"Lỗi khi thêm sản phẩm: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API cập nhật sản phẩm
@admin_bp.route('/api/admin/update_product/<int:product_id>', methods=['PUT'])
def update_admin_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Thử cập nhật sản phẩm không được phép")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        name = request.form['name']
        category_id = request.form['category_id']
        description = request.form['description']
        price = float(request.form['price'])
        discount_percentage = float(request.form['discount_percentage'])
        stock_quantity = int(request.form['stock_quantity'])
        image_url = request.form.get('image_url', '')

        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join('static/uploads', filename)
                file.save(file_path)
                image_url = f"/{file_path}"
            else:
                logger.error(f"Loại tệp không được phép: {file.filename}")
                return jsonify({'success': False, 'message': 'Chỉ chấp nhận png, jpg, jpeg, gif'}), 400

        if Product.update(product_id, name, category_id, description, price, discount_percentage, image_url, stock_quantity):
            logger.info(f"Admin đã cập nhật sản phẩm ID: {product_id}")
            return jsonify({'success': True, 'message': 'Cập nhật sản phẩm thành công'})
        return jsonify({'success': False, 'message': 'Không thể cập nhật sản phẩm'}), 500
    except KeyError as e:
        logger.error(f"Thiếu trường dữ liệu: {e}")
        return jsonify({'success': False, 'message': f'Thiếu trường: {str(e)}'}), 400
    except ValueError as e:
        logger.error(f"Dữ liệu không hợp lệ: {e}")
        return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật sản phẩm: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500
# API lấy thông tin chi tiết sản phẩm
@admin_bp.route('/api/admin/product/<int:product_id>', methods=['GET'])
def get_admin_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào thông tin chi tiết sản phẩm")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        product = Product.get_by_id(product_id)
        if product:
            return jsonify({
                'success': True,
                'id': product[0],
                'name': product[2],
                'category_name': product[1],
                'description': product[3],
                'price': float(product[4]) ,
                'discount_percentage': float(product[5]),
                'image_url': product[6],
                'stock_quantity': product[9],
                'sold': product[8]
            })
        return jsonify({'success': False, 'message': 'Không tìm thấy sản phẩm'}), 404
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin sản phẩm ID {product_id}: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500
# API xóa sản phẩm
@admin_bp.route('/api/admin/delete_product/<int:product_id>', methods=['DELETE'])
def delete_admin_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Thử xóa sản phẩm không được phép")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        if Product.delete(product_id):
            logger.info(f"Admin đã xóa sản phẩm ID: {product_id}")
            return jsonify({'success': True, 'message': 'Xóa sản phẩm thành công'})
        return jsonify({'success': False, 'message': 'Không thể xóa sản phẩm'}), 500
    except Exception as e:
        logger.error(f"Lỗi khi xóa sản phẩm: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API lấy danh sách đơn hàng
@admin_bp.route('/api/admin/orders')
def get_admin_orders():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào danh sách đơn hàng")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        orders = Order.get_all()
        if orders:
            pending_orders = [{
                'id': row[0],
                'user_name': row[1],
                'product_name': row[2],
                'quantity': row[3],
                'total_price': float(row[4]),
                'status': row[5],
                'phone': row[7],  # Updated field from phone_number to phone
                'address': row[8] # Updated field
            } for row in orders if row[5] in ['Đang chờ giao', 'Đang giao']]
            completed_orders = [{
                'id': row[0],
                'user_name': row[1],
                'product_name': row[2],
                'quantity': row[3],
                'total_price': float(row[4]),
                'status': row[5],
                'delivered_at': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
                'phone': row[7],  # Updated field from phone_number to phone
                'address': row[8] # Updated field
            } for row in orders if row[5] == 'Đã giao']
            return jsonify({
                'success': True,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders
            })
        return jsonify({'success': False, 'message': 'Không tìm thấy đơn hàng'}), 404
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách đơn hàng: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API cập nhật trạng thái đơn hàng
@admin_bp.route('/api/admin/update_order_status/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Thử cập nhật trạng thái đơn hàng không được phép")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        data = request.get_json()
        status = data['status']
        if status not in ['Đang chờ giao', 'Đang giao', 'Đã giao']:
            logger.error(f"Trạng thái không hợp lệ: {status}")
            return jsonify({'success': False, 'message': 'Trạng thái không hợp lệ'}), 400

        if Order.update_status(order_id, status):
            logger.info(f"Admin đã cập nhật trạng thái đơn hàng ID: {order_id} thành {status}")
            return jsonify({'success': True, 'message': 'Cập nhật trạng thái thành công'})
        return jsonify({'success': False, 'message': 'Không thể cập nhật trạng thái'}), 500
    except KeyError as e:
        logger.error(f"Thiếu trường dữ liệu: {e}")
        return jsonify({'success': False, 'message': f'Thiếu trường: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật trạng thái đơn hàng: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500

# API xóa đơn hàng
@admin_bp.route('/api/admin/delete_order/<int:order_id>', methods=['DELETE'])
def delete_admin_order(order_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Thử xóa đơn hàng không được phép")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        if Order.delete(order_id):
            logger.info(f"Admin đã xóa đơn hàng ID: {order_id}")
            return jsonify({'success': True, 'message': 'Xóa đơn hàng thành công'})
        return jsonify({'success': False, 'message': 'Không thể xóa đơn hàng'}), 500
    except Exception as e:
        logger.error(f"Lỗi khi xóa đơn hàng: {e}")
        return jsonify({'success': False, 'message': 'Lỗi cơ sở dữ liệu'}), 500