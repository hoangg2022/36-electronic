from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
from models.order import Order
from config import logger

order_bp = Blueprint('order', __name__)

# API thanh toán giỏ hàng
@order_bp.route('/api/cart/checkout', methods=['POST'])
def checkout_cart():
    if 'user_id' not in session:
        logger.warning("Thử thanh toán không được phép")
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập để thanh toán'}), 401

    try:
        data = request.get_json()
        selected_items = data.get('selected_items', [])
        payment_method = data.get('payment_method')
        address = data.get('address')
        phone = data.get('phone')

        # Kiểm tra địa chỉ và SĐT
        if not address or not phone:
            return jsonify({'success': False, 'message': 'Vui lòng nhập địa chỉ và số điện thoại'}), 400

        # Kiểm tra phương thức thanh toán
        if payment_method != 'cod':
            return jsonify({'success': False, 'message': 'Chúng tôi chưa hỗ trợ thanh toán online'}), 400

        # Gọi model xử lý đơn hàng
        success, message = Order.checkout(
            session['user_id'],
            selected_items,
            payment_method,
            address,
            phone
        )

        if success:
            logger.info(f"Thanh toán thành công cho người dùng {session['user_id']}: {len(selected_items)} mục, phương thức {payment_method}")
            return jsonify({
                'success': True,
                'message': 'Thanh toán thành công! Đơn hàng của bạn đang chờ giao.'
            })
        else:
            logger.warning(f"Thanh toán thất bại: {message}")
            return jsonify({'success': False, 'message': message}), 400

    except KeyError as e:
        logger.error(f"Thiếu trường trong yêu cầu thanh toán: {str(e)}")
        return jsonify({'success': False, 'message': f'Thiếu trường: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Lỗi xử lý thanh toán: {str(e)}")
        return jsonify({'success': False, 'message': 'Lỗi máy chủ'}), 500


# Trang quản lý đơn hàng admin (trả về html)
@order_bp.route('/admin/orders')
def admin_orders():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào quản lý đơn hàng")
        return redirect(url_for('user.login'))
    return render_template('admin/manage_orders.html')


# API lấy danh sách đơn hàng cho admin
@order_bp.route('/api/admin/orders')
def get_admin_orders():
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Truy cập không được phép vào danh sách đơn hàng admin")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401

    try:
        pending_orders, completed_orders = Order.get_admin_orders()
        return jsonify({
            'success': True,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders
        })
    except Exception as e:
        logger.error(f"Lỗi khi lấy đơn hàng admin: {str(e)}")
        return jsonify({'success': False, 'message': 'Lỗi máy chủ'}), 500


# API cập nhật trạng thái đơn hàng cho admin
@order_bp.route('/api/admin/update_order_status/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        logger.warning("Thử cập nhật trạng thái đơn hàng không được phép")
        return jsonify({'success': False, 'message': 'Không được phép'}), 401
    try:
        data = request.get_json()
        status = data['status']
        success, message = Order.update_order_status(order_id, status)
        if success:
            logger.info(f"Admin đã cập nhật trạng thái đơn hàng ID: {order_id} thành {status}")
            return jsonify({'success': True, 'message': 'Trạng thái đơn hàng được cập nhật thành công'})
        else:
            return jsonify({'success': False, 'message': message}), 400
    except KeyError as e:
        logger.error(f"Thiếu trường trong update_order_status: {str(e)}")
        return jsonify({'success': False, 'message': 'Thiếu trường'}), 400
    except Exception as e:
        logger.error(f"Lỗi cập nhật trạng thái đơn hàng: {str(e)}")
        return jsonify({'success': False, 'message': 'Lỗi máy chủ'}), 500
