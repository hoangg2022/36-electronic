from flask import Blueprint, render_template, request, jsonify
from models.product import Product
from models.category import Category
import logging

product_bp = Blueprint('product', __name__)
logger = logging.getLogger(__name__)

# --- SỬA TÊN HÀM Ở DÒNG DƯỚI TỪ index() THÀNH products() ---
@product_bp.route('/products')
def products():
    """Render trang danh sách sản phẩm (HTML)."""
    category_id = request.args.get('category')
    return render_template('products/products.html', category_id=category_id)

@product_bp.route('/api/products', methods=['GET'])
def get_products_api():
    """API trả về JSON danh sách sản phẩm."""
    try:
        # Lấy tham số từ URL
        category_id = request.args.get('category_id')
        search_query = request.args.get('search')
        sort_option = request.args.get('sort')
        price_range = request.args.get('price_range')
        discount = request.args.get('discount') == 'true'

        # Gọi Model
        products = Product.get_all(
            category_id=category_id, 
            search_query=search_query, 
            discount=discount, 
            sort=sort_option, 
            price_range=price_range
        )
        
        if products is None:
            products = []

        # Xử lý dữ liệu trước khi trả về (Convert Decimal -> float)
        processed_products = []
        for p in products:
            item = dict(p) # Copy dict
            if item.get('price'): item['price'] = float(item['price'])
            if item.get('discount_percentage'): item['discount_percentage'] = float(item['discount_percentage'])
            if item.get('discounted_price'): item['discounted_price'] = float(item['discounted_price'])
            if item.get('avg_rating'): item['avg_rating'] = float(item['avg_rating'])
            
            processed_products.append(item)

        return jsonify(processed_products)

    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách sản phẩm API: {e}")
        return jsonify({'error': str(e)}), 500

@product_bp.route('/api/product/<int:product_id>', methods=['GET'])
def get_product_detail_api(product_id):
    """API lấy chi tiết 1 sản phẩm."""
    try:
        product = Product.get_by_id(product_id)
        if product:
            if product.get('price'): product['price'] = float(product['price'])
            if product.get('discount_percentage'): product['discount_percentage'] = float(product['discount_percentage'])
            if product.get('discounted_price'): product['discounted_price'] = float(product['discounted_price'])
            if product.get('avg_rating'): product['avg_rating'] = float(product['avg_rating'])
            
            return jsonify(product)
        else:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
    except Exception as e:
        logger.error(f"Lỗi khi lấy chi tiết sản phẩm {product_id}: {e}")
        return jsonify({'error': str(e)}), 500

@product_bp.route('/api/categories', methods=['GET'])
def get_categories_api():
    """API lấy danh sách danh mục."""
    try:
        categories = Category.get_all()
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh mục: {e}")
        return jsonify([]), 500