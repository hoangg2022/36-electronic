let cartItems = [];

function renderCart() {
    const cartList = document.getElementById('cartList');
    const cartTotal = document.getElementById('cartTotal');
    const checkoutBtn = document.querySelector('.checkout-btn');
    const paymentMethods = document.getElementById('paymentMethods');

    cartList.innerHTML = '';
    if (cartItems.length === 0) {
        cartList.innerHTML = '<tr><td colspan="7" class="empty-cart">Giỏ hàng của bạn đang trống!</td></tr>';
        cartTotal.textContent = 'Tổng: 0 VNĐ';
        checkoutBtn.style.display = 'none';
        paymentMethods.style.display = 'none';
    } else {
        checkoutBtn.style.display = 'block';
        let total = 0;
        cartItems.forEach((item, index) => {
            const itemTotal = item.price * item.quantity;
            if (item.selected) total += itemTotal;
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><input type="checkbox" ${item.selected ? 'checked' : ''} onchange="toggleItem(${index})"></td>
                <td><img src="${item.image_url}" alt="${item.name}"></td>
                <td>${item.name}</td>
                <td>${item.price.toLocaleString('vi-VN')} VNĐ</td>
                <td><input type="number" min="1" value="${item.quantity}" onchange="updateQuantity(${index}, this.value)"></td>
                <td>${itemTotal.toLocaleString('vi-VN')} VNĐ</td>
                <td><button onclick="removeFromCart(${item.product_id})"><i class="fas fa-trash"></i></button></td>
            `;
            cartList.appendChild(row);
        });
        cartTotal.textContent = `Tổng: ${total.toLocaleString('vi-VN')} VNĐ`;
        document.getElementById('selectAll').checked = cartItems.every(item => item.selected);
    }
}

function loadCart() {
    fetch('/api/cart')
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                Swal.fire('Lỗi', data.message, 'error').then(() => {
                    window.location.href = '/login';
                });
                return;
            }
            cartItems = data.items.map(item => ({
                ...item,
                selected: cartItems.find(i => i.product_id === item.product_id)?.selected || false
            }));
            renderCart();
        })
        .catch(error => {
            console.error('Lỗi tải giỏ hàng:', error);
            Swal.fire('Lỗi', 'Không thể tải giỏ hàng', 'error');
        });
}

function toggleItem(index) {
    cartItems[index].selected = !cartItems[index].selected;
    renderCart();
}

function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll').checked;
    cartItems.forEach(item => item.selected = selectAll);
    renderCart();
}

function updateQuantity(index, quantity) {
    const item = cartItems[index];
    const newQuantity = parseInt(quantity) || 1;
    fetch('/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `product_id=${item.product_id}&quantity=${newQuantity - item.quantity}`
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                loadCart();
            } else {
                Swal.fire('Lỗi', result.message, 'error');
            }
        })
        .catch(error => {
            console.error('Lỗi cập nhật số lượng:', error);
            Swal.fire('Lỗi', 'Không thể cập nhật số lượng', 'error');
        });
}

function removeFromCart(productId) {
    fetch('/api/cart/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire('Thành công', data.message, 'success');
                loadCart();
            } else {
                Swal.fire('Lỗi', data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Lỗi xóa sản phẩm:', error);
            Swal.fire('Lỗi', 'Không thể xóa sản phẩm', 'error');
        });
}

function showPaymentMethods() {
    const selectedItems = cartItems.filter(item => item.selected);
    if (selectedItems.length === 0) {
        Swal.fire('Cảnh báo', 'Vui lòng chọn ít nhất một sản phẩm để thanh toán!', 'warning');
        return;
    }
    document.getElementById('paymentMethods').style.display = 'block';
}

function checkout(paymentMethod) {
    const selectedItems = cartItems.filter(item => item.selected);
    if (selectedItems.length === 0) {
        Swal.fire('Cảnh báo', 'Vui lòng chọn ít nhất một sản phẩm để thanh toán!', 'warning');
        return;
    }

    if (paymentMethod === 'online') {
        Swal.fire({
            title: 'Không hỗ trợ',
            text: 'Chúng tôi chưa có dịch vụ thanh toán online. Vui lòng chọn "Thanh toán khi nhận hàng".',
            icon: 'error',
            confirmButtonText: 'OK'
        });
        return;
    }

    Swal.fire({
        title: 'Xác nhận',
        text: 'Bạn có chắc muốn thanh toán khi nhận hàng?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Có',
        cancelButtonText: 'Hủy'
    }).then(result => {
        if (result.isConfirmed) {
            fetch('/api/cart/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ selected_items: selectedItems, payment_method: 'cod' })
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        Swal.fire('Thành công', result.message, 'success').then(() => {
                            loadCart();
                        });
                    } else {
                        Swal.fire('Lỗi', result.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Lỗi thanh toán:', error);
                    Swal.fire('Lỗi', 'Không thể thanh toán', 'error');
                });
        }
    });
}

function setupUserMenu() {
    fetch('/api/check_login')
        .then(response => response.json())
        .then(data => {
            const userMenu = document.getElementById('userMenu');
            const userNameSpan = document.getElementById('userName');
            const userDropdown = document.getElementById('userDropdown');
            const logoutBtn = document.getElementById('logoutBtn');

            if (data.logged_in && userNameSpan) {
                userNameSpan.textContent = data.full_name;
                if (userMenu) {
                    userMenu.onclick = () => {
                        userDropdown.style.display = userDropdown.style.display === 'block' ? 'none' : 'block';
                    };
                }
            } else if (userMenu && userNameSpan) {
                userNameSpan.textContent = 'Đăng nhập';
                if (userDropdown) userDropdown.style.display = 'none';
                userMenu.onclick = () => window.location.href = '/login';
            }

            if (logoutBtn) {
                logoutBtn.onclick = (e) => {
                    e.preventDefault();
                    fetch('/api/logout', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                Swal.fire('Thành công', 'Đã đăng xuất!', 'success').then(() => {
                                    window.location.href = data.redirect;
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Lỗi đăng xuất:', error);
                            Swal.fire('Lỗi', 'Không thể đăng xuất', 'error');
                        });
                };
            }
        })
        .catch(error => {
            console.error('Lỗi kiểm tra đăng nhập:', error);
        });
}

window.onload = () => {
    loadCart();
    setupUserMenu();
};