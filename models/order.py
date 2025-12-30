# models/order.py
from .database import get_db_connection, close_db_connection
import logging

logger = logging.getLogger(__name__)

class Order:
    @staticmethod
    def checkout(user_id, selected_items, payment_method, address, phone):
        try:
            db = get_db_connection()
            cursor = db.cursor()

            for item in selected_items:
                product_id = item['product_id']
                quantity = item['quantity']
                price = item['price']
                total_price = quantity * price

                # 1. Thêm đơn hàng kèm địa chỉ và SĐT
                cursor.execute("""
                    INSERT INTO order_activities (user_id, product_id, quantity, total_price, status, address, phone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, product_id, quantity, total_price, "Đang chờ giao", address, phone))

                # 2. Xóa khỏi cart
                cursor.execute("""
                    DELETE FROM cart WHERE user_id = %s AND product_id = %s
                """, (user_id, product_id))

                # 3. Cập nhật tồn kho và sold
                cursor.execute("""
                    UPDATE products
                    SET sold = sold + %s,
                        stock_quantity = stock_quantity - %s
                    WHERE id = %s AND stock_quantity >= %s
                """, (quantity, quantity, product_id, quantity))

            db.commit()
            close_db_connection(db, cursor)
            return True, "Đặt hàng thành công"
        except Exception as e:
            logger.error(f"Lỗi khi xử lý thanh toán đơn hàng: {e}")
            return False, "Không thể hoàn tất thanh toán"



    @staticmethod
    def create(user_id, product_id, quantity, total_price, status="Đang chờ giao"):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO order_activities (user_id, product_id, quantity, total_price, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, product_id, quantity, total_price, status))
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi tạo đơn hàng: {e}")
            return False

    @staticmethod
    def get_by_user_id(user_id):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "SELECT id, product_id, quantity, total_price, status, created_at FROM order_activities WHERE user_id = %s",
                (user_id,)
            )
            orders = cursor.fetchall()
            close_db_connection(db, cursor)
            return orders
        except Exception as e:
            logger.error(f"Lỗi khi lấy đơn hàng cho user_id {user_id}: {e}")
            return None

    @staticmethod
    def get_all():
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                SELECT o.id, u.full_name, p.name, o.quantity, o.total_price, o.status, o.delivered_at, o.phone, o.address
                FROM order_activities o
                JOIN users u ON o.user_id = u.id
                JOIN products p ON o.product_id = p.id
            """)
            orders = cursor.fetchall()
            close_db_connection(db, cursor)
            return orders
        except Exception as e:
            logger.error(f"Lỗi khi lấy tất cả đơn hàng: {e}")
            return None

    @staticmethod
    def update_status(order_id, status):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            if status == 'Đã giao':
                cursor.execute(
                    "UPDATE order_activities SET status = %s, delivered_at = NOW() WHERE id = %s",
                    (status, order_id)
                )
            else:
                cursor.execute(
                    "UPDATE order_activities SET status = %s, delivered_at = NULL WHERE id = %s",
                    (status, order_id)
                )
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật trạng thái đơn hàng ID {order_id}: {e}")
            return False

    @staticmethod
    def delete(order_id):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM order_activities WHERE id = %s", (order_id,))
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa đơn hàng ID {order_id}: {e}")
            return False