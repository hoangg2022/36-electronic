# controllers/contact_controller.py
from flask import Blueprint, request, jsonify, render_template
import logging

contact_bp = Blueprint('contact', __name__)
logger = logging.getLogger(__name__)

# Route cho trang liên hệ
@contact_bp.route('/contact')
def contact_page():
    return render_template('contact.html')

# API xử lý biểu mẫu liên hệ
@contact_bp.route('/api/contact', methods=['POST'])
def contact():
    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        logger.info(f"Biểu mẫu liên hệ được gửi bởi {name} ({email})")
        return jsonify({'success': True, 'message': 'Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm.'})
    except KeyError as e:
        logger.error(f"Thiếu trường trong yêu cầu liên hệ: {str(e)}")
        return jsonify({'success': False, 'message': f'Thiếu trường: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Lỗi khi xử lý liên hệ: {e}")
        return jsonify({'success': False, 'message': 'Lỗi, vui lòng thử lại sau'}), 500