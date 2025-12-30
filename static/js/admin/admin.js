document.addEventListener('DOMContentLoaded', function() {
    const currentTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Ho_Chi_Minh' });
    document.querySelector('.time-info').textContent = currentTime;

    const itemsPerPage = 5;
    let currentPage = 1;
    let users = [];
    let products = [];
    let orders = [];

    // Kiểm tra đăng nhập qua API
    fetch('{{ url_for("cart.check_login") }}')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (!data.logged_in || data.role !== 'admin') {
                alert('Bạn không có quyền truy cập trang Admin!');
                window.location.href = '{{ url_for("auth.login") }}';
                return;
            }
            document.getElementById('userName').textContent = data.full_name;
            loadData();
        })
        .catch(error => {
            console.error('Lỗi kiểm tra đăng nhập:', error);
            alert('Lỗi kiểm tra đăng nhập, vui lòng thử lại');
            window.location.href = '{{ url_for("auth.login") }}';
        });

    // Tải dữ liệu từ API
    async function loadData() {
        try {
            // Tải thống kê
            const statsResponse = await fetch('/api/admin/stats');
            if (!statsResponse.ok) throw new Error(`HTTP ${statsResponse.status}`);
            const statsData = await statsResponse.json();
            if (statsData.success) {
                document.getElementById('totalProducts').textContent = statsData.total_products;
                document.getElementById('totalOrders').textContent = statsData.total_orders;
                document.getElementById('totalRevenue').textContent = statsData.total_revenue.toLocaleString('vi-VN') + ' VNĐ';
            }

            // Tải danh sách users
            const usersResponse = await fetch('/api/admin/users');
            if (!usersResponse.ok) throw new Error(`HTTP ${usersResponse.status}`);
            users = await usersResponse.json();

            // Tải danh sách products
            const productsResponse = await fetch('/api/admin/products');
            if (!productsResponse.ok) throw new Error(`HTTP ${productsResponse.status}`);
            products = await productsResponse.json();

            // Tải danh sách orders
            const ordersResponse = await fetch('/api/admin/orders');
            if (!ordersResponse.ok) throw new Error(`HTTP ${ordersResponse.status}`);
            const ordersData = await ordersResponse.json();
            if (ordersData.success) {
                orders = [...ordersData.pending_orders, ...ordersData.completed_orders];
            }

            // Render danh sách ban đầu
            const pageType = window.location.pathname.includes('users') ? 'userList' : window.location.pathname.includes('products') ? 'productList' : 'orderList';
            renderList(pageType === 'userList' ? users : pageType === 'productList' ? products : orders, pageType, '', pageType === 'userList' ? 'editUser' : pageType === 'productList' ? 'editProduct' : 'editOrder', pageType === 'userList' ? 'deleteUser' : pageType === 'productList' ? 'deleteProduct' : 'deleteOrder');
        } catch (error) {
            console.error('Lỗi tải dữ liệu:', error);
            alert('Không thể tải dữ liệu, vui lòng thử lại');
        }
    }

    // Hàm render danh sách
    function renderList(list, containerId, searchTerm = '', editFunc, deleteFunc) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        const filteredList = list.filter(item =>
            item.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.id?.toString().includes(searchTerm)
        );

        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const paginatedList = filteredList.slice(start, end);

        paginatedList.forEach(item => {
            const row = document.createElement('tr');
            let cols = '';
            if (containerId === 'userList') {
                cols = `<td>${item.full_name}</td><td>${item.email}</td><td>${item.role}</td>`;
            } else if (containerId === 'productList') {
                cols = `<td>${item.name}</td><td>${item.price.toLocaleString('vi-VN')} VNĐ</td><td>${item.stock_quantity}</td>`;
            } else if (containerId === 'orderList') {
                cols = `<td>${item.id}</td><td>${item.user_name}</td><td>${item.status}</td>`;
            }
            row.innerHTML = `${cols}<td><button onclick="${editFunc}(${item.id})">Sửa</button><button class="delete" onclick="${deleteFunc}(${item.id})">Xóa</button></td>`;
            container.appendChild(row);
        });

        renderPagination(filteredList.length);
    }

    // Hàm render phân trang
    function renderPagination(totalItems) {
        const pagination = document.getElementById('pagination');
        pagination.innerHTML = '';
        const totalPages = Math.ceil(totalItems / itemsPerPage);

        for (let i = 1; i <= totalPages; i++) {
            const button = document.createElement('button');
            button.textContent = i;
            if (i === currentPage) button.classList.add('active');
            button.addEventListener('click', () => {
                currentPage = i;
                const searchTerm = document.getElementById('searchInput')?.value || '';
                const pageType = window.location.pathname.includes('users') ? 'userList' : window.location.pathname.includes('products') ? 'productList' : 'orderList';
                renderList(pageType === 'userList' ? users : pageType === 'productList' ? products : orders, pageType, searchTerm, pageType === 'userList' ? 'editUser' : pageType === 'productList' ? 'editProduct' : 'editOrder', pageType === 'userList' ? 'deleteUser' : pageType === 'productList' ? 'deleteProduct' : 'deleteOrder');
            });
            pagination.appendChild(button);
        }
    }

    // Thêm người dùng
    async function addUser() {
        const username = document.getElementById('userName').value.trim();
        const email = document.getElementById('userEmail').value.trim();
        const password = document.getElementById('userPassword').value.trim();
        const full_name = username;
        const birth_date = '2000-01-01'; // Giá trị mặc định, cần form nhập
        const role = document.getElementById('userRole').value.toLowerCase() === 'admin' ? 'admin' : 'customer';

        if (!username || !email || !password || !role) {
            alert('Vui lòng điền đầy đủ thông tin!');
            return;
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            alert('Vui lòng nhập email hợp lệ!');
            return;
        }

        try {
            const response = await fetch('/api/admin/add_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, full_name, birth_date, role })
            });
            const result = await response.json();
            if (result.success) {
                users = await (await fetch('/api/admin/users')).json();
                renderList(users, 'userList', '', 'editUser', 'deleteUser');
                document.getElementById('userName').value = '';
                document.getElementById('userEmail').value = '';
                document.getElementById('userPassword').value = '';
                document.getElementById('userRole').value = 'Khách hàng';
                alert('Thêm người dùng thành công!');
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Lỗi thêm người dùng:', error);
            alert('Lỗi, vui lòng thử lại sau');
        }
    }

    // Thêm sản phẩm
    async function addProduct() {
        const name = document.getElementById('productName').value.trim();
        const price = parseFloat(document.getElementById('productPrice').value) || 0;
        const stock_quantity = parseInt(document.getElementById('productQuantity').value) || 0;
        const category_id = 1; // Giá trị mặc định, cần form nhập
        const description = 'Mô tả mặc định'; // Giá trị mặc định
        const discount_percentage = 0;
        const image = null; // Cần xử lý upload file

        if (!name || price <= 0 || stock_quantity <= 0) {
            alert('Vui lòng điền đầy đủ thông tin hợp lệ!');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('name', name);
            formData.append('category_id', category_id);
            formData.append('description', description);
            formData.append('price', price / 25000); // Chuyển về đơn vị server
            formData.append('discount_percentage', discount_percentage);
            formData.append('stock_quantity', stock_quantity);
            if (document.getElementById('productImage').files[0]) {
                formData.append('image', document.getElementById('productImage').files[0]);
            }

            const response = await fetch('/api/admin/add_product', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.success) {
                products = await (await fetch('/api/admin/products')).json();
                renderList(products, 'productList', '', 'editProduct', 'deleteProduct');
                document.getElementById('productName').value = '';
                document.getElementById('productPrice').value = '';
                document.getElementById('productQuantity').value = '';
                alert('Thêm sản phẩm thành công!');
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Lỗi thêm sản phẩm:', error);
            alert('Lỗi, vui lòng thử lại sau');
        }
    }

    // Thêm đơn hàng
    async function addOrder() {
        const id = document.getElementById('orderId').value.trim();
        const user_name = document.getElementById('orderCustomer').value.trim();
        const status = document.getElementById('orderStatus').value;
        const product_name = 'Sản phẩm mặc định'; // Cần form nhập
        const quantity = 1; // Cần form nhập
        const total_price = 0; // Cần tính toán

        if (!id || !user_name || !status) {
            alert('Vui lòng điền đầy đủ thông tin!');
            return;
        }

        try {
            const response = await fetch('/api/admin/add_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, user_name, product_name, quantity, total_price, status })
            });
            const result = await response.json();
            if (result.success) {
                const ordersResponse = await fetch('/api/admin/orders');
                const ordersData = await ordersResponse.json();
                if (ordersData.success) {
                    orders = [...ordersData.pending_orders, ...ordersData.completed_orders];
                }
                renderList(orders, 'orderList', '', 'editOrder', 'deleteOrder');
                document.getElementById('orderId').value = '';
                document.getElementById('orderCustomer').value = '';
                document.getElementById('orderStatus').value = 'Chờ xử lý';
                alert('Thêm đơn hàng thành công!');
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Lỗi thêm đơn hàng:', error);
            alert('Lỗi, vui lòng thử lại sau');
        }
    }

    // Sửa/xóa
    async function editUser(id) {
        const user = users.find(u => u.id === id);
        if (user) {
            const full_name = prompt('Nhập tên mới:', user.full_name);
            const email = prompt('Nhập email mới:', user.email);
            const role = prompt('Nhập vai trò mới (customer/admin):', user.role);
            const birth_date = '2000-01-01'; // Giá trị mặc định
            if (full_name && email && role && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) && ['customer', 'admin'].includes(role)) {
                try {
                    const response = await fetch(`/api/admin/update_user/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ full_name, email, birth_date, role })
                    });
                    const result = await response.json();
                    if (result.success) {
                        users = await (await fetch('/api/admin/users')).json();
                        renderList(users, 'userList', '', 'editUser', 'deleteUser');
                        alert('Cập nhật người dùng thành công!');
                    } else {
                        alert(result.message);
                    }
                } catch (error) {
                    console.error('Lỗi cập nhật người dùng:', error);
                    alert('Lỗi, vui lòng thử lại sau');
                }
            } else {
                alert('Thông tin không hợp lệ!');
            }
        }
    }

    async function editProduct(id) {
    try {
        // Lấy thông tin sản phẩm từ API
        const response = await fetch(`/api/admin/product/${id}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const product = await response.json();
        if (!product.success) {
            alert(product.message);
            return;
        }

        // Điền dữ liệu vào form
        document.getElementById('productNameUpdate').value = product.name;
        document.getElementById('categoryIdUpdate').value = product.category_id || 1; // Giả sử có trường category_id
        document.getElementById('descriptionUpdate').value = product.description || '';
        document.getElementById('priceUpdate').value = product.price;
        document.getElementById('discountUpdate').value = product.discount_percentage;
        document.getElementById('quantityUpdate').value = product.stock_quantity;
        // Hiển thị hình ảnh hiện tại (nếu cần)
        const imagePreview = document.getElementById('currentImage');
        if (imagePreview && product.image_url) {
            imagePreview.src = product.image_url;
            imagePreview.style.display = 'block';
        }

        // Xử lý cập nhật khi nhấn nút "Cập nhật Sản phẩm"
        document.getElementById('updateProductBtn').onclick = async () => {
            const name = document.getElementById('productNameUpdate').value.trim();
            const category_id = parseInt(document.getElementById('categoryIdUpdate').value) || 1;
            const description = document.getElementById('descriptionUpdate').value.trim();
            const price = parseFloat(document.getElementById('priceUpdate').value) || 0;
            const discount_percentage = parseFloat(document.getElementById('discountUpdate').value) || 0;
            const stock_quantity = parseInt(document.getElementById('quantityUpdate').value) || 0;

            if (!name || price <= 0 || stock_quantity < 0) {
                alert('Vui lòng điền đầy đủ thông tin hợp lệ!');
                return;
            }

            try {
                const formData = new FormData();
                formData.append('name', name);
                formData.append('category_id', category_id);
                formData.append('description', description);
                formData.append('price', price / 25000);
                formData.append('discount_percentage', discount_percentage);
                formData.append('stock_quantity', stock_quantity);
                formData.append('image_url', product.image_url || '');
                if (document.getElementById('productImageUpdate')?.files[0]) {
                    formData.append('image', document.getElementById('productImageUpdate').files[0]);
                }

                const updateResponse = await fetch(`/api/admin/update_product/${id}`, {
                    method: 'PUT',
                    body: formData
                });
                const result = await updateResponse.json();
                if (result.success) {
                    products = await (await fetch('/api/admin/products')).json();
                    renderList(products, 'productList', '', 'editProduct', 'deleteProduct');
                    alert('Cập nhật sản phẩm thành công!');
                    // Reset form
                    document.getElementById('productNameUpdate').value = '';
                    document.getElementById('categoryIdUpdate').value = '';
                    document.getElementById('descriptionUpdate').value = '';
                    document.getElementById('priceUpdate').value = '';
                    document.getElementById('discountUpdate').value = '';
                    document.getElementById('quantityUpdate').value = '';
                    if (imagePreview) imagePreview.style.display = 'none';
                } else {
                    alert(result.message);
                }
            } catch (error) {
                console.error('Lỗi cập nhật sản phẩm:', error);
                alert('Lỗi, vui lòng thử lại sau');
            }
        };
    } catch (error) {
        console.error('Lỗi khi lấy thông tin sản phẩm:', error);
        alert('Lỗi, vui lòng thử lại sau');
    }
}

    async function editOrder(id) {
        const order = orders.find(o => o.id === id);
        if (order) {
            const user_name = prompt('Nhập khách hàng mới:', order.user_name);
            const status = prompt('Nhập trạng thái mới (Đang chờ giao/Đang giao/Đã giao):', order.status);
            if (user_name && ['Đang chờ giao', 'Đang giao', 'Đã giao'].includes(status)) {
                try {
                    const response = await fetch(`/api/admin/update_order_status/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ status })
                    });
                    const result = await response.json();
                    if (result.success) {
                        const ordersResponse = await fetch('/api/admin/orders');
                        const ordersData = await ordersResponse.json();
                        if (ordersData.success) {
                            orders = [...ordersData.pending_orders, ...ordersData.completed_orders];
                        }
                        renderList(orders, 'orderList', '', 'editOrder', 'deleteOrder');
                        alert('Cập nhật đơn hàng thành công!');
                    } else {
                        alert(result.message);
                    }
                } catch (error) {
                    console.error('Lỗi cập nhật đơn hàng:', error);
                    alert('Lỗi, vui lòng thử lại sau');
                }
            } else {
                alert('Thông tin không hợp lệ!');
            }
        }
    }

    async function deleteUser(id) {
        if (confirm('Bạn có chắc muốn xóa người dùng này?')) {
            try {
                const response = await fetch(`/api/admin/delete_user/${id}`, { method: 'DELETE' });
                const result = await response.json();
                if (result.success) {
                    users = await (await fetch('/api/admin/users')).json();
                    renderList(users, 'userList', '', 'editUser', 'deleteUser');
                    alert('Xóa người dùng thành công!');
                } else {
                    alert(result.message);
                }
            } catch (error) {
                console.error('Lỗi xóa người dùng:', error);
                alert('Lỗi, vui lòng thử lại sau');
            }
        }
    }

    async function deleteProduct(id) {
        if (confirm('Bạn có chắc muốn xóa sản phẩm này?')) {
            try {
                const response = await fetch(`/api/admin/delete_product/${id}`, { method: 'DELETE' });
                const result = await response.json();
                if (result.success) {
                    products = await (await fetch('/api/admin/products')).json();
                    renderList(products, 'productList', '', 'editProduct', 'deleteProduct');
                    alert('Xóa sản phẩm thành công!');
                } else {
                    alert(result.message);
                }
            } catch (error) {
                console.error('Lỗi xóa sản phẩm:', error);
                alert('Lỗi, vui lòng thử lại sau');
            }
        }
    }

    async function deleteOrder(id) {
        if (confirm('Bạn có chắc muốn xóa đơn hàng này?')) {
            try {
                const response = await fetch(`/api/admin/delete_order/${id}`, { method: 'DELETE' });
                const result = await response.json();
                if (result.success) {
                    const ordersResponse = await fetch('/api/admin/orders');
                    const ordersData = await ordersResponse.json();
                    if (ordersData.success) {
                        orders = [...ordersData.pending_orders, ...ordersData.completed_orders];
                    }
                    renderList(orders, 'orderList', '', 'editOrder', 'deleteOrder');
                    alert('Xóa đơn hàng thành công!');
                } else {
                    alert(result.message);
                }
            } catch (error) {
                console.error('Lỗi xóa đơn hàng:', error);
                alert('Lỗi, vui lòng thử lại sau');
            }
        }
    }

    // Tìm kiếm
    document.getElementById('searchInput')?.addEventListener('input', (e) => {
        currentPage = 1;
        const searchTerm = e.target.value;
        const pageType = window.location.pathname.includes('users') ? 'userList' : window.location.pathname.includes('products') ? 'productList' : 'orderList';
        renderList(pageType === 'userList' ? users : pageType === 'productList' ? products : orders, pageType, searchTerm, pageType === 'userList' ? 'editUser' : pageType === 'productList' ? 'editProduct' : 'editOrder', pageType === 'userList' ? 'deleteUser' : pageType === 'productList' ? 'deleteProduct' : 'deleteOrder');
    });

    // Gắn sự kiện cho nút thêm
    document.getElementById('addUserBtn')?.addEventListener('click', addUser);
    document.getElementById('addProductBtn')?.addEventListener('click', addProduct);
    document.getElementById('addOrderBtn')?.addEventListener('click', addOrder);
});