import os
import logging
from flask import Flask, render_template
from controllers import auth_controller, user_controller, product_controller, admin_controller, contact_controller, cart_controller, order_controller, about_controller
from controllers import website_reviews_controller
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_secure_random_key')  # Use environment variable in production

# Thiết lập thư mục lưu trữ ảnh
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Đảm bảo thư mục uploads tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Thiết lập cấu hình MySQL
app.config['MYSQL_HOST'] = os.environ.get('MYSQLHOST', 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQLPORT', 4000))
app.config['MYSQL_USER'] = os.environ.get('MYSQLUSER', '6kSJ9qn8Nkb2g3r.root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQLPASSWORD', 'FHvZQsNZ5uL1OtMs')
app.config['MYSQL_DB'] = os.environ.get('MYSQLDATABASE', 'test')
app.config['MYSQL_SSL_CA'] = os.environ.get('MYSQL_SSL_CA', '<CA_PATH>')
app.config['MYSQL_SSL_VERIFY_CERT'] = True
app.config['MYSQL_SSL_VERIFY_IDENTITY'] = True

# Thiết lập logging để debug
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