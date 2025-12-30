$(document).ready(function() {

    function fetchProducts(categoryId, sort, filters, page, callback) {
        let url = '/api/products';
        const params = { page: page, limit: 20 };
        if (categoryId && categoryId !== 'all') params.category_id = categoryId;
        if (sort !== 'default') params.sort = sort;
        if (filters.priceRanges.length > 0) params.price_range = filters.priceRanges.join(',');
        if (filters.discount) params.discount = 'true';
        console.log('API Request Params:', params);

        $.ajax({
            url: url,
            method: 'GET',
            data: params,
            success: function(data) {
                console.log('API Response:', data);
                // Since API returns array directly, wrap it in an object
                const response = {
                    products: data.slice((page - 1) * 20, page * 20), // Client-side slicing
                    totalItems: data.length
                };
                callback(response);
            },
            error: function(xhr) {
                $('#productGrid').html('<p style="color: #e63946;">Lỗi khi tải sản phẩm.</p>');
                console.error('Error fetching products:', xhr.responseJSON ? xhr.responseJSON.message : xhr.statusText);
            }
        });
    }

    // Function to generate pagination controls
    function generatePaginationControls(totalItems, currentPage, categoryId, sort, filters) {
        const itemsPerPage = 20;
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        let paginationHtml = '<div class="pagination">';
        
        // Previous button
        paginationHtml += `
            <button class="pagination-btn" ${currentPage === 1 ? 'disabled' : ''} data-page="${currentPage - 1}">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        if (startPage > 1) {
            paginationHtml += `<button class="pagination-btn" data-page="1">1</button>`;
            if (startPage > 2) paginationHtml += '<span>...</span>';
        }
        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `
                <button class="pagination-btn ${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>
            `;
        }
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) paginationHtml += '<span>...</span>';
            paginationHtml += `<button class="pagination-btn" data-page="${totalPages}">${totalPages}</button>`;
        }

        // Next button
        paginationHtml += `
            <button class="pagination-btn" ${currentPage === totalPages ? 'disabled' : ''} data-page="${currentPage + 1}">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;
        paginationHtml += '</div>';

        $('#pagination').html(paginationHtml);

        $('.pagination-btn').off('click').on('click', function() {
            const page = parseInt($(this).data('page'));
            if (page) {
                renderProducts(categoryId, sort, filters, page);
                window.history.pushState({}, '', `/products?category=${categoryId || 'all'}&sort=${sort}&page=${page}`);
            }
        });
    }

    // Modified renderProducts to handle pagination
    function renderProducts(categoryId, sort, filters, page = 1) {
        const container = $('#productGrid');
        container.html('<p style="color: #4a90e2;">Đang tải sản phẩm...</p>');

        fetchProducts(categoryId, sort, filters, page, function(data) {
            container.empty();
            if (!data.products || data.products.length === 0) {
                container.html('<p style="color: #e63946;">Không tìm thấy sản phẩm nào.</p>');
                return;
            }
            data.products.forEach(product => {
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

            generatePaginationControls(data.totalItems, page, categoryId, sort, filters);

            $('.product-card').off('click').on('click', function(e) {
                if (!$(e.target).closest('button').length) {
                    window.location.href = `/product-detail?id=${$(this).find('button').attr('data-product-id')}`;
                }
            });
            attachAddToCartEvents();
        });
    }

    // Show modal for adding to cart
    function showAddToCartModal(productId, productName, productPrice) {
        $.ajax({
            url: `/api/product/${productId}`,
            method: 'GET',
            success: function(data) {
                if (data.success === false || !data.stock_quantity) {
                    alert('Không thể lấy thông tin sản phẩm hoặc sản phẩm hết hàng.');
                    return;
                }

                const stockQuantity = data.stock_quantity;

                $('#cartModal').remove();

                const modalHtml = `
                    <div id="cartModal" class="cart-modal">
                        <div class="cart-modal-content">
                            <span class="cart-modal-close">×</span>
                            <h2>Thêm vào giỏ hàng</h2>
                            <p><strong>Sản phẩm:</strong> ${productName}</p>
                            <p><strong>Giá:</strong> ${productPrice.toLocaleString('vi-VN')} VNĐ</p>
                            <p><strong>Tồn kho:</strong> ${stockQuantity} sản phẩm</p>
                            <label for="cartQuantity"><strong>Số lượng:</strong></label>
                            <input type="number" id="cartQuantity" value="1" min="1" max="${stockQuantity}" step="1">
                            <p><strong>Tổng tiền:</strong> <span id="cartTotal">${productPrice.toLocaleString('vi-VN')} VNĐ</span></p>
                            <button id="cartConfirmBtn">Xác nhận</button>
                            <button id="cartCancelBtn">Hủy</button>
                        </div>
                    </div>
                `;

                $('body').append(modalHtml);

                $('#cartQuantity').on('input', function () {
                    let quantity = parseInt($(this).val()) || 1;
                    if (quantity < 1) {
                        quantity = 1;
                        $(this).val(quantity);
                    }
                    if (quantity > stockQuantity) {
                        quantity = stockQuantity;
                        $(this).val(quantity);
                        alert(`Số lượng không được vượt quá ${stockQuantity}.`);
                    }
                    const total = quantity * productPrice;
                    $('#cartTotal').text(total.toLocaleString('vi-VN') + ' VNĐ');
                });

                $('#cartConfirmBtn').on('click', function () {
                    const quantity = parseInt($('#cartQuantity').val()) || 1;
                    if (quantity < 1 || quantity > stockQuantity) {
                        alert('Số lượng không hợp lệ!');
                        return;
                    }
                    addToCart(productId, productName, productPrice, quantity);
                    $('#cartModal').remove();
                });

                $('#cartCancelBtn, .cart-modal-close').on('click', function () {
                    $('#cartModal').remove();
                });
            },
            error: function () {
                alert('Lỗi khi lấy thông tin sản phẩm.');
            }
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

                    attachAddToCartEvents();

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

        $('.star-rating .star').on('click', function() {
            selectedRating = parseInt($(this).data('value'));
            $('.star-rating .star').each(function() {
                $(this).toggleClass('selected', $(this).data('value') <= selectedRating);
            });
        });

        $('#submitReview').on('click', function() {
            const comment = $('#reviewComment').val().trim();
            if (!selectedRating || !comment) {
                alert('Vui lòng chọn số sao và nhập bình luận.');
                return;
            }

            $.ajax({
                url: '/api/check_login',
                method: 'GET',
                success: function(data) {
                    if (data.logged_in) {
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
                                renderProductDetail();
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

    // Add to cart
    function addToCart(productId, productName, productPrice, quantity) {
        $.ajax({
            url: '/api/cart/add',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                product_id: productId,
                quantity: quantity
            }),
            success: function(response) {
                alert(`${productName} (x${quantity}) đã được thêm vào giỏ hàng!`);
                if (response.cart_count !== undefined) {
                    $('#cartCount').text(response.cart_count);
                }
            },
            error: function(xhr) {
                alert(xhr.responseJSON ? xhr.responseJSON.message : 'Lỗi khi thêm vào giỏ hàng.');
            }
        });
    }

    function setupControls() {
        const filterButtons = document.querySelectorAll('.filter-section button');
        const sortButtons = document.querySelectorAll('.sort-section button');
        const priceCheckboxes = document.querySelectorAll('input[name="price-range"]');
        const discountCheckbox = document.getElementById('discountFilter');
        const filterPanel = document.getElementById('filterPanel');
        const urlParams = new URLSearchParams(window.location.search);
        let currentCategory = urlParams.get('category') || 'all';
        let currentSort = urlParams.get('sort') || 'default';
        let currentPage = parseInt(urlParams.get('page')) || 1;
        let currentFilters = { priceRanges: [], discount: false };

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

        renderProducts(getCategoryId(currentCategory), getSortParam(currentSort), currentFilters, currentPage);

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                currentCategory = button.getAttribute('data-category');
                currentPage = 1;
                renderProducts(getCategoryId(currentCategory), getSortParam(currentSort), currentFilters, currentPage);
                window.history.pushState({}, '', `/products?category=${currentCategory}&sort=${currentSort}&page=${currentPage}`);
            });
        });

        sortButtons.forEach(button => {
            button.addEventListener('click', () => {
                sortButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                currentSort = button.getAttribute('data-sort');
                currentPage = 1;
                renderProducts(getCategoryId(currentCategory), getSortParam(currentSort), currentFilters, currentPage);
                window.history.pushState({}, '', `/products?category=${currentCategory}&sort=${currentSort}&page=${currentPage}`);
            });
        });

        window.toggleFilterPanel = function() {
            filterPanel.classList.toggle('active');
        };

        window.applyFilters = function() {
            currentFilters.priceRanges = Array.from(priceCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            currentFilters.discount = discountCheckbox.checked;
            currentPage = 1;
            console.log('Applied Filters:', currentFilters);
            renderProducts(getCategoryId(currentCategory), getSortParam(currentSort), currentFilters, currentPage);
            window.history.pushState({}, '', `/products?category=${currentCategory}&sort=${currentSort}&page=${currentPage}`);
            filterPanel.classList.remove('active');
        };
    }

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

    if (window.location.pathname.includes('/product-detail')) {
        renderProductDetail();
    } else if (window.location.pathname.includes('/products')) {
        setupControls();
    }
});