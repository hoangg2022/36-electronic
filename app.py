import os
import logging
from flask import Flask, render_template
from controllers import auth_controller, user_controller, product_controller, admin_controller, contact_controller, cart_controller, order_controller, about_controller
from controllers import website_reviews_controller

app = Flask(__name__)
# Dùng secret key từ môi trường, nếu không có mới dùng key random
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key_for_dev')

# Thiết lập thư mục lưu trữ ảnh
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- SỬA LẠI PHẦN NÀY ---
# Không gán cứng localhost. Lấy từ biến môi trường.
app.config['MYSQL_HOST'] = os.environ.get('MYSQLHOST') 
app.config['MYSQL_USER'] = os.environ.get('MYSQLUSER') # Lưu ý: KHÔNG CÓ DẤU GẠCH DƯỚI giữa MYSQL và USER
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQLPASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQLDATABASE')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQLPORT', 4000))
# ------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index/index.html')

# Đăng ký các Blueprints
app.register_blueprint(auth_controller.auth_bp)
app.register_blueprint(user_controller.user_bp)
app.register_blueprint(product_controller.product_bp)
app.register_blueprint(admin_controller.admin_bp)
app.register_blueprint(contact_controller.contact_bp)
app.register_blueprint(cart_controller.cart_bp)
app.register_blueprint(order_controller.order_bp)
app.register_blueprint(about_controller.contact_bp)
app.register_blueprint(website_reviews_controller.website_bp)

if __name__ == '__main__':
    app.run(debug=True)