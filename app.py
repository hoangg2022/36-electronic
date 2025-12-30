import os
import logging
from flask import Flask, render_template
# Import các controller
from controllers import auth_controller, user_controller, product_controller, admin_controller, contact_controller, cart_controller, order_controller, about_controller
from controllers import website_reviews_controller

app = Flask(__name__)
# Lấy Secret Key từ biến môi trường
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key_12345')

# Thiết lập thư mục lưu trữ ảnh
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- QUAN TRỌNG: Đã xóa toàn bộ cấu hình MySQL ở đây ---

# Thiết lập logging
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
# Sửa dòng này: dùng about_bp
app.register_blueprint(about_controller.about_bp)
app.register_blueprint(website_reviews_controller.website_bp)

if __name__ == '__main__':
    app.run(debug=True)