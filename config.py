import mysql.connector
import logging
import os
from werkzeug.utils import secure_filename

# Thiết lập thư mục lưu trữ ảnh
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Hàm tạo kết nối MySQL
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.environ.get('MYSQLHOST'),
            user=os.environ.get('MYSQLUSER'),
            password=os.environ.get('MYSQLPASSWORD'),
            database=os.environ.get('MYSQLDATABASE'),
            port=int(os.environ.get('MYSQLPORT', 4000)),
            ssl_disabled=False
        )
    except mysql.connector.Error as err:
        logger.error(f"Lỗi kết nối cơ sở dữ liệu: {err}")
        raise

def close_db_connection(db, cursor=None):
    if cursor:
        cursor.close()
    if db:
        db.close()