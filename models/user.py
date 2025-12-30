# models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_db_connection, close_db_connection
import logging

logger = logging.getLogger(__name__)

class User:
    @staticmethod
    def get_by_username(username):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT id, username, password, full_name, role FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            close_db_connection(db, cursor)
            return user
        except Exception as e:
            logger.error(f"Lỗi khi lấy người dùng theo username: {e}")
            return None

    @staticmethod
    def get_by_id(user_id):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "SELECT id, username, email, full_name, birth_date FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
            close_db_connection(db, cursor)
            return user
        except Exception as e:
            logger.error(f"Lỗi khi lấy người dùng theo ID: {e}")
            return None

    @staticmethod
    def create(username, email, password, full_name, birth_date, role='customer'):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            hashed_password = generate_password_hash(password)
            # Validate role
            if role not in ['customer', 'admin']:
                logger.error(f"Role không hợp lệ: {role}")
                return False
            sql = "INSERT INTO users (username, email, password, full_name, birth_date, role) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (username, email, hashed_password, full_name, birth_date, role))
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi tạo người dùng: {e}")
            return False

    @staticmethod
    def update(user_id, full_name, email, birth_date, password=None, role=None):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            query = "UPDATE users SET full_name = %s, email = %s, birth_date = %s"
            values = [full_name, email, birth_date]
            if password:
                query += ", password = %s"
                values.append(generate_password_hash(password))
            if role and role in ['customer', 'admin']:  # Validate role
                query += ", role = %s"
                values.append(role)
            query += " WHERE id = %s"
            values.append(user_id)
            cursor.execute(query, values)
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật người dùng: {e}")
            return False
    @staticmethod
    def delete(user_id):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa người dùng: {e}")
            return False


    @staticmethod
    def check_email_exists(email, exclude_user_id=None):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            query = "SELECT id FROM users WHERE email = %s"
            params = [email]
            if exclude_user_id:
                query += " AND id != %s"
                params.append(exclude_user_id)
            cursor.execute(query, params)
            result = cursor.fetchone()
            close_db_connection(db, cursor)
            return result is not None
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra email: {e}")
            return False