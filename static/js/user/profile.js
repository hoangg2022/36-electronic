let currentTab = 'account';

function formatVND(amount) {
    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' VNĐ';
}

function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
    document.getElementById(tabId).style.display = 'block';
    document.querySelectorAll('.nav-tabs a').forEach(a => a.classList.remove('active'));
    document.querySelector(`.nav-tabs a[href="#${tabId}"]`).classList.add('active');
    currentTab = tabId;
    if (tabId === 'account') loadProfile();
    if (tabId === 'address') loadAddresses();
    if (tabId === 'orders') loadOrders();
    if (tabId === 'membership') loadMembership();
}

function loadProfile() {
    fetch('/api/user/profile')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const profile = data.data.user_info;
                document.getElementById('username').value = profile.username;
                document.getElementById('email').value = profile.email;
                document.getElementById('full_name').value = profile.full_name;
                document.getElementById('birth_date').value = profile.birth_date;
            } else {
                Swal.fire('Lỗi', data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Lỗi tải thông tin:', error);
            Swal.fire('Lỗi', 'Không thể tải thông tin', 'error');
        });
}

function loadAddresses() {
    fetch('/api/user/addresses')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const addressList = document.getElementById('addressList');
                addressList.innerHTML = '';
                if (data.data.addresses.length === 0) {
                    addressList.innerHTML = '<tr><td colspan="5">Chưa có địa chỉ nào.</td></tr>';
                } else {
                    data.data.addresses.forEach(address => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                                    <td data-label="Địa chỉ">${address.address_line}</td>
                                    <td data-label="Thành phố">${address.city}</td>
                                    <td data-label="Mã bưu điện">${address.postal_code || 'N/A'}</td>
                                    <td data-label="Quốc gia">${address.country}</td>
                                    <td class="address-actions" data-label="Hành động">
                                        <button class="edit-btn" onclick="editAddress(${address.id}, '${address.address_line}', '${address.city}', '${address.postal_code || ''}', '${address.country}')">Sửa</button>
                                        <button onclick="deleteAddress(${address.id})">Xóa</button>
                                    </td>
                                `;
                        addressList.appendChild(row);
                    });
                }
            } else {
                Swal.fire('Lỗi', data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Lỗi tải địa chỉ:', error);
            Swal.fire('Lỗi', 'Không thể tải địa chỉ', 'error');
        });
}

function addAddress() {
    Swal.fire({
        title: 'Thêm địa chỉ mới',
        html: `
                    <input id="swal-address-line" class="swal2-input" placeholder="Địa chỉ" required>
                    <input id="swal-city" class="swal2-input" placeholder="Thành phố" required>
                    <input id="swal-postal-code" class="swal2-input" placeholder="Mã bưu điện">
                    <input id="swal-country" class="swal2-input" placeholder="Quốc gia" required>
                `,
        showCancelButton: true,
        confirmButtonText: 'Thêm',
        cancelButtonText: 'Hủy',
        preConfirm: () => {
            const address_line = document.getElementById('swal-address-line').value;
            const city = document.getElementById('swal-city').value;
            const postal_code = document.getElementById('swal-postal-code').value;
            const country = document.getElementById('swal-country').value;
            if (!address_line || !city || !country) {
                Swal.showValidationMessage('Vui lòng điền các trường bắt buộc');
                return false;
            }
            return { address_line, city, postal_code, country };
        }
    }).then(result => {
        if (result.isConfirmed) {
            fetch('/api/user/addresses/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(result.value)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire('Thành công', 'Địa chỉ đã được thêm', 'success').then(() => loadAddresses());
                    } else {
                        Swal.fire('Lỗi', data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Lỗi thêm địa chỉ:', error);
                    Swal.fire('Lỗi', 'Không thể thêm địa chỉ', 'error');
                });
        }
    });
}

function loadOrders() {
    fetch('/api/user/profile')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const orders = data.data.orders;
                const orderList = document.getElementById('orderList');
                orderList.innerHTML = '';
                orders.forEach(order => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                                <td data-label="Mã đơn">${order.order_id}</td>
                                <td data-label="Ngày đặt">${order.date}</td>
                                <td data-label="Tổng tiền">${formatVND(order.total_price)}</td>
                                <td data-label="Trạng thái">${order.status}</td>
                            `;
                    orderList.appendChild(row);
                });
                document.getElementById('purchasedCount').textContent = data.data.purchased_count;
                document.getElementById('cartCount').textContent = data.data.cart_count;
            } else {
                Swal.fire('Lỗi', data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Lỗi tải đơn hàng:', error);
            Swal.fire('Lỗi', 'Không thể tải đơn hàng', 'error');
        });
}

function loadMembership() {
    fetch('/api/user/profile')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const totalSpent = data.data.total_spent;
                const membershipLevel = Math.floor(totalSpent / 10000000);
                document.getElementById('membershipLevel').textContent = membershipLevel === 0 ? 'Chưa có' : `Hạng ${membershipLevel}`;
                document.getElementById('totalSpent').textContent = formatVND(totalSpent);
            } else {
                Swal.fire('Lỗi', data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Lỗi tải hạng thành viên:', error);
            Swal.fire('Lỗi', 'Không thể tải hạng thành viên', 'error');
        });
}

window.onload = () => {
    showTab('account');
    loadProfile();
};