import mysql.connector
import logging
import os

logger = logging.getLogger(__name__)

def get_db_connection():
    # Lấy thông tin từ biến môi trường, chú ý tên biến phải KHỚP CHÍNH XÁC với Render
    db_host = os.environ.get('MYSQLHOST')
    db_user = os.environ.get('MYSQLUSER')
    db_pass = os.environ.get('MYSQLPASSWORD')
    db_name = os.environ.get('MYSQLDATABASE')
    db_port = os.environ.get('MYSQLPORT', '4000')

    # Log để debug (Xem trong Render Logs)
    print(f"DEBUG: Connecting to DB Host: {db_host}, User: {db_user}, Port: {db_port}")

    if not db_host:
        logger.error("CHƯA CẤU HÌNH BIẾN MÔI TRƯỜNG: MYSQLHOST đang trống!")
        # Không raise lỗi ngay để tránh sập app nếu chạy local, nhưng sẽ báo lỗi connection sau đó

    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name,
            port=int(db_port),
            # TiDB yêu cầu kết nối bảo mật, thêm dòng này để đảm bảo
            ssl_disabled=False
        )
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Lỗi kết nối cơ sở dữ liệu: {err}")
        raise

def close_db_connection(db, cursor=None):
    if cursor:
        cursor.close()
    if db:
        db.close()