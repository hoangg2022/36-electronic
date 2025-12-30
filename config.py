import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
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

# Hàm tạo kết nối Database (Đã chuyển sang PostgreSQL)
def get_db_connection():
    try:
        # Lấy URL từ biến môi trường Render
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
             raise ValueError("DATABASE_URL chưa được thiết lập!")
             
        # Kết nối Postgres
        return psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    except Exception as err:
        logger.error(f"Lỗi kết nối cơ sở dữ liệu: {err}")
        raise

# Đóng kết nối an toàn
def close_db_connection(db, cursor=None):
    if cursor:
        cursor.close()
    if db:
        db.close()