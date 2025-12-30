from flask import Blueprint, jsonify
from models.category import CategoryModel
from config import logger

category_bp = Blueprint('category', __name__)

@category_bp.route('/api/categories')
def get_categories():
    categories = CategoryModel.get_categories()
    return jsonify(categories)