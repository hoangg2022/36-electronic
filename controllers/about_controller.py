from flask import Blueprint, request, jsonify, render_template
import logging

contact_bp = Blueprint('about', __name__)
logger = logging.getLogger(__name__)

# Route cho trang liên hệ
@contact_bp.route('/about')
def contact_page():
    return render_template('/about/about.html')