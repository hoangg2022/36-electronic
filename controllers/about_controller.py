from flask import Blueprint, render_template
import logging

# Đổi tên biến từ contact_bp -> about_bp
about_bp = Blueprint('about', __name__)
logger = logging.getLogger(__name__)

@about_bp.route('/about')
def contact_page():
    return render_template('about/about.html')