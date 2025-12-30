from .database import get_db_connection, close_db_connection
import logging

logger = logging.getLogger(__name__)

class Product:
    @staticmethod
    def get_all(category_id=None, search_query=None, discount=False, sort=None, price_range=None):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            query = """
                SELECT p.id, p.category_id, p.name, p.description, p.price, p.discount_percentage, p.discounted_price,
                    p.image_url, p.sold, p.stock_quantity, par.avg_rating, par.review_count
                FROM products p
                LEFT JOIN product_avg_rating par ON p.id = par.product_id
            """
            params = []
            conditions = []

            if category_id:
                conditions.append("p.category_id = %s")
                params.append(category_id)
            if search_query:
                conditions.append("p.name LIKE %s")
                params.append(f"%{search_query}%")
            if discount:
                conditions.append("p.discount_percentage > 0")

            if price_range:
                price_conditions = []
                ranges = price_range.split(',')
                for range_str in ranges:
                    try:
                        min_price, max_price = map(float, range_str.split('-'))
                        min_price /= 25000
                        max_price /= 25000
                        price_conditions.append(f"(p.discounted_price >= %s AND p.discounted_price <= %s)")
                        params.extend([min_price, max_price])
                    except ValueError:
                        logger.warning(f"Định dạng price_range không hợp lệ: {range_str}")
                        continue
                if price_conditions:
                    conditions.append(f"({' OR '.join(price_conditions)})")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            if sort:
                if sort == "name_asc":
                    query += " ORDER BY p.name ASC"
                elif sort == "name_desc":
                    query += " ORDER BY p.name DESC"
                elif sort == "price_asc":
                    query += " ORDER BY p.price ASC"
                elif sort == "price_desc":
                    query += " ORDER BY p.price DESC"
                elif sort in ("sold_desc", "sold DESC"):
                    query += " ORDER BY COALESCE(p.sold, 0) DESC, p.id ASC"
                elif sort == "rating_desc":
                    query += " ORDER BY COALESCE(par.avg_rating, 0) DESC, p.id ASC"
                elif sort == "discount_desc":
                    query += " ORDER BY COALESCE(p.discount_percentage, 0) DESC, p.id ASC"
                elif sort == "discounted_price_asc":
                    query += " ORDER BY p.discounted_price ASC"
                elif sort == "discounted_price_desc":
                    query += " ORDER BY p.discounted_price DESC"
                else:
                    query += " ORDER BY p.id ASC"
            else:
                query += " ORDER BY p.id ASC"

            cursor.execute(query, params)
            products = cursor.fetchall()
            close_db_connection(db, cursor)
            return products
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách sản phẩm: {e}")
            return None

    @staticmethod
    def get_by_id(product_id):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                SELECT 
                    p.id, p.category_id, p.name, p.description, p.price,
                    p.discount_percentage, p.discounted_price, p.image_url,
                    p.stock_quantity, p.sold, par.avg_rating, par.review_count
                FROM products p
                LEFT JOIN product_avg_rating par ON p.id = par.product_id
                WHERE p.id = %s
            """, (product_id,))
            product = cursor.fetchone()
            close_db_connection(db, cursor)
            return product
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None

    @staticmethod
    def create(category_id, name, description, price, discount_percentage, image_url, stock_quantity):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO products (category_id, name, description, price, discount_percentage, image_url, stock_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (category_id, name, description, price, discount_percentage, image_url, stock_quantity)
            )
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi thêm sản phẩm: {e}")
            return False

    @staticmethod
    def update(product_id, name, category_id, description, price, discount_percentage, image_url, stock_quantity):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "UPDATE products SET name = %s, category_id = %s, description = %s, price = %s, discount_percentage = %s, image_url = %s, stock_quantity = %s WHERE id = %s",
                (name, category_id, description, price, discount_percentage, image_url, stock_quantity, product_id)
            )
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật sản phẩm ID {product_id}: {e}")
            return False

    @staticmethod
    def delete(product_id):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa sản phẩm ID {product_id}: {e}")
            return False

    @staticmethod
    def decrease_stock(product_id, quantity):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                UPDATE products
                SET stock_quantity = stock_quantity - %s
                WHERE id = %s AND stock_quantity >= %s
            """, (quantity, product_id, quantity))
            db.commit()
            affected = cursor.rowcount
            close_db_connection(db, cursor)
            return affected > 0  # Trả về True nếu cập nhật thành công
        except Exception as e:
            logger.error(f"Lỗi khi giảm tồn kho sản phẩm {product_id}: {e}")
            return False

    @staticmethod
    def increase_stock(product_id, quantity):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                UPDATE products
                SET stock_quantity = stock_quantity + %s
                WHERE id = %s
            """, (quantity, product_id))
            db.commit()
            close_db_connection(db, cursor)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi tăng tồn kho sản phẩm {product_id}: {e}")
            return False
