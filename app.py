from flask import Flask, render_template, request, jsonify, url_for, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure random key in production

# Thiết lập logging để dễ debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hàm tạo kết nối MySQL
def get_db_connection():
    try:
        # Lấy URL từ biến môi trường của Render
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)
        return conn
    except Exception as err:
        logger.error(f"Database connection error: {err}")
        raise

# Đóng kết nối MySQL an toàn
def close_db_connection(db, cursor=None):
    if cursor:
        cursor.close()
    if db:
        db.close()

@app.route('/')
def index():
    current_date = datetime.now().strftime("%B %d, %Y %I:%M %p %Z")  # e.g., May 31, 2025 07:18 PM +07
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
            logger.debug(f"Received login data: {{'username': {username}, 'password': '[REDACTED]'}}")

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
                logger.info(f"User {username} logged in successfully")
            else:
                response = {'success': False, 'message': 'Invalid username or password'}
                logger.warning(f"Failed login attempt for username: {username}")
            close_db_connection(db, cursor)
            return jsonify(response)
        except psycopg2.Error as err:
            logger.error(f"Database error during login: {err}")
            return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500
        except KeyError as e:
            logger.error(f"Missing field in login request: {str(e)}")
            return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400
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
            sql = "INSERT INTO users (username, email, password, full_name, birth_date) VALUES (%s, %s, %s, %s, %s)"
            values = (username, email, password, full_name, birth_date)
            cursor.execute(sql, values)
            db.commit()
            response = {
                'success': True,
                'message': 'Registration successful! Please login.',
                'redirect': url_for('login')
            }
            logger.info(f"User {username} registered successfully")
            close_db_connection(db, cursor)
            return jsonify(response)
        except pymysql.IntegrityError as err:
            logger.warning(f"Duplicate username or email during registration: {err}")
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
        except KeyError as e:
            logger.error(f"Missing field in register request: {str(e)}")
            return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400
        except psycopg2.Error as err:
            logger.error(f"Database error during registration: {err}")
            return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500
    return render_template('login/register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            full_name = request.form['full_name']
            birth_date = request.form['birth_date']
            logger.debug(f"Received forgot password data: {{'username': {username}, 'email': {email}, 'full_name': {full_name}, 'birth_date': {birth_date}}}")

            try:
                datetime.strptime(birth_date, '%Y-%m-%d')
            except ValueError:
                logger.error(f"Invalid birth date format: {birth_date}")
                return jsonify({'success': False, 'message': 'Invalid birth date format. Use YYYY-MM-DD.'}), 400

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
                response = {
                    'success': True,
                    'message': 'Password reset to "newpassword123". Please login.',
                    'redirect': url_for('login')
                }
                logger.info(f"Password reset successful for user: {username}")
            else:
                response = {'success': False, 'message': 'No account found with the provided details'}
                logger.warning(f"Failed password reset attempt for username: {username}")
            close_db_connection(db, cursor)
            return jsonify(response)
        except KeyError as e:
            logger.error(f"Missing field in forgot password request: {str(e)}")
            return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400
        except psycopg2.Error as err:
            logger.error(f"Database error during password reset: {err}")
            return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500
    return render_template('login/forgot_password.html')

@app.route('/logout', methods=['POST'])
def logout():
    username = session.get('full_name', 'Unknown')
    session.pop('user_id', None)
    session.pop('full_name', None)
    logger.info(f"User {username} logged out successfully")
    return jsonify({'success': True, 'message': 'Logged out successfully', 'redirect': url_for('index')})

@app.route('/api/check_login')
def check_login():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'full_name': session.get('full_name', 'User')})
    return jsonify({'logged_in': False})

@app.route('/api/user')
def get_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, username, email, full_name, birth_date FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        if user:
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'birth_date': str(user['birth_date'])
            }
            close_db_connection(db, cursor)
            return jsonify(user_data)
        else:
            logger.warning(f"User not found for user_id: {session['user_id']}")
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'User not found'}), 404
    except psycopg2.Error as err:
        logger.error(f"Database error in get_user: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

@app.route('/api/update_user', methods=['POST'])
def update_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    try:
        data = request.get_json()
        full_name = data.get('full_name')
        email = data.get('email')
        birth_date = data.get('birth_date')
        password = data.get('password')

        if not full_name or not email or not birth_date:
            logger.error("Missing required fields in update_user request")
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        try:
            datetime.strptime(birth_date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Invalid birth date format: {birth_date}")
            return jsonify({'success': False, 'message': 'Invalid birth date format. Use YYYY-MM-DD.'}), 400

        db = get_db_connection()
        cursor = db.cursor()

        # Kiểm tra email trùng lặp (không tính chính user hiện tại)
        cursor.execute(
            "SELECT id FROM users WHERE email = %s AND id != %s",
            (email, session['user_id'])
        )
        if cursor.fetchone():
            close_db_connection(db, cursor)
            logger.warning(f"Email already exists: {email}")
            return jsonify({'success': False, 'message': 'Email already exists'}), 400

        # Cập nhật thông tin
        update_query = "UPDATE users SET full_name = %s, email = %s, birth_date = %s"
        update_values = [full_name, email, birth_date]

        if password:
            update_query += ", password = %s"
            update_values.append(generate_password_hash(password))

        update_query += " WHERE id = %s"
        update_values.append(session['user_id'])

        cursor.execute(update_query, update_values)
        db.commit()

        # Cập nhật lại session
        session['full_name'] = full_name
        logger.info(f"User {session['user_id']} updated profile successfully")

        close_db_connection(db, cursor)
        return jsonify({'success': True, 'message': 'User information updated successfully'})
    except psycopg2.Error as err:
        logger.error(f"Database error in update_user: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500
    except KeyError as e:
        logger.error(f"Missing field in update_user request: {str(e)}")
        return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400

@app.route('/api/categories')
def get_categories():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, image_url FROM categories")
        categories = [{"id": row['id'], "name": row['name'], "image_url": row['image_url']} for row in cursor.fetchall()]
        close_db_connection(db, cursor)
        return jsonify(categories)
    except psycopg2.Error as err:
        logger.error(f"Database error in get_categories: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

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

        # Apply category filter
        if category_id:
            conditions.append("p.category_id = %s")
            params.append(category_id)

        # Apply search filter
        if search_query:
            conditions.append("p.name LIKE %s")
            params.append(f"%{search_query}%")

        # Apply price range filter (convert VND to USD for internal processing)
        exchange_rate = 25000  # 1 USD = 25,000 VND
        if price_range:
            logger.debug(f"Received price_range: {price_range}")
            ranges = price_range.split(',')
            range_conditions = []
            for r in ranges:
                if '-' in r:
                    min_price_vnd, max_price_vnd = map(float, r.split('-'))
                    min_price_usd = min_price_vnd / exchange_rate
                    max_price_usd = max_price_vnd / exchange_rate
                    range_conditions.append(f"p.discounted_price BETWEEN {min_price_usd} AND {max_price_usd}")
                elif r.endswith('+'):
                    min_price_vnd = float(r[:-1])
                    min_price_usd = min_price_vnd / exchange_rate
                    range_conditions.append(f"p.discounted_price >= {min_price_usd}")
            if range_conditions:
                conditions.append('(' + ' OR '.join(range_conditions) + ')')

        # Apply discount filter
        if discount:
            conditions.append("p.discount_percentage > 0")

        # Combine conditions
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        logger.debug(f"Executing query: {query} with params: {params}")

        # Apply sorting
        if sort == 'price_asc':
            query += " ORDER BY p.discounted_price ASC"
        elif sort == 'price_desc':
            query += " ORDER BY p.discounted_price DESC"
        elif sort == 'discount_desc':
            query += " ORDER BY p.discount_percentage DESC"
        elif sort == 'rating_desc':
            query += " ORDER BY par.avg_rating DESC, par.review_count DESC"
        elif sort == 'sold DESC':
            query += " ORDER BY p.sold DESC"
        else:
            query += " ORDER BY p.id ASC"

        cursor.execute(query, params)
        products = cursor.fetchall()
        logger.debug(f"Products fetched: {len(products)} items")
        exchange_rate = 25000  # 1 USD = 25,000 VND
        result = [
            {
                "id": row['id'],
                "category_id": row['category_id'],
                "name": row['name'],
                "description": row['description'],
                "price": float(row['price']) * exchange_rate if row['price'] is not None else 0.0,
                "discount_percentage": float(row['discount_percentage']) if row['discount_percentage'] is not None else 0.0,
                "discounted_price": float(row['discounted_price']) * exchange_rate if row['discounted_price'] is not None else 0.0,
                "image_url": row['image_url'],
                "sold": row['sold'] if row['sold'] is not None else 0,
                "stock_quantity": row['stock_quantity'] if row['stock_quantity'] is not None else 0,
                "avg_rating": float(row['avg_rating']) if row['avg_rating'] is not None else 0.0,
                "review_count": row['review_count'] if row['review_count'] is not None else 0,
                "student_price": float(row['discounted_price']) * 0.95 * exchange_rate if row['discounted_price'] is not None else 0.0,
                "installment": "0% qua thẻ tín dụng kỳ hạn 3-6..."
            } for row in products
        ]
        close_db_connection(db, cursor)
        return jsonify(result)
    except psycopg2.Error as err:
        logger.error(f"Database error in get_products: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

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
        logger.debug(f"Fetching product ID {product_id}: {product}")
        if product:
            cursor.execute(
                "SELECT comment, u.full_name FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.product_id = %s",
                (product_id,)
            )
            reviews = [{"comment": row['comment'], "user_name": row['full_name']} for row in cursor.fetchall()]
            exchange_rate = 25000  # 1 USD = 25,000 VND
            result = {
                "id": product['id'],
                "category_id": product['category_id'],
                "name": product['name'],
                "description": product['description'],
                "price": float(product['price']) * exchange_rate if product['price'] is not None else 0.0,
                "discount_percentage": float(product['discount_percentage']) if product['discount_percentage'] is not None else 0.0,
                "discounted_price": float(product['discounted_price']) * exchange_rate if product['discounted_price'] is not None else 0.0,
                "image_url": product['image_url'],
                "sold": product['sold'] if product['sold'] is not None else 0,
                "stock_quantity": product['stock_quantity'] if product['stock_quantity'] is not None else 0,
                "avg_rating": float(product['avg_rating']) if product['avg_rating'] is not None else 0.0,
                "review_count": product['review_count'] if product['review_count'] is not None else 0,
                "student_price": float(product['discounted_price']) * 0.95 * exchange_rate if product['discounted_price'] is not None else 0.0,
                "installment": "0% qua thẻ tín dụng kỳ hạn 3-6...",
                "reviews": reviews
            }
            close_db_connection(db, cursor)
            return jsonify(result)
        logger.warning(f"Product not found: {product_id}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    except psycopg2.Error as err:
        logger.error(f"Database error in get_product: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        logger.info(f"Contact form submitted by {name} ({email})")
        return jsonify({'success': True, 'message': 'Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm.'})
    except KeyError as e:
        logger.error(f"Missing field in contact request: {str(e)}")
        return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400
    except psycopg2.Error as err:
        logger.error(f"Database error in contact: {err}")
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

@app.route('/api/reviews/add', methods=['POST'])
def add_review():
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to add review")
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập để đánh giá'}), 401

    try:
        data = request.get_json()
        product_id = data.get('product_id')
        comment = data.get('comment')
        rating = data.get('rating')

        # Validate inputs
        if not all([product_id, comment, rating]):
            logger.error("Missing review information")
            return jsonify({'success': False, 'message': 'Thiếu thông tin đánh giá'}), 400

        product_id = int(product_id)
        rating = int(rating)
        if rating < 1 or rating > 5:
            logger.error(f"Invalid rating value: {rating}")
            return jsonify({'success': False, 'message': 'Điểm đánh giá phải từ 1 đến 5'}), 400
        if len(comment.strip()) == 0:
            logger.error("Empty comment in review")
            return jsonify({'success': False, 'message': 'Bình luận không được để trống'}), 400

        db = get_db_connection()
        cursor = db.cursor()

        # Verify product exists
        cursor.execute('SELECT id FROM products WHERE id = %s', (product_id,))
        product = cursor.fetchone()
        if not product:
            logger.warning(f"Product not found for review: {product_id}")
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại'}), 404

        # Insert review
        cursor.execute('''
            INSERT INTO reviews (user_id, product_id, comment, rating)
            VALUES (%s, %s, %s, %s)
        ''', (session['user_id'], product_id, comment, rating))
        db.commit()

        logger.info(f"Review added for product {product_id} by user {session['user_id']}")
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'message': 'Đánh giá đã được gửi thành công'}), 200
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid data in add_review: {str(e)}")
        return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400
    except psycopg2.Error as err:
        logger.error(f"Database error in add_review: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Lỗi khi gửi đánh giá'}), 500

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to add to cart")
        return jsonify({'success': False, 'message': 'Please log in to add items to cart'}), 401

    try:
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        if quantity < 1:
            logger.error(f"Invalid quantity in add_to_cart: {quantity}")
            return jsonify({'success': False, 'message': 'Quantity must be at least 1'}), 400

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT stock_quantity, discounted_price FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if not product or product['stock_quantity'] < quantity:
            logger.warning(f"Insufficient stock for product {product_id}: requested {quantity}, available {product['stock_quantity'] if product else 'N/A'}")
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'Insufficient stock'}), 400

        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (user_id, product_id) 
            DO UPDATE SET quantity = cart.quantity + EXCLUDED.quantity
            """, (session['user_id'], product_id, quantity))
        db.commit()

        exchange_rate = 25000  # 1 USD = 25,000 VND
        total_price = float(product['discounted_price']) * quantity * exchange_rate
        logger.info(f"Product {product_id} added to cart for user {session['user_id']}: quantity {quantity}, total {total_price} VND")

        close_db_connection(db, cursor)
        return jsonify({
            'success': True,
            'message': 'Product added to cart successfully',
            'total_price': total_price
        })
    except ValueError:
        logger.error("Invalid quantity format in add_to_cart")
        return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
    except psycopg2.Error as err:
        logger.error(f"Database error in add_to_cart: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500
    except KeyError as e:
        logger.error(f"Missing field in add_to_cart request: {str(e)}")
        return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400

@app.route('/api/cart', methods=['GET'])
def get_cart():
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to view cart")
        return jsonify({'success': False, 'message': 'Please log in to view cart'}), 401

    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = """
            SELECT c.product_id, p.name, p.discounted_price, c.quantity, p.image_url
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """
        cursor.execute(query, (session['user_id'],))
        cart_items = cursor.fetchall()
        exchange_rate = 25000  # 1 USD = 25,000 VND
        total_cart_price = 0
        items = []
        for item in cart_items:
            item_total = float(item['discounted_price']) * item['quantity'] * exchange_rate
            total_cart_price += item_total
            items.append({
                'product_id': item['product_id'],
                'name': item['name'],
                'price': float(item['discounted_price']) * exchange_rate,
                'quantity': item['quantity'],
                'image_url': item['image_url'],
                'total': item_total,
                'selected': False  # Mặc định không chọn, để client quản lý trạng thái
            })
        logger.debug(f"Cart fetched for user {session['user_id']}: {len(items)} items, total {total_cart_price} VND")
        close_db_connection(db, cursor)
        return jsonify({
            'success': True,
            'items': items,
            'total_cart_price': total_cart_price
        })
    except psycopg2.Error as err:
        logger.error(f"Database error in get_cart: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to remove from cart")
        return jsonify({'success': False, 'message': 'Please log in to remove items from cart'}), 401

    try:
        data = request.get_json()
        product_id = data['product_id']
        
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
            (session['user_id'], product_id)
        )
        db.commit()
        logger.info(f"Product {product_id} removed from cart for user {session['user_id']}")
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'message': 'Product removed from cart successfully'})
    except KeyError as e:
        logger.error(f"Missing field in remove_from_cart request: {str(e)}")
        return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400
    except psycopg2.Error as err:
        logger.error(f"Database error in remove_from_cart: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

@app.route('/api/cart/checkout', methods=['POST'])
def checkout_cart():
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to checkout")
        return jsonify({'success': False, 'message': 'Please log in to checkout'}), 401

    try:
        data = request.get_json()
        selected_items = data.get('selected_items', [])
        payment_method = data.get('payment_method')

        if not selected_items:
            logger.error("No items selected for checkout")
            return jsonify({'success': False, 'message': 'No items selected for checkout'}), 400

        if not payment_method:
            logger.error("Payment method not specified")
            return jsonify({'success': False, 'message': 'Payment method is required'}), 400

        db = get_db_connection()
        cursor = db.cursor()
        exchange_rate = 25000  # 1 USD = 25,000 VND

        for item in selected_items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            # Get product price and stock
            cursor.execute(
                "SELECT discounted_price, stock_quantity FROM products WHERE id = %s",
                (product_id,)
            )
            product = cursor.fetchone()
            if not product:
                logger.warning(f"Product not found during checkout: {product_id}")
                close_db_connection(db, cursor)
                return jsonify({'success': False, 'message': f'Product {product_id} not found'}), 404
            if product['stock_quantity'] < quantity:
                logger.warning(f"Insufficient stock for product {product_id}: requested {quantity}, available {product['stock_quantity']}")
                close_db_connection(db, cursor)
                return jsonify({'success': False, 'message': f'Insufficient stock for product {product_id}'}), 400

            total_price = float(product['discounted_price']) * quantity * exchange_rate

            # Insert into order_activities
            cursor.execute("""
                INSERT INTO order_activities (user_id, product_id, quantity, total_price, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (session['user_id'], product_id, quantity, total_price, 'Đang chờ giao'))

            # Update stock quantity and sold count
            cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - %s, sold = sold + %s WHERE id = %s",
                (quantity, quantity, product_id)
            )

            # Remove from cart
            cursor.execute(
                "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
                (session['user_id'], product_id)
            )

        db.commit()
        logger.info(f"Checkout successful for user {session['user_id']}: {len(selected_items)} items, payment method {payment_method}")

        message = 'Thanh toán thành công! Đơn hàng của bạn đang chờ giao.'
        redirect_url = None  # Không chuyển hướng, giữ nguyên ở cart.html

        if payment_method == 'online':
            message = 'Thanh toán online chưa được hỗ trợ. Vui lòng chọn thanh toán khi nhận hàng.'
            redirect_url = None

        close_db_connection(db, cursor)
        return jsonify({
            'success': True,
            'message': message,
            'redirect': redirect_url
        })
    except KeyError as e:
        logger.error(f"Missing field in checkout request: {str(e)}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400
    except psycopg2.Error as err:
        logger.error(f"Database error in checkout_cart: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

@app.route('/api/user/profile')
def get_user_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Lấy thông tin cơ bản (trừ mật khẩu)
        cursor.execute(
            "SELECT username, email, full_name, birth_date FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        if not user:
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'User not found'}), 404

        user_info = {
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'birth_date': str(user['birth_date'])
        }

        # Lấy số lượng sản phẩm trong giỏ hàng
        cursor.execute(
            "SELECT COUNT(*) FROM cart WHERE user_id = %s",
            (session['user_id'],)
        )
        cart_count = cursor.fetchone()['COUNT(*)']

        # Lấy số lượng sản phẩm đã mua (tổng quantity từ order_activities)
        cursor.execute(
            "SELECT SUM(quantity) FROM order_activities WHERE user_id = %s",
            (session['user_id'],)
        )
        purchased_count = cursor.fetchone()['SUM(quantity)'] or 0

        # Lấy chi tiết đơn hàng
        cursor.execute(
            """
            SELECT id, product_id, quantity, total_price, status, created_at 
            FROM order_activities WHERE user_id = %s
            """,
            (session['user_id'],)
        )
        orders = []
        for order in cursor.fetchall():
            orders.append({
                'order_id': order['id'],
                'product_id': order['product_id'],
                'quantity': order['quantity'],
                'total_price': order['total_price'],
                'status': order['status'],
                'date': order['created_at'].strftime('%Y-%m-%d %H:%M')
            })

        # Lấy tổng chi tiêu
        cursor.execute(
            "SELECT COALESCE(SUM(total_price), 0) FROM order_activities WHERE user_id = %s",
            (session['user_id'],)
        )
        total_spent = cursor.fetchone()['COALESCE(SUM(total_price), 0)']

        # Lấy danh sách địa chỉ
        cursor.execute(
            "SELECT id, address as address_line, city, postal_code, country FROM addresses WHERE user_id = %s",
            (session['user_id'],)
        )
        addresses = [
            {
                'id': row['id'],
                'address_line': row['address_line'],
                'city': row['city'],
                'postal_code': row['postal_code'],
                'country': row['country']
            } for row in cursor.fetchall()
        ]

        profile_data = {
            'user_info': user_info,
            'cart_count': cart_count,
            'purchased_count': purchased_count,
            'orders': orders,
            'total_spent': total_spent,
            'addresses': addresses
        }

        close_db_connection(db, cursor)
        return jsonify({'success': True, 'data': profile_data})
    except psycopg2.Error as err:
        logger.error(f"Database error in get_user_profile: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

@app.route('/api/user/addresses', methods=['GET'])
def get_addresses():
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to get addresses")
        return jsonify({'success': False, 'message': 'Please log in to view addresses'}), 401

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, address as address_line, city, postal_code, country FROM addresses WHERE user_id = %s",
            (session['user_id'],)
        )
        addresses = [
            {
                'id': row['id'],
                'address_line': row['address_line'],
                'city': row['city'],
                'postal_code': row['postal_code'],
                'country': row['country']
            } for row in cursor.fetchall()
        ]
        logger.info(f"Addresses fetched for user {session['user_id']}: {len(addresses)} addresses")
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'data': {'addresses': addresses}})
    except psycopg2.Error as err:
        logger.error(f"Database error in get_addresses: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500

@app.route('/api/user/addresses/add', methods=['POST'])
def add_address():
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to add address")
        return jsonify({'success': False, 'message': 'Please log in to add an address'}), 401

    try:
        data = request.get_json()
        address_line = data.get('address_line')
        city = data.get('city')
        postal_code = data.get('postal_code')
        country = data.get('country')

        if not all([address_line, city, country]):
            logger.error("Missing required fields in add_address request")
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO addresses (user_id, address, city, postal_code, country) VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], address_line, city, postal_code, country)
        )
        db.commit()
        logger.info(f"Address added for user {session['user_id']}")
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'message': 'Address added successfully'})
    except psycopg2.Error as err:
        logger.error(f"Database error in add_address: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500
    except KeyError as e:
        logger.error(f"Missing field in add_address request: {str(e)}")
        return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400

@app.route('/api/user/addresses/<int:address_id>/edit', methods=['POST'])
def edit_address(address_id):
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to edit address")
        return jsonify({'success': False, 'message': 'Please log in to edit address'}), 401

    try:
        data = request.get_json()
        address_line = data.get('address_line')
        city = data.get('city')
        postal_code = data.get('postal_code')
        country = data.get('country')

        if not all([address_line, city, country]):
            logger.error("Missing required fields in edit_address request")
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE addresses SET address = %s, city = %s, postal_code = %s, country = %s WHERE id = %s AND user_id = %s",
            (address_line, city, postal_code, country, address_id, session['user_id'])
        )
        if cursor.rowcount == 0:
            logger.warning(f"No address found with id {address_id} for user {session['user_id']}")
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'Address not found or not authorized'}), 404
        db.commit()
        logger.info(f"Address {address_id} updated for user {session['user_id']}")
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'message': 'Address updated successfully'})
    except psycopg2.Error as err:
        logger.error(f"Database error in edit_address: {err}")
        close_db_connection(db, cursor)
        return jsonify({'success': False, 'message': 'Database error, please try again later'}), 500
    except KeyError as e:
        logger.error(f"Missing field in edit_address request: {str(e)}")
        return jsonify({'success': False, 'message': f'Missing field: {str(e)}'}), 400

@app.route('/api/user/addresses/<int:address_id>/delete', methods=['POST'])
def delete_address(address_id):
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to delete address")
        return jsonify({'success': False, 'message': 'Please log in to delete address'}), 401

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM addresses WHERE id = %s AND user_id = %s",
            (address_id, session['user_id'])
        )
        if cursor.rowcount == 0:
            logger.warning(f"No address found with id {address_id} for user {session['user_id']}")
            close_db_connection(db, cursor)
            return jsonify({'success': False, 'message': 'Address not found or not authorized'}), 404
        db.commit()
        logger.info(f"Address {address_id} deleted for user {session['user_id']}")
        close_db_connection(db, cursor)
        return jsonify({'success': True, 'message': 'Address deleted successfully'})
    except psycopg2.Error as err:
        logger.error(f"Database error in delete_address: {err}")
        close_db_connection(db, cursor)
        return jsonify_compare({'success': False, 'message': 'Database error'}, 500), 500

if __name__ == '__main__':
    app.run(debug=True)