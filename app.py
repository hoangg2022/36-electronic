import os
import logging
from flask import Flask, render_template
# Import các controller
from controllers import auth_controller, user_controller, product_controller, admin_controller, contact_controller, cart_controller, order_controller, about_controller
from controllers import website_reviews_controller

app = Flask(__name__)
# Lấy Secret Key từ biến môi trường trên Render
app.secret_key = os.environ.get('SECRET_KEY', 'default_dev_key_123')

# Thiết lập thư mục lưu trữ ảnh (Render chỉ cho phép lưu tạm, không vĩnh viễn với gói Free)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Đảm bảo thư mục uploads tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- ĐÃ XÓA CẤU HÌNH MYSQL CŨ ---

# Thiết lập logging để debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index/index.html')

# Đăng ký các Blueprints (Giữ nguyên phần này vì là cấu trúc mới của bạn)
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