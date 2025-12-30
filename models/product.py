from .database import get_db_connection, close_db_connection
import logging

logger = logging.getLogger(__name__)

class Product:
    @staticmethod
    def get_all(category_id=None, search_query=None, discount=False, sort=None, price_range=None):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            
            # Query cơ bản
            query = """
                SELECT p.id, p.category_id, p.name, p.description, p.price, p.discount_percentage, p.discounted_price,
                    p.image_url, p.sold, p.stock_quantity, par.avg_rating, par.review_count
                FROM products p
                LEFT JOIN product_avg_rating par ON p.id = par.product_id
            """
            params = []
            conditions = []

            # Xử lý điều kiện lọc
            if category_id:
                conditions.append("p.category_id = %s")
                params.append(category_id)
            
            if search_query:
                # Postgres dùng ILIKE để tìm kiếm không phân biệt hoa thường
                conditions.append("p.name ILIKE %s")
                params.append(f"%{search_query}%")
            
            if discount:
                conditions.append("p.discount_percentage > 0")

            if price_range:
                price_conditions = []
                ranges = price_range.split(',')
                for range_str in ranges:
                    try:
                        # Giả sử range gửi lên là tiền Việt (VND), chia 25000 ra USD
                        if '-' in range_str:
                            min_v, max_v = map(float, range_str.split('-'))
                            price_conditions.append("(p.discounted_price BETWEEN %s AND %s)")
                            params.extend([min_v/25000, max_v/25000])
                        elif range_str.endswith('+'): # Ví dụ "20000000+"
                             min_v = float(range_str[:-1])
                             price_conditions.append("(p.discounted_price >= %s)")
                             params.append(min_v/25000)
                    except ValueError:
                        continue
                if price_conditions:
                    conditions.append(f"({' OR '.join(price_conditions)})")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Xử lý sắp xếp
            if sort == "name_asc": query += " ORDER BY p.name ASC"
            elif sort == "name_desc": query += " ORDER BY p.name DESC"
            elif sort == "price_asc": query += " ORDER BY p.discounted_price ASC"
            elif sort == "price_desc": query += " ORDER BY p.discounted_price DESC"
            elif sort == "sold_desc": query += " ORDER BY p.sold DESC"
            elif sort == "rating_desc": query += " ORDER BY par.avg_rating DESC NULLS LAST"
            elif sort == "discount_desc": query += " ORDER BY p.discount_percentage DESC"
            else: query += " ORDER BY p.id ASC"

            cursor.execute(query, params)
            products = cursor.fetchall() # Trả về list of dicts (RealDictCursor)
            
            return products

        except Exception as e:
            logger.error(f"Lỗi Model Product get_all: {e}")
            return []
        finally:
            # Đảm bảo đóng kết nối dù có lỗi hay không
            if 'db' in locals(): close_db_connection(db, cursor)

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
            return product
        except Exception as e:
            logger.error(f"Lỗi Model Product get_by_id {product_id}: {e}")
            return None
        finally:
             if 'db' in locals(): close_db_connection(db, cursor)