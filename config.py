import mysql.connector
import logging
import os
from werkzeug.utils import secure_filename

# Thiết lập thư mục lưu trữ ảnh
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Đảm bảo thư mục uploads tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Thiết lập logging để debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hàm kiểm tra phần mở rộng tệp
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Hàm tạo kết nối MySQL
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",  # Bảo mật bằng biến môi trường trong production
            database="36_electronic_shop"
        )
    except mysql.connector.Error as err:
        logger.error(f"Lỗi kết nối cơ sở dữ liệu: {err}")
        raise

# Đóng kết nối MySQL an toàn
def close_db_connection(db, cursor=None):
    if cursor:
        cursor.close()
    if db:
        db.close()