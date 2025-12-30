from flask import Flask, render_template, request, jsonify, url_for, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
import os

app = Flask(__name__)
# Lấy Secret Key từ biến môi trường
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key_12345')

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hàm tạo kết nối PostgreSQL
def get_db_connection():
    try:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL chưa được thiết lập!")
        return psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    except Exception as err:
        logger.error(f"Database connection error: {err}")
        raise

# Đóng kết nối
def close_db_connection(db, cursor=None):
    if cursor:
        cursor.close()
    if db:
        db.close()

@app.route('/')
def index():
    current_date = datetime.now().strftime("%B %d, %Y %I:%M %p %Z")
    return render_template('index/index.html', current_date=current_date)

@app.route('/products')
def products():
    category_id = request.args.get('category_id')
    return render_template('products/products.html', category_id=category_id)

@app.route('/product-detail')
def product_detail():
    product_id = request.args.get('id')
    return render_template('products/product-detail.html', product_id=product_id)

@app.route('/user')
def user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('user/profile.html')

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('user/cart.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT id, username, password, full_name FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['full_name'] = user['full_name']
                response = {
                    'success': True,
                    'message': 'Login successful',
                    'redirect': url_for('index'),
                    'full_name': user['full_name']
                }
            else:
                response = {'success': False, 'message': 'Invalid username or password'}
            close_db_connection(db, cursor)
            return jsonify(response)
        except Exception as err:
            logger.error(f"Error login: {err}")
            return jsonify({'success': False, 'message': 'Server error'}), 500
    return render_template('login/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])
            full_name = request.form['full_name']
            birth_date = request.form['birth_date']

            db = get_db_connection()
            cursor = db.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                close_db_connection(db, cursor)
                return jsonify({'success': False, 'message': 'Username or email already exists'}), 400

            sql = "INSERT INTO users (username, email, password, full_name, birth_date) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (username, email, password, full_name, birth_date))
            db.commit()
            
            close_db_connection(db, cursor)
            return jsonify({'success': True, 'message': 'Registration successful! Please login.', 'redirect': url_for('login')})
        except Exception as err:
            logger.error(f"Error register: {err}")
            return jsonify({'success': False, 'message': 'Server error'}), 500
    return render_template('login/register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            full_name = request.form['full_name']
            birth_date = request.form['birth_date']

            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = %s AND email = %s AND full_name = %s AND birth_date = %s",
                (username, email, full_name, birth_date)
            )
            user = cursor.fetchone()
            if user:
                new_password = generate_password_hash('newpassword123')
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user['id']))
                db.commit()
                response = {'success': True, 'message': 'Password reset to "newpassword123".', 'redirect': url_for('login')}
            else:
                response = {'success': False, 'message': 'No account found'}
            close_db_connection(db, cursor)
            return jsonify(response)
        except Exception as err:
            logger.error(f"Error forgot password: {err}")
            return jsonify({'success': False, 'message': 'Server error'}), 500
    return render_template('login/forgot_password.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('full_name', None)
    return jsonify({'success': True, 'message': 'Logged out successfully', 'redirect': url_for('index')})

@app.route('/api/check_login')
def check_login():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'full_name': session.get('full_name', 'User')})
    return jsonify({'logged_in': False})

@app.route('/api/user')
def get_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, username, email, full_name, birth_date FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        close_db_connection(db, cursor)
        if user:
            user['birth_date'] = str(user['birth_date'])
            return jsonify(user)
        return jsonify({'success': False, 'message': 'User not found'}), 404
    except Exception as err:
        return jsonify({'success': False, 'message': str(err)}), 500

@app.route('/api/update_user', methods=['POST'])
def update_user():
    if 'user_id' not in session: return jsonify({'success': False}), 401
    try:
        data = request.get_json()
        db = get_db_connection()
        cursor = db.cursor()
        
        # Kiểm tra email trùng (trừ chính user này)
        cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (data['email'], session['user_id']))
        if cursor.fetchone():
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'Email already exists'}), 400

        update_query = "UPDATE users SET full_name = %s, email = %s, birth_date = %s"
        update_values = [data['full_name'], data['email'], data['birth_date']]
        
        if data.get('password'):
            update_query += ", password = %s"
            update_values.append(generate_password_hash(data['password']))
            
        update_query += " WHERE id = %s"
        update_values.append(session['user_id'])
        
        cursor.execute(update_query, update_values)
        db.commit()
        session['full_name'] = data['full_name']
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'message': 'Updated successfully'})
    except Exception as err:
        logger.error(f"Update error: {err}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/categories')
def get_categories():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, image_url FROM categories")
        categories = [{"id": row['id'], "name": row['name'], "image_url": row['image_url']} for row in cursor.fetchall()]
        close_db_connection(db, cursor)
        return jsonify(categories)
    except Exception as err:
        return jsonify({'success': False, 'message': str(err)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        category_id = request.args.get('category_id')
        search_query = request.args.get('search')
        sort = request.args.get('sort', 'default')
        price_range = request.args.get('price_range', None)
        discount = request.args.get('discount', 'false') == 'true'

        query = """
            SELECT p.id, p.category_id, p.name, p.description, p.price, p.discount_percentage, p.discounted_price,
                   p.image_url, p.sold, p.stock_quantity, par.avg_rating, par.review_count
            FROM products p
            LEFT JOIN product_avg_rating par ON p.id = par.product_id
        """
        params = []
        conditions = []

        if category_id:
            conditions.append("p.category_id = %s")
            params.append(category_id)
        if search_query:
            conditions.append("p.name ILIKE %s") # Postgres dùng ILIKE để tìm kiếm không phân biệt hoa thường
            params.append(f"%{search_query}%")
        
        exchange_rate = 25000
        if price_range:
            ranges = price_range.split(',')
            range_conditions = []
            for r in ranges:
                if '-' in r:
                    min_v, max_v = map(float, r.split('-'))
                    range_conditions.append(f"p.discounted_price BETWEEN {min_v/exchange_rate} AND {max_v/exchange_rate}")
                elif r.endswith('+'):
                    min_v = float(r[:-1])
                    range_conditions.append(f"p.discounted_price >= {min_v/exchange_rate}")
            if range_conditions:
                conditions.append('(' + ' OR '.join(range_conditions) + ')')

        if discount: conditions.append("p.discount_percentage > 0")
        if conditions: query += " WHERE " + " AND ".join(conditions)

        if sort == 'price_asc': query += " ORDER BY p.discounted_price ASC"
        elif sort == 'price_desc': query += " ORDER BY p.discounted_price DESC"
        elif sort == 'discount_desc': query += " ORDER BY p.discount_percentage DESC"
        elif sort == 'rating_desc': query += " ORDER BY par.avg_rating DESC, par.review_count DESC"
        elif sort == 'sold DESC': query += " ORDER BY p.sold DESC"
        else: query += " ORDER BY p.id ASC"

        cursor.execute(query, params)
        products = cursor.fetchall()
        
        result = []
        for row in products:
            item = dict(row)
            # Chuyển đổi Decimal sang float nếu cần
            for k in ['price', 'discounted_price', 'avg_rating', 'discount_percentage']:
                if item.get(k) is not None: item[k] = float(item[k])
            
            item['price'] *= exchange_rate
            item['discounted_price'] *= exchange_rate
            item['student_price'] = item['discounted_price'] * 0.95
            item['installment'] = "0% qua thẻ tín dụng..."
            result.append(item)

        close_db_connection(db, cursor)
        return jsonify(result)
    except Exception as err:
        logger.error(f"Products error: {err}")
        return jsonify({'success': False, 'message': 'Database error'}), 500

@app.route('/api/product/<int:product_id>')
def get_product(product_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.id, p.category_id, p.name, p.description, p.price, p.discount_percentage, p.discounted_price,
                   p.image_url, p.sold, p.stock_quantity, par.avg_rating, par.review_count
            FROM products p
            LEFT JOIN product_avg_rating par ON p.id = par.product_id
            WHERE p.id = %s
        """, (product_id,))
        product = cursor.fetchone()
        
        if product:
            product = dict(product)
            exchange_rate = 25000
            for k in ['price', 'discounted_price', 'avg_rating', 'discount_percentage']:
                if product.get(k) is not None: product[k] = float(product[k])
            
            product['price'] *= exchange_rate
            product['discounted_price'] *= exchange_rate
            product['student_price'] = product['discounted_price'] * 0.95
            
            cursor.execute("SELECT r.comment, u.full_name FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.product_id = %s", (product_id,))
            product['reviews'] = [{"comment": r['comment'], "user_name": r['full_name']} for r in cursor.fetchall()]
            
            close_db_connection(db, cursor)
            return jsonify(product)
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Not found'}), 404
    except Exception as err:
        return jsonify({'success': False, 'message': str(err)}), 500

# Route này đã được khôi phục để sửa lỗi BuildError
@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        # Xử lý form contact (Ví dụ lưu vào DB hoặc gửi email)
        name = request.form.get('name')
        logger.info(f"Contact received from {name}")
        return jsonify({'success': True, 'message': 'Cảm ơn bạn đã liên hệ!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/reviews/add', methods=['POST'])
def add_review():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO reviews (user_id, product_id, comment, rating) VALUES (%s, %s, %s, %s)",
                       (session['user_id'], data['product_id'], data['comment'], data['rating']))
        db.commit()
        close_db_connection(db, cursor)
        return jsonify({'success': True})
    except Exception as err:
        return jsonify({'success': False, 'message': str(err)}), 500

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Please log in'}), 401
    try:
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        
        db = get_db_connection()
        cursor = db.cursor()
        
        cursor.execute("SELECT stock_quantity, discounted_price FROM products WHERE id = %s", (product_id,))
        prod = cursor.fetchone()
        if not prod or prod['stock_quantity'] < quantity:
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'Out of stock'}), 400

        # Postgres ON CONFLICT
        query = """
            INSERT INTO cart (user_id, product_id, quantity) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (user_id, product_id) 
            DO UPDATE SET quantity = cart.quantity + EXCLUDED.quantity
        """
        cursor.execute(query, (session['user_id'], product_id, quantity))
        db.commit()
        
        total = float(prod['discounted_price']) * quantity * 25000
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'message': 'Added', 'total_price': total})
    except Exception as err:
        logger.error(f"Cart add error: {err}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/cart', methods=['GET'])
def get_cart():
    if 'user_id' not in session: return jsonify({'success': False}), 401
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT c.product_id, p.name, p.discounted_price, c.quantity, p.image_url
            FROM cart c JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (session['user_id'],))
        items = []
        total_cart = 0
        exchange_rate = 25000
        for row in cursor.fetchall():
            item = dict(row)
            item['price'] = float(item['discounted_price']) * exchange_rate
            item['total'] = item['price'] * item['quantity']
            total_cart += item['total']
            item['selected'] = False
            items.append(item)
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'items': items, 'total_cart_price': total_cart})
    except Exception as err:
        return jsonify({'success': False, 'message': str(err)}), 500

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session: return jsonify({'success': False}), 401
    try:
        data = request.get_json()
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (session['user_id'], data['product_id']))
        db.commit()
        close_db_connection(db, cursor)
        return jsonify({'success': True})
    except Exception: return jsonify({'success': False}), 500

@app.route('/api/cart/checkout', methods=['POST'])
def checkout_cart():
    if 'user_id' not in session: return jsonify({'success': False}), 401
    try:
        data = request.get_json()
        items = data.get('selected_items', [])
        payment = data.get('payment_method')
        
        db = get_db_connection()
        cursor = db.cursor()
        
        for item in items:
            pid = item['product_id']
            qty = item['quantity']
            cursor.execute("SELECT discounted_price FROM products WHERE id = %s", (pid,))
            price = float(cursor.fetchone()['discounted_price']) * 25000 * qty
            
            cursor.execute("INSERT INTO order_activities (user_id, product_id, quantity, total_price, status) VALUES (%s, %s, %s, %s, %s)",
                           (session['user_id'], pid, qty, price, 'Đang chờ giao'))
            cursor.execute("UPDATE products SET stock_quantity = stock_quantity - %s, sold = sold + %s WHERE id = %s", (qty, qty, pid))
            cursor.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (session['user_id'], pid))
            
        db.commit()
        close_db_connection(db, cursor)
        msg = 'Thanh toán thành công!' if payment != 'online' else 'Thanh toán online chưa hỗ trợ.'
        return jsonify({'success': True, 'message': msg})
    except Exception as err:
        logger.error(f"Checkout error: {err}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/user/profile')
def get_user_profile():
    if 'user_id' not in session: return jsonify({'success': False}), 401
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        cursor.execute("SELECT username, email, full_name, birth_date FROM users WHERE id = %s", (session['user_id'],))
        user = dict(cursor.fetchone())
        user['birth_date'] = str(user['birth_date'])
        
        # Postgres trả về key là 'count' chữ thường (thay vì COUNT(*))
        cursor.execute("SELECT COUNT(*) as count FROM cart WHERE user_id = %s", (session['user_id'],))
        cart_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT SUM(quantity) as total FROM order_activities WHERE user_id = %s", (session['user_id'],))
        res = cursor.fetchone()
        purchased_count = res['total'] if res and res['total'] else 0
        
        cursor.execute("SELECT * FROM order_activities WHERE user_id = %s", (session['user_id'],))
        orders = []
        for row in cursor.fetchall():
            o = dict(row)
            o['date'] = o['created_at'].strftime('%Y-%m-%d %H:%M')
            orders.append(o)
            
        cursor.execute("SELECT COALESCE(SUM(total_price), 0) as spent FROM order_activities WHERE user_id = %s", (session['user_id'],))
        total_spent = cursor.fetchone()['spent']
        
        cursor.execute("SELECT * FROM addresses WHERE user_id = %s", (session['user_id'],))
        addresses = [dict(row) for row in cursor.fetchall()]
        
        data = {
            'user_info': user,
            'cart_count': cart_count,
            'purchased_count': purchased_count,
            'orders': orders,
            'total_spent': total_spent,
            'addresses': addresses
        }
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'data': data})
    except Exception as err:
        logger.error(f"Profile error: {err}")
        return jsonify({'success': False}), 500

@app.route('/api/user/addresses', methods=['GET'])
def get_addresses():
    if 'user_id' not in session: return jsonify({'success': False}), 401
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM addresses WHERE user_id = %s", (session['user_id'],))
        addresses = [dict(row) for row in cursor.fetchall()]
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'data': {'addresses': addresses}})
    except Exception: return jsonify({'success': False}), 500

@app.route('/api/user/addresses/add', methods=['POST'])
def add_address():
    if 'user_id' not in session: return jsonify({'success': False}), 401
    try:
        data = request.get_json()
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO addresses (user_id, address, city, postal_code, country) VALUES (%s, %s, %s, %s, %s)",
                       (session['user_id'], data['address_line'], data['city'], data['postal_code'], data['country']))
        db.commit()
        close_db_connection(db, cursor)
        return jsonify({'success': True})
    except Exception: return jsonify({'success': False}), 500

@app.route('/api/user/addresses/<int:address_id>/delete', methods=['POST'])
def delete_address(address_id):
    if 'user_id' not in session: return jsonify({'success': False}), 401
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM addresses WHERE id = %s AND user_id = %s", (address_id, session['user_id']))
        db.commit()
        close_db_connection(db, cursor)
        return jsonify({'success': True})
    except Exception: return jsonify({'success': False}), 500

@app.route('/api/user/addresses/<int:address_id>/edit', methods=['POST'])
def edit_address(address_id):
    if 'user_id' not in session: return jsonify({'success': False}), 401
    try:
        data = request.get_json()
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("UPDATE addresses SET address=%s, city=%s, postal_code=%s, country=%s WHERE id=%s AND user_id=%s",
                       (data['address_line'], data['city'], data['postal_code'], data['country'], address_id, session['user_id']))
        db.commit()
        close_db_connection(db, cursor)
        return jsonify({'success': True})
    except Exception: return jsonify({'success': False}), 500

if __name__ == '__main__':
    app.run(debug=True)