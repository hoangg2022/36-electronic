$(document).ready(function () {
    // Carousel functionality
    let currentSlide = 0;
    const slides = $('.carousel-item');
    function showSlide(index) {
        if (index >= slides.length) currentSlide = 0;
        if (index < 0) currentSlide = slides.length - 1;
        $('#carouselInner').css('transform', `translateX(-${currentSlide * 100}%)`);
    }
    window.nextSlide = function () {
        currentSlide++;
        showSlide(currentSlide);
    };
    window.prevSlide = function () {
        currentSlide--;
        showSlide(currentSlide);
    };
    setInterval(nextSlide, 5000);
    showSlide(currentSlide);

    // Fetch top 5 products by discount percentage
    function fetchTopDiscountedProducts() {
        $.ajax({
            url: '/api/products',
            method: 'GET',
            data: { sort: 'discount_desc' },
            success: function (data) {
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
                            <p class="installment">0% qua thẻ tín dụng kỳ hạn 3-6...</p>
                            <button class="add-to-cart" onclick="addToCart(${product.id}, '${product.name}', ${product.discounted_price})">
                                <i class="fas fa-cart-plus"></i> Thêm vào giỏ hàng
                            </button>
                        </div>
                    `;
                });
                $('#discountedProducts').html(html);
                $('#discountedProducts .product-card').click(function (e) {
                    if (!$(e.target).closest('button').length) {
                        window.location.href = `/product-detail?id=${$(this).find('button').attr('onclick').match(/\d+/)[0]}`;
                    }
                });
            },
            error: function () {
                $('#discountedProducts').html('<p style="color: #e63946;">Lỗi khi tải sản phẩm giảm giá.</p>');
            }
        });
    }

    // Fetch top 5 products by number of items sold
    function fetchPopularProducts() {
        $.ajax({
            url: '/api/products',
            method: 'GET',
            data: { sort: 'sold_desc' },
            success: function (data) {
                let html = '';
                if (!data || data.length === 0) {
                    $('#popularProducts').html('<p style="color: #e63946;">Không có sản phẩm phổ biến.</p>');
                    return;
                }
                data.slice(0, 5).forEach(product => {
                    const stars = '★'.repeat(Math.round(product.avg_rating)) + '☆'.repeat(5 - Math.round(product.avg_rating));
                    html += `
                        <div class="product-card">
                            <img src="${product.image_url || '/images/placeholder.jpg'}" alt="${product.name || 'Không có tên'}">
                            ${product.discount_percentage ? `<span class="discount">Giảm ${product.discount_percentage}%</span>` : ''}
                            <h3>${product.name || 'Không xác định'}</h3>
                            <p class="original-price">${product.price?.toLocaleString('vi-VN') || 0} VNĐ</p>
                            <p class="price">${product.discounted_price?.toLocaleString('vi-VN') || 0} VNĐ</p>
                            <p class="sold">Đã bán ${product.sold || 0}</p>
                            <p class="stock">Còn ${product.stock_quantity || 0} sản phẩm</p>
                            <p class="rating"><span class="stars">${stars}</span> (${product.review_count || 0} đánh giá)</p>
                            <p class="installment">${product.installment || '0% qua thẻ tín dụng kỳ hạn 3-6...'}</p>
                            <button class="add-to-cart" onclick="addToCart(${product.id}, '${product.name}', ${product.discounted_price})">
                                <i class="fas fa-cart-plus"></i> Thêm vào giỏ hàng
                            </button>
                        </div>
                    `;
                });
                $('#popularProducts').html(html);
                $('#popularProducts .product-card').click(function (e) {
                    if (!$(e.target).closest('button').length) {
                        window.location.href = `/product-detail?id=${$(this).find('button').attr('onclick').match(/\d+/)[0]}`;
                    }
                });
            },
            error: function (xhr) {
                const errorMsg = xhr.responseJSON?.message || 'Lỗi khi tải sản phẩm phổ biến.';
                $('#popularProducts').html(`<p style="color: #e63946;">${errorMsg}</p>`);
                console.error('Lỗi:', xhr.status, xhr.statusText, xhr.responseJSON);
            }
        });
    }

    // Fetch website reviews with vertical scroll
    function fetchWebsiteReviews() {
        $.ajax({
            url: '/api/website-reviews',
            method: 'GET',
            success: function (data) {
                if (data.reviews && data.reviews.length > 0) {
                    let html = '';
                    data.reviews.forEach(review => {
                        const stars = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);
                        html += `
                            <div class="review-card">
                                <p>"${review.comment}"</p>
                                <p><span class="stars">${stars}</span> - ${review.full_name || 'Ẩn danh'}</p>
                                <small>${new Date(review.created_at).toLocaleDateString('vi-VN')}</small>
                            </div>
                        `;
                    });
                    $('#reviews').html(html);
                } else {
                    $('#reviews').html('<p style="color: #e63946;">Chưa có đánh giá nào.</p>');
                }
            },
            error: function () {
                $('#reviews').html('<p style="color: #e63946;">Lỗi khi tải đánh giá.</p>');
            }
        });
    }

    // Handle contact form submission
    let isSubmitting = false;
    $('#contact-form').on('submit', function (e) {
        e.preventDefault();
        if (isSubmitting) return;
        isSubmitting = true;

        const userId = $('#userId').val() || null;
        const rating = parseInt($('#rating').val()) || 1;
        const comment = $('#message').val().trim();

        if (!comment) {
            alert('Vui lòng nhập nhận xét.');
            isSubmitting = false;
            return;
        }

        $.ajax({
            url: '/api/website-reviews',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                user_id: userId,
                rating: rating,
                comment: comment
            }),
            success: function (response) {
                $('#review-submit-message')
                    .text(response.message || 'Đánh giá đã được gửi thành công!')
                    .css({
                        'display': 'block',
                        'background-color': '#d4edda',
                        'color': '#155724'
                    })
                    .fadeIn()
                    .delay(1000)
                    .fadeOut();

                $('#contact-form')[0].reset();
                fetchWebsiteReviews();
                isSubmitting = false;
            },
            error: function (xhr) {
                $('#review-submit-message')
                    .text(xhr.responseJSON?.message || 'Lỗi khi gửi đánh giá.')
                    .css({
                        'display': 'block',
                        'background-color': '#f8d7da',
                        'color': '#721c24'
                    })
                    .fadeIn()
                    .delay(3000)
                    .fadeOut();
                isSubmitting = false;
            }
        });
    });

    // Add to cart with custom modal
    window.addToCart = function (productId, productName, productPrice) {
        const modalHtml = `
            <div class="cart-modal-overlay">
                <div class="cart-modal">
                    <div class="cart-modal-header">
                        <h3>Xác nhận thêm vào giỏ hàng</h3>
                        <span class="cart-modal-close">×</span>
                    </div>
                    <div class="cart-modal-content">
                        <div class="cart-modal-row">
                            <span class="cart-modal-label">Sản phẩm:</span>
                            <span class="cart-modal-value">${productName}</span>
                        </div>
                        <div class="cart-modal-row">
                            <span class="cart-modal-label">Giá:</span>
                            <span class="cart-modal-value">${productPrice.toLocaleString('vi-VN')} VNĐ</span>
                        </div>
                        <div class="cart-modal-row">
                            <span class="cart-modal-label">Số lượng:</span>
                            <input type="number" id="cartQuantity" value="1" min="1" step="1">
                        </div>
                        <div class="cart-modal-row">
                            <span class="cart-modal-label">Tổng tiền:</span>
                            <span class="cart-modal-value" id="cartTotal">${productPrice.toLocaleString('vi-VN')} VNĐ</span>
                        </div>
                    </div>
                    <div class="cart-modal-buttons">
                        <button id="cartConfirm">Xác nhận</button>
                        <button id="cartCancel">Hủy</button>
                    </div>
                </div>
            </div>
        `;
        $('body').append(modalHtml);

        $('#cartQuantity').on('input', function () {
            const quantity = parseInt($(this).val()) || 1;
            if (quantity < 1) $(this).val(1);
            const total = productPrice * quantity;
            $('#cartTotal').text(total.toLocaleString('vi-VN') + ' VNĐ');
        });

        $('#cartConfirm').click(function () {
            const quantity = parseInt($('#cartQuantity').val()) || 1;
            if (quantity < 1) {
                alert('Số lượng phải lớn hơn 0!');
                $('.cart-modal-overlay').remove();
                return;
            }

            $.ajax({
                url: '/api/cart/add',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                }),
                success: function (response) {
                    alert(`${productName} (x${quantity}) đã được thêm vào giỏ hàng!`);
                    $('.cart-modal-overlay').remove();
                },
                error: function (xhr) {
                    alert(xhr.responseJSON ? xhr.responseJSON.message : 'Lỗi khi thêm vào giỏ hàng.');
                    $('.cart-modal-overlay').remove();
                }
            });
        });

        $('#cartCancel, .cart-modal-close').click(function () {
            $('.cart-modal-overlay').remove();
        });
    };

    // User menu setup
    function setupUserMenu() {
        $.ajax({
            url: '/api/check_login',
            method: 'GET',
            success: function (data) {
                const userMenu = $('#userMenu');
                const userNameSpan = $('#userName');
                const userDropdown = $('#userDropdown');
                const logoutBtn = $('#logoutBtn');

                if (data.logged_in && userNameSpan.length) {
                    userNameSpan.text(data.full_name);
                    userDropdown.show();
                    userMenu.click(function () {
                        userDropdown.toggle();
                    });
                    if (logoutBtn.length) {
                        logoutBtn.click(function (e) {
                            e.preventDefault();
                            $.ajax({
                                url: '/logout',
                                method: 'POST',
                                success: function (response) {
                                    alert(response.message);
                                    window.location.href = response.redirect;
                                }
                            });
                        });
                    }
                    $('#contact-form').find('#userId').val(data.user_id);
                } else {
                    userNameSpan.text('Đăng nhập');
                    userMenu.click(function () {
                        window.location.href = '/login';
                    });
                    userDropdown.hide();
                    $('#contact-form').find('#userId').val('');
                }
            }
        });
    }

    // Search functionality
    function setupSearch() {
        $('#searchBtn').click(function () {
            const query = $('#searchInput').val().trim();
            if (query) {
                window.location.href = `/products?search=${encodeURIComponent(query)}`;
            }
        });
        $('#searchInput').on('keypress', function (e) {
            if (e.which === 13) {
                const query = $(this).val().trim();
                if (query) {
                    window.location.href = `/products?search=${encodeURIComponent(query)}`;
                }
            }
        });
    }

    // Initialize functions
    setupUserMenu();
    setupSearch();
    fetchTopDiscountedProducts();
    fetchPopularProducts();
    fetchWebsiteReviews();

    // Only run on products page
    if (window.location.pathname.includes('products.html')) {
        function fetchProducts() {
            const urlParams = new URLSearchParams(window.location.search);
            const category = urlParams.get('category_id');
            const search = urlParams.get('search');
            const sort = $('#sortSelect').val() || 'default';
            const priceRange = $('#priceRangeFilter input:checked').val();
            const hasDiscount = $('#discountFilter').is(':checked');

            $.ajax({
                url: '/api/products',
                method: 'GET',
                data: {
                    category_id: category,
                    search: search,
                    sort: sort,
                    price_range: priceRange,
                    has_discount: hasDiscount
                },
                success: function (data) {
                    let html = '';
                    data.forEach(product => {
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
                                <p class="installment">0% qua thẻ tín dụng kỳ hạn 3-6...</p>
                                <button class="add-to-cart" onclick="addToCart(${product.id}, '${product.name}', ${product.discounted_price})">
                                    <i class="fas fa-cart-plus"></i> Thêm vào giỏ hàng
                                </button>
                            </div>
                        `;
                    });
                    $('#productGrid').html(html);
                    $('#productGrid .product-card').click(function (e) {
                        if (!$(e.target).closest('button').length) {
                            window.location.href = `/product-detail?id=${$(this).find('button').attr('onclick').match(/\d+/)[0]}`;
                        }
                    });
                },
                error: function () {
                    $('#productGrid').html('<p style="color: #e63946;">Lỗi khi tải sản phẩm.</p>');
                }
            });
        }

        fetchProducts();
        $('#sortSelect').change(fetchProducts);
        $('#filterForm').submit(function (e) {
            e.preventDefault();
            fetchProducts();
        });
    }
});