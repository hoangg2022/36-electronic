$(document).ready(function() {
    // Fetch top 5 products by discount percentage
    function fetchTopDiscountedProducts() {
        $.ajax({
            url: '/api/products',
            method: 'GET',
            data: { sort: 'discount_desc' },
            success: function(data) {
                let html = '';
                data.slice(0, 5).forEach(product => {
                    const stars = '★'.repeat(Math.round(product.avg_rating)) + '☆'.repeat(5 - Math.round(product.avg_rating));
                    html += `
                        <div class="product-card">
                            <img src="${product.image_url}" alt="${product.name}">
                            ${product.discount_percentage ? `<span class="discount">Giảm ${product.discount_percentage}%</span>` : ''}
                            <h3>${product.name}</h3>
                            <p class="original-price">${product.price.toLocaleString('vi-VN')} VNĐ</p>
                            <p class="price">${product.discounted_price.toLocaleString('vi-VN')} VNĐ</p>
                            <p class="sold">Đã bán ${product.sold || 0}</p>
                            <p class="stock">Còn ${product.stock_quantity} sản phẩm</p>
                            <p class="rating"><span class="stars">${stars}</span> (${product.review_count} đánh giá)</p>
                            <p class="installment">${product.installment || '0% qua thẻ tín dụng kỳ hạn 3-6...'}</p>
                            <button class="add-to-cart" data-product-id="${product.id}" data-product-name="${product.name}" data-product-price="${product.discounted_price}">
                                <i class="fas fa-cart-plus"></i> Thêm vào giỏ hàng
                            </button>
                        </div>
                    `;
                });
                $('#discountedProducts').html(html);
                $('#discountedProducts .product-card').click(function(e) {
                    if (!$(e.target).closest('button').length) {
                        window.location.href = `/product-detail?id=${$(this).find('button').attr('data-product-id')}`;
                    }
                });
                attachAddToCartEvents();
            },
            error: function() {
                $('#discountedProducts').html('<p style="color: #e63946;">Lỗi khi tải sản phẩm giảm giá.</p>');
            }
        });
    }

    // Fetch top 5 products by number of items sold
    function fetchPopularProducts() {
        $.ajax({
            url: '/api/products',
            method: 'GET',
            data: { sort: 'sold DESC' },
            success: function(data) {
                let html = '';
                data.slice(0, 5).forEach(product => {
                    const stars = '★'.repeat(Math.round(product.avg_rating)) + '☆'.repeat(5 - Math.round(product.avg_rating));
                    html += `
                        <div class="product-card">
                            <img src="${product.image_url}" alt="${product.name}">
                            ${product.discount_percentage ? `<span class="discount">Giảm ${product.discount_percentage}%</span>` : ''}
                            <h3>${product.name}</h3>
                            <p class="original-price">${product.price.toLocaleString('vi-VN')} VNĐ</p>
                            <p class="price">${product.discounted_price.toLocaleString('vi-VN')} VNĐ</p>
                            <p class="sold">Đã bán ${product.sold || 0}</p>
                            <p class="stock">Còn ${product.stock_quantity} sản phẩm</p>
                            <p class="rating"><span class="stars">${stars}</span> (${product.review_count} đánh giá)</p>
                            <p class="installment">${product.installment || '0% qua thẻ tín dụng kỳ hạn 3-6...'}</p>
                            <button class="add-to-cart" data-product-id="${product.id}" data-product-name="${product.name}" data-product-price="${product.discounted_price}">
                                <i class="fas fa-cart-plus"></i> Thêm vào giỏ hàng
                            </button>
                        </div>
                    `;
                });
                $('#popularProducts').html(html);
                $('#popularProducts .product-card').click(function(e) {
                    if (!$(e.target).closest('button').length) {
                        window.location.href = `/product-detail?id=${$(this).find('button').attr('data-product-id')}`;
                    }
                });
                attachAddToCartEvents();
            },
            error: function() {
                $('#popularProducts').html('<p style="color: #e63946;">Lỗi khi tải sản phẩm phổ biến.</p>');
            }
        });
    }

    // Modified fetchProducts to support filtering and sorting
    function fetchProducts(categoryId, sort, filters, callback) {
        let url = '/api/products';
        const params = {};
        if (categoryId && categoryId !== 'all') params.category_id = categoryId;
        if (sort !== 'default') params.sort = sort;
        if (filters.priceRanges.length > 0) params.price_range = filters.priceRanges.join(',');
        if (filters.discount) params.discount = 'true';
        console.log('API Request Params:', params); // Debug log

        $.ajax({
            url: url,
            method: 'GET',
            data: params,
            success: function(data) {
                console.log('API Response:', data); // Debug log
                callback(data);
            },
            error: function(xhr) {
                $('#productGrid').html('<p style="color: #e63946;">Lỗi khi tải sản phẩm.</p>');
                console.error('Error fetching products:', xhr.responseJSON ? xhr.responseJSON.message : xhr.statusText);
            }
        });
    }

    // Modified renderProducts to handle filtered products
    function renderProducts(categoryId, sort, filters) {
        const container = $('#productGrid');
        container.html('<p style="color: #4a90e2;">Đang tải sản phẩm...</p>');

        fetchProducts(categoryId, sort, filters, function(products) {
            container.empty();
            if (products.length === 0) {
                container.html('<p style="color: #e63946;">Không tìm thấy sản phẩm nào.</p>');
                return;
            }
            products.forEach(product => {
                const stars = '★'.repeat(Math.round(product.avg_rating)) + '☆'.repeat(5 - Math.round(product.avg_rating));
                const card = `
                    <div class="product-card">
                        <img src="${product.image_url}" alt="${product.name}">
                        ${product.discount_percentage ? `<span class="discount">Giảm ${product.discount_percentage}%</span>` : ''}
                        <h3>${product.name}</h3>
                        <p class="original-price">${product.price.toLocaleString('vi-VN')} VNĐ</p>
                        <p class="price">${product.discounted_price.toLocaleString('vi-VN')} VNĐ</p>
                        <p class="sold">Đã bán ${product.sold || 0}</p>
                        <p class="stock">Còn ${product.stock_quantity} sản phẩm</p>
                        <p class="rating"><span class="stars">${stars}</span> (${product.review_count} đánh giá)</p>
                        <p class="installment">${product.installment || '0% qua thẻ tín dụng kỳ hạn 3-6...'}</p>
                        <button class="add-to-cart" data-product-id="${product.id}" data-product-name="${product.name}" data-product-price="${product.discounted_price}">
                            <i class="fas fa-cart-plus"></i> Thêm vào giỏ hàng
                        </button>
                    </div>
                `;
                container.append(card);
            });

            // Add click event for product details
            $('.product-card').off('click').on('click', function(e) {
                if (!$(e.target).closest('button').length) {
                    window.location.href = `/product-detail?id=${$(this).find('button').attr('data-product-id')}`;
                }
            });
            attachAddToCartEvents();
        });
    }

    // Fetch and render product details
    function renderProductDetail() {
        const urlParams = new URLSearchParams(window.location.search);
        const productId = urlParams.get('id');

        if (productId) {
            $.ajax({
                url: `/api/product/${productId}`,
                method: 'GET',
                success: function(data) {
                    if (data.success === false) {
                        $('#productDetail').html('<p style="color: #e63946;">Sản phẩm không tồn tại.</p>');
                        return;
                    }

                    const stars = '★'.repeat(Math.round(data.avg_rating)) + '☆'.repeat(5 - Math.round(data.avg_rating));
                    const html = `
                        <div class="product-detail">
                            <img src="${data.image_url}" alt="${data.name}">
                            <div class="product-info">
                                <h3>${data.name}</h3>
                                <p class="rating"><span class="stars">${stars}</span> (${data.review_count} đánh giá)</p>
                                ${data.discount_percentage ? `<span class="discount">Giảm ${data.discount_percentage}%</span>` : ''}
                                <p class="price">${data.discounted_price.toLocaleString('vi-VN')} VNĐ</p>
                                <p class="original-price">${data.price.toLocaleString('vi-VN')} VNĐ</p>
                                <p class="student-price">Giá sinh viên: ${data.student_price.toLocaleString('vi-VN')} VNĐ</p>
                                <p class="stock">Còn ${data.stock_quantity} sản phẩm</p>
                                <p class="sold">Đã bán ${data.sold || 0}</p>
                                <p class="installment">${data.installment}</p>
                                <p class="description">${data.description}</p>
                                <button class="add-to-cart" data-product-id="${data.id}" data-product-name="${data.name}" data-product-price="${data.discounted_price}">
                                    <i class="fas fa-cart-plus"></i> Thêm vào giỏ hàng
                                </button>
                            </div>
                        </div>
                    `;
                    $('#productDetail').html(html);

                    // Render reviews
                    let reviewsHtml = '';
                    if (data.reviews && data.reviews.length > 0) {
                        data.reviews.forEach(review => {
                            const reviewStars = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);
                            reviewsHtml += `
                                <div class="review-card">
                                    <p class="rating"><span class="stars">${reviewStars}</span></p>
                                    <p>"${review.comment}"</p>
                                    <h4>- ${review.user_name}</h4>
                                </div>
                            `;
                        });
                    } else {
                        reviewsHtml = '<p>Chưa có đánh giá nào.</p>';
                    }
                    $('#reviewsContainer').html(reviewsHtml);

                    // Attach add-to-cart event
                    attachAddToCartEvents();

                    // Setup review form
                    setupReviewForm(productId);
                },
                error: function() {
                    $('#productDetail').html('<p style="color: #e63946;">Lỗi khi tải chi tiết sản phẩm.</p>');
                }
            });
        } else {
            $('#productDetail').html('<p style="color: #e63946;">Không tìm thấy ID sản phẩm.</p>');
        }
    }

    // Setup review form
    function setupReviewForm(productId) {
        let selectedRating = 0;

        // Star rating interaction
        $('.star-rating .star').on('click', function() {
            selectedRating = parseInt($(this).data('value'));
            $('.star-rating .star').each(function() {
                $(this).toggleClass('selected', $(this).data('value') <= selectedRating);
            });
        });

        // Submit review
        $('#submitReview').on('click', function() {
            const comment = $('#reviewComment').val().trim();
            if (!selectedRating || !comment) {
                alert('Vui lòng chọn số sao và nhập bình luận.');
                return;
            }

            // Check login status
            $.ajax({
                url: '/api/check_login',
                method: 'GET',
                success: function(data) {
                    if (data.logged_in) {
                        // Submit review
                        $.ajax({
                            url: '/api/reviews/add',
                            method: 'POST',
                            contentType: 'application/json',
                            data: JSON.stringify({
                                product_id: productId,
                                rating: selectedRating,
                                comment: comment
                            }),
                            success: function(response) {
                                alert('Đánh giá của bạn đã được gửi!');
                                $('#reviewComment').val('');
                                $('.star-rating .star').removeClass('selected');
                                selectedRating = 0;
                                renderProductDetail(); // Refresh product details and reviews
                            },
                            error: function(xhr) {
                                alert(xhr.responseJSON ? xhr.responseJSON.message : 'Lỗi khi gửi đánh giá.');
                            }
                        });
                    } else {
                        window.location.href = '/login';
                    }
                },
                error: function() {
                    alert('Lỗi khi kiểm tra trạng thái đăng nhập.');
                }
            });
        });
    }

    // Attach add-to-cart button events
    function attachAddToCartEvents() {
        $('.add-to-cart').off('click').on('click', function() {
            const productId = $(this).data('product-id');
            const productName = $(this).data('product-name');
            const productPrice = $(this).data('product-price');

            // Check login status
            $.ajax({
                url: '/api/check_login',
                method: 'GET',
                success: function(data) {
                    if (data.logged_in) {
                        showAddToCartModal(productId, productName, productPrice);
                    } else {
                        window.location.href = '/login';
                    }
                },
                error: function() {
                    alert('Lỗi khi kiểm tra trạng thái đăng nhập.');
                }
            });
        });
    }

    // Show modal for adding to cart
    function showAddToCartModal(productId, productName, productPrice) {
        // Remove existing modal if any
        $('#cartModal').remove();

        // Create modal HTML
        const modalHtml = `
            <div id="cartModal" class="cart-modal">
                <div class="cart-modal-content">
                    <span class="cart-modal-close">×</span>
                    <h2>Xác nhận thêm vào giỏ hàng</h2>
                    <p><strong>Sản phẩm:</strong> ${productName}</p>
                    <p><strong>Giá:</strong> ${productPrice.toLocaleString('vi-VN')} VNĐ</p>
                    <label for="cartQuantity"><strong>Số lượng:</strong></label>
                    <input type="number" id="cartQuantity" value="1" min="1" step="1">
                    <p><strong>Tổng tiền:</strong> <span id="cartTotal">${productPrice.toLocaleString('vi-VN')} VNĐ</span></p>
                    <button id="cartConfirmBtn">Xác nhận</button>
                    <button id="cartCancelBtn">Hủy</button>
                </div>
            </div>
        `;
        $('body').append(modalHtml);

        // Update total cost when quantity changes
        $('#cartQuantity').on('input', function() {
            const quantity = parseInt($(this).val()) || 1;
            if (quantity < 1) {
                $(this).val(1);
                alert('Số lượng phải lớn hơn 0!');
                return;
            }
            const total = quantity * productPrice;
            $('#cartTotal').text(total.toLocaleString('vi-VN') + ' VNĐ');
        });

        // Confirm button
        $('#cartConfirmBtn').on('click', function() {
            const quantity = parseInt($('#cartQuantity').val()) || 1;
            if (quantity < 1) {
                alert('Số lượng phải lớn hơn 0!');
                return;
            }
            addToCart(productId, productName, productPrice, quantity);
            $('#cartModal').remove();
        });

        // Cancel button and close icon
        $('#cartCancelBtn, .cart-modal-close').on('click', function() {
            $('#cartModal').remove();
        });
    }

    // Add to cart
    function addToCart(productId, productName, productPrice, quantity) {
        $.ajax({
            url: '/api/cart/add',
            method: 'POST',
            data: {
                product_id: productId,
                quantity: quantity
            },
            success: function(response) {
                alert(`${productName} (x${quantity}) đã được thêm vào giỏ hàng! Tổng: ${(quantity * productPrice).toLocaleString('vi-VN')} VNĐ`);
            },
            error: function(xhr) {
                alert(xhr.responseJSON ? xhr.responseJSON.message : 'Lỗi khi thêm vào giỏ hàng.');
            }
        });
    }

    // User menu setup
    function setupUserMenu() {
        $.ajax({
            url: '/api/check_login',
            method: 'GET',
            success: function(data) {
                const userMenu = $('#userMenu');
                const userNameSpan = $('#userName');
                const userDropdown = $('#userDropdown');
                const logoutBtn = $('#logoutBtn');

                if (data.logged_in && userNameSpan.length) {
                    userNameSpan.text(data.full_name);
                    userDropdown.show();
                    userMenu.click(function() {
                        userDropdown.toggle();
                    });
                    if (logoutBtn.length) {
                        logoutBtn.click(function(e) {
                            e.preventDefault();
                            $.ajax({
                                url: '/logout',
                                method: 'POST',
                                success: function(response) {
                                    alert(response.message);
                                    window.location.href = response.redirect;
                                }
                            });
                        });
                    }
                } else {
                    userNameSpan.text('Đăng nhập');
                    userMenu.click(function() {
                        window.location.href = '/login';
                    });
                    userDropdown.hide();
                }
            }
        });
    }

    // Filter and sort setup
    function setupControls() {
        const filterButtons = document.querySelectorAll('.filter-section button');
        const sortButtons = document.querySelectorAll('.sort-section button');
        const priceCheckboxes = document.querySelectorAll('input[name="price-range"]');
        const discountCheckbox = document.getElementById('discountFilter');
        const filterPanel = document.getElementById('filterPanel');
        const urlParams = new URLSearchParams(window.location.search);
        let currentCategory = urlParams.get('category') || 'all';
        let currentSort = urlParams.get('sort') || 'default';
        let currentFilters = { priceRanges: [], discount: false };

        // Set active category and sort buttons
        filterButtons.forEach(button => {
            if (button.getAttribute('data-category') === currentCategory) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });

        sortButtons.forEach(button => {
            if (button.getAttribute('data-sort') === currentSort) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });

        // Initial render
        renderProducts(getCategoryId(currentCategory), getSortParam(currentSort), currentFilters);

        // Category filter buttons
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                currentCategory = button.getAttribute('data-category');
                renderProducts(getCategoryId(currentCategory), getSortParam(currentSort), currentFilters);
                window.history.pushState({}, '', `/products?category=${currentCategory}`);
            });
        });

        // Sort buttons
        sortButtons.forEach(button => {
            button.addEventListener('click', () => {
                sortButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                currentSort = button.getAttribute('data-sort');
                renderProducts(getCategoryId(currentCategory), getSortParam(currentSort), currentFilters);
                window.history.pushState({}, '', `/products?category=${currentCategory}&sort=${currentSort}`);
            });
        });

        // Toggle filter panel
        window.toggleFilterPanel = function() {
            filterPanel.classList.toggle('active');
        };

        // Apply filters
        window.applyFilters = function() {
            currentFilters.priceRanges = Array.from(priceCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            currentFilters.discount = discountCheckbox.checked;
            console.log('Applied Filters:', currentFilters); // Debug log
            renderProducts(getCategoryId(currentCategory), getSortParam(currentSort), currentFilters);
            filterPanel.classList.remove('active');
        };
    }

    // Helper function to map category name to category_id
    function getCategoryId(category) {
        const categoryMap = {
            'all': null,
            'phones': 1,
            'laptops': 2,
            'headphones': 3,
            'speakers': 4
        };
        return categoryMap[category] || null;
    }

    // Helper function to map sort option to API sort parameter
    function getSortParam(sort) {
        const sortMap = {
            'default': 'default',
            'price-low-high': 'price_asc',
            'price-high-low': 'price_desc',
            'popularity': 'sold DESC',
            'rating': 'rating_desc'
        };
        return sortMap[sort] || 'default';
    }

    // Initialize based on page
    if (window.location.pathname.includes('/product-detail')) {
        renderProductDetail();
    } else if (window.location.pathname.includes('/products')) {
        setupControls();
    }
});