@staticmethod
    def get_by_username(username):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            # Đảm bảo lấy đủ các cột cần thiết
            cursor.execute("SELECT id, username, password, full_name, role FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            close_db_connection(db, cursor)
            return user # Trả về Dictionary (nhờ RealDictCursor trong config.py)
        except Exception as e:
            logger.error(f"Lỗi khi lấy người dùng theo username: {e}")
            return None