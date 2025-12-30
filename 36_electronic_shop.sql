-- Tạo database và sử dụng
CREATE DATABASE IF NOT EXISTS 36_electronic_shop;
USE 36_electronic_shop;

-- Bảng users (có cả thông tin role)
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  full_name VARCHAR(100) NOT NULL,
  birth_date DATE NOT NULL,
  total_purchased INT NOT NULL DEFAULT 0,
  role ENUM('customer', 'admin') NOT NULL DEFAULT 'customer',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    address_line VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_default TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_user_id (user_id)
);

-- Bảng categories
CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  image_url VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng products
CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  category_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  discount_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  discounted_price DECIMAL(10,2) AS (price * (1 - discount_percentage/100)) STORED,
  image_url VARCHAR(255) NOT NULL,
  stock_quantity INT NOT NULL DEFAULT 0,
  sold INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Bảng reviews
CREATE TABLE IF NOT EXISTS reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NOT NULL,
  comment TEXT NOT NULL,
  rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Bảng cart
CREATE TABLE IF NOT EXISTS cart (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL CHECK (quantity >= 1),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_cart_item (user_id, product_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Bảng order_activities (có address & phone luôn)
CREATE TABLE IF NOT EXISTS order_activities (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL CHECK (quantity >= 1),
  total_price DECIMAL(15,2) NOT NULL,
  status ENUM('Đang chờ giao', 'Đang giao', 'Đã giao') NOT NULL DEFAULT 'Đang chờ giao',
  address VARCHAR(255),
  phone VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  delivered_at TIMESTAMP NULL DEFAULT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE ON UPDATE CASCADE
);
-- Bảng website_reviews (Đánh giá trang web)
CREATE TABLE IF NOT EXISTS website_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- View tổng hợp đánh giá
CREATE VIEW product_avg_rating AS
SELECT
  product_id,
  ROUND(AVG(rating),1) AS avg_rating,
  COUNT(*) AS review_count
FROM reviews
GROUP BY product_id;
-- Thêm dữ liệu mẫu
-- Bảng users
INSERT INTO users (username, email, password, full_name, birth_date, total_purchased) VALUES
('nguyenvana', 'nguyenvana@example.com', '$2b$12$Kix2h0g8vN0vW1X9z2m2b.VW5J1vK8P0g9tL2X5vW3N6J9K8L2M5', 'Nguyễn Văn A', '1990-01-01', 10),
('tranthib', 'tranthib@example.com', '$2b$12$Kix2h0g8vN0vW1X9z2m2b.VW5J1vK8P0g9tL2X5vW3N6J9K8L2M5', 'Trần Thị B', '1995-05-15', 8),
('lethic', 'lethic@example.com', '$2b$12$Kix2h0g8vN0vW1X9z2m2b.VW5J1vK8P0g9tL2X5vW3N6J9K8L2M5', 'Lê Thị C', '1988-03-20', 2),
('phamvand', 'phamvand@example.com', '$2b$12$Kix2h0g8vN0vW1X9z2m2b.VW5J1vK8P0g9tL2X5vW3N6J9K8L2M5', 'Phạm Văn D', '1992-07-10', 4),
('hoangthie', 'hoangthie@example.com', '$2b$12$Kix2h0g8vN0vW1X9z2m2b.VW5J1vK8P0g9tL2X5vW3N6J9K8L2M5', 'Hoàng Thị E', '1997-11-25', 1);



-- Bảng categories
INSERT INTO categories (name, image_url) VALUES
('Điện thoại', 'https://images.pexels.com/photos/699122/pexels-photo-699122.jpeg'),
('Laptop', 'https://images.pexels.com/photos/205926/pexels-photo-205926.jpeg'),
('Tai nghe', 'https://images.pexels.com/photos/3944405/pexels-photo-3944405.jpeg'),
('Loa', 'https://images.pexels.com/photos/374087/pexels-photo-374087.jpeg');

-- Bảng products
-- Điện thoại
INSERT INTO products (category_id, name, description, price, discount_percentage, image_url, stock_quantity, sold) VALUES
(1, 'iPhone 14 Pro', 'Điện thoại với màn hình 6.1 inch, chip A16', 999.99, 10.00, 'https://images.pexels.com/photos/699122/pexels-photo-699122.jpeg', 50, 20),
(1, 'Samsung Galaxy S23', 'Điện thoại Android cao cấp, camera 50MP', 849.99, 15.00, 'https://images.pexels.com/photos/788946/pexels-photo-788946.jpeg', 60, 15),
(1, 'Google Pixel 8', 'Trải nghiệm Android thuần túy, AI tối ưu', 699.99, 5.00, 'https://images.pexels.com/photos/607812/pexels-photo-607812.jpeg', 45, 10),
(1, 'Xiaomi 13', 'Hiệu năng mạnh mẽ, giá cạnh tranh', 599.99, 8.00, 'https://images.pexels.com/photos/1092644/pexels-photo-1092644.jpeg', 70, 25),
(1, 'Oppo Find X5', 'Thiết kế sang trọng, sạc nhanh 80W', 799.99, 12.00, 'https://images.pexels.com/photos/248510/pexels-photo-248510.jpeg', 55, 30),
(1, 'Vivo V27', 'Camera selfie đỉnh cao, màn hình AMOLED', 499.99, 10.00, 'https://images.pexels.com/photos/399953/pexels-photo-399953.jpeg', 65, 12),
(1, 'OnePlus 11', 'Hiệu năng vượt trội, OxygenOS mượt mà', 749.99, 5.00, 'https://images.pexels.com/photos/47261/pexels-photo-47261.jpeg', 50, 18),
(1, 'Sony Xperia 1 V', 'Màn hình 4K HDR, âm thanh chất lượng', 899.99, 7.00, 'https://images.pexels.com/photos/788946/pexels-photo-788946.jpeg', 40, 22),
(1, 'Realme GT3', 'Sạc siêu nhanh 240W, hiệu năng mạnh', 649.99, 9.00, 'https://images.pexels.com/photos/607812/pexels-photo-607812.jpeg', 60, 17),
(1, 'Asus ROG Phone 7', 'Điện thoại gaming, Snapdragon 8 Gen 2', 999.99, 15.00, 'https://images.pexels.com/photos/248510/pexels-photo-248510.jpeg', 30, 28);

-- Laptop
INSERT INTO products (category_id, name, description, price, discount_percentage, image_url, stock_quantity, sold) VALUES
(2, 'Dell XPS 13', 'Laptop mỏng nhẹ, hiệu năng cao', 1299.99, 10.00, 'https://images.pexels.com/photos/205926/pexels-photo-205926.jpeg', 20, 15),
(2, 'MacBook Air M2', 'Chip M2, thiết kế mới, pin lâu', 1199.99, 5.00, 'https://images.pexels.com/photos/303383/pexels-photo-303383.jpeg', 25, 10),
(2, 'Lenovo ThinkPad X1', 'Laptop doanh nhân, độ bền cao', 1499.99, 8.00, 'https://images.pexels.com/photos/1229861/pexels-photo-1229861.jpeg', 15, 12),
(2, 'HP Spectre x360', 'Laptop 2-in-1, màn hình OLED', 1399.99, 12.00, 'https://images.pexels.com/photos/204790/pexels-photo-204790.jpeg', 30, 20),
(2, 'Asus ZenBook 14', 'Màn hình NanoEdge, nhẹ và mạnh', 1099.99, 10.00, 'https://images.pexels.com/photos/205926/pexels-photo-205926.jpeg', 35, 18),
(2, 'Acer Swift 3', 'Giá trị tốt, hiệu năng ổn định', 799.99, 7.00, 'https://images.pexels.com/photos/303383/pexels-photo-303383.jpeg', 40, 22),
(2, 'MSI Stealth 15M', 'Laptop gaming mỏng nhẹ', 1599.99, 5.00, 'https://images.pexels.com/photos/1229861/pexels-photo-1229861.jpeg', 20, 15),
(2, 'Surface Laptop 5', 'Thiết kế tối giản, Windows mượt mà', 1299.99, 9.00, 'https://images.pexels.com/photos/204790/pexels-photo-204790.jpeg', 25, 10),
(2, 'LG Gram 16', 'Siêu nhẹ, pin lên đến 20 giờ', 1399.99, 15.00, 'https://images.pexels.com/photos/205926/pexels-photo-205926.jpeg', 30, 17),
(2, 'Razer Blade 14', 'Laptop gaming cao cấp, RTX 4070', 1999.99, 10.00, 'https://images.pexels.com/photos/1229861/pexels-photo-1229861.jpeg', 15, 20);

-- Tai nghe
INSERT INTO products (category_id, name, description, price, discount_percentage, image_url, stock_quantity, sold) VALUES
(3, 'AirPods Pro 2', 'Tai nghe không dây, chống ồn chủ động', 249.99, 10.00, 'https://images.pexels.com/photos/3944405/pexels-photo-3944405.jpeg', 40, 25),
(3, 'Sony WH-1000XM5', 'Tai nghe over-ear, chất lượng âm thanh đỉnh cao', 399.99, 5.00, 'https://images.pexels.com/photos/577769/pexels-photo-577769.jpeg', 30, 18),
(3, 'Bose QC45', 'Chống ồn vượt trội, thoải mái đeo lâu', 329.99, 8.00, 'https://images.pexels.com/photos/685283/pexels-photo-685283.jpeg', 35, 20),
(3, 'JBL Live 660NC', 'Âm thanh mạnh mẽ, giá phải chăng', 199.99, 12.00, 'https://images.pexels.com/photos/3944405/pexels-photo-3944405.jpeg', 50, 15),
(3, 'Sennheiser Momentum 4', 'Pin 60 giờ, âm thanh chi tiết', 349.99, 10.00, 'https://images.pexels.com/photos/577769/pexels-photo-577769.jpeg', 25, 12),
(3, 'Anker Soundcore Q30', 'Chống ồn tốt, giá hợp lý', 79.99, 7.00, 'https://images.pexels.com/photos/685283/pexels-photo-685283.jpeg', 60, 22),
(3, 'Beats Solo 4', 'Thiết kế thời trang, âm bass mạnh', 199.99, 5.00, 'https://images.pexels.com/photos/3944405/pexels-photo-3944405.jpeg', 45, 18),
(3, 'Sony WF-1000XM5', 'Tai nghe true wireless, âm thanh lossless', 299.99, 9.00, 'https://images.pexels.com/photos/577769/pexels-photo-577769.jpeg', 30, 15),
(3, 'Jabra Elite 85t', 'Chống ồn, kết nối ổn định', 229.99, 15.00, 'https://images.pexels.com/photos/685283/pexels-photo-685283.jpeg', 40, 20),
(3, 'Samsung Galaxy Buds 2 Pro', 'Thiết kế nhỏ gọn, âm thanh 360', 199.99, 10.00, 'https://images.pexels.com/photos/3944405/pexels-photo-3944405.jpeg', 50, 25);

-- Loa
INSERT INTO products (category_id, name, description, price, discount_percentage, image_url, stock_quantity, sold) VALUES
(4, 'Bose SoundLink Revolve', 'Loa Bluetooth 360 độ, âm thanh sống động', 199.99, 10.00, 'https://images.pexels.com/photos/374087/pexels-photo-374087.jpeg', 40, 20),
(4, 'JBL Charge 5', 'Loa di động, pin 20 giờ, chống nước', 179.99, 15.00, 'https://images.pexels.com/photos/1059138/pexels-photo-1059138.jpeg', 50, 25),
(4, 'Sonos Roam', 'Loa thông minh, hỗ trợ Wi-Fi và Bluetooth', 179.99, 8.00, 'https://images.pexels.com/photos/374087/pexels-photo-374087.jpeg', 45, 15),
(4, 'Harman Kardon Onyx Studio 7', 'Âm thanh cao cấp, thiết kế sang trọng', 249.99, 12.00, 'https://images.pexels.com/photos/1059138/pexels-photo-1059138.jpeg', 30, 18),
(4, 'Ultimate Ears Boom 3', 'Loa di động, chống nước, âm thanh mạnh', 149.99, 10.00, 'https://images.pexels.com/photos/374087/pexels-photo-374087.jpeg', 60, 22),
(4, 'Sony SRS-XB43', 'Âm bass sâu, đèn LED tích hợp', 199.99, 7.00, 'https://images.pexels.com/photos/1059138/pexels-photo-1059138.jpeg', 40, 20),
(4, 'Anker Soundcore Motion+', 'Âm thanh Hi-Res, giá hợp lý', 99.99, 5.00, 'https://images.pexels.com/photos/374087/pexels-photo-374087.jpeg', 70, 25),
(4, 'Bose Home Speaker 300', 'Loa thông minh, hỗ trợ Alexa', 259.99, 9.00, 'https://images.pexels.com/photos/1059138/pexels-photo-1059138.jpeg', 25, 15),
(4, 'JBL PartyBox 110', 'Loa tiệc tùng, công suất lớn', 349.99, 15.00, 'https://images.pexels.com/photos/374087/pexels-photo-374087.jpeg', 20, 12),
(4, 'Sonos One', 'Loa thông minh, âm thanh đa phòng', 219.99, 10.00, 'https://images.pexels.com/photos/1059138/pexels-photo-1059138.jpeg', 30, 18);

-- Bảng reviews
INSERT INTO reviews (user_id, product_id, comment, rating) VALUES
(1, 1, 'Sản phẩm chất lượng, giao hàng nhanh, hỗ trợ nhiệt tình!', 4),
(2, 3, 'Tai nghe DEF âm thanh tuyệt vời, đáng giá từng đồng!', 5),
(3, 1, 'iPhone 14 Pro chất lượng, camera tuyệt vời!', 5),
(4, 1, 'iPhone 14 Pro xài ổn, đáng tiền.', 4),
(3, 2, 'Samsung Galaxy S23 hiệu năng mạnh, camera đẹp.', 5),
(4, 2, 'Samsung Galaxy S23 rất mượt mà.', 4),
(5, 3, 'Google Pixel 8 chụp ảnh đẹp, giao diện mượt.', 4),
(1, 3, 'Pixel 8 đáng giá trong tầm tiền.', 5),
(2, 4, 'Xiaomi 13 giá tốt, hiệu năng cao.', 4),
(3, 4, 'Xiaomi 13 rất đáng mua!', 5),
(4, 5, 'Oppo Find X5 thiết kế đẹp, sạc nhanh.', 5),
(5, 5, 'Oppo Find X5 màn hình đẹp, dùng ổn.', 4),
(1, 6, 'Vivo V27 selfie đẹp, màn hình sáng.', 4),
(2, 6, 'Vivo V27 rất tốt trong tầm giá.', 5),
(3, 7, 'OnePlus 11 nhanh, giao diện mượt.', 5),
(4, 7, 'OnePlus 11 đáng tiền, hiệu năng cao.', 4),
(5, 8, 'Sony Xperia 1 V màn hình 4K ấn tượng.', 4),
(1, 8, 'Sony Xperia 1 V âm thanh tuyệt vời.', 5),
(2, 9, 'Realme GT3 sạc nhanh kinh ngạc!', 5),
(3, 9, 'Realme GT3 hiệu năng mạnh, giá tốt.', 4),
(4, 10, 'Asus ROG Phone 7 chơi game rất đã.', 5),
(5, 10, 'ROG Phone 7 mạnh mẽ, phù hợp gaming.', 4),
(1, 11, 'Dell XPS 13 nhẹ, hiệu năng cao.', 4),
(2, 11, 'Dell XPS 13 rất đáng mua!', 5),
(3, 12, 'MacBook Air M2 pin lâu, thiết kế đẹp.', 5),
(4, 12, 'MacBook Air M2 mượt mà, đáng giá.', 4),
(5, 13, 'Lenovo ThinkPad X1 bền, phù hợp công việc.', 4),
(1, 13, 'ThinkPad X1 chất lượng tốt.', 5),
(2, 14, 'HP Spectre x360 màn hình OLED đẹp.', 5),
(3, 14, 'HP Spectre x360 linh hoạt, tiện dụng.', 4),
(4, 15, 'Asus ZenBook 14 nhẹ, hiệu năng ổn.', 4),
(5, 15, 'ZenBook 14 rất đáng giá!', 5),
(1, 16, 'Acer Swift 3 giá tốt, hiệu năng ổn.', 4),
(2, 16, 'Acer Swift 3 phù hợp sinh viên.', 5),
(3, 17, 'MSI Stealth 15M chơi game mượt.', 5),
(4, 17, 'MSI Stealth 15M thiết kế đẹp.', 4),
(5, 18, 'Surface Laptop 5 giao diện mượt, thiết kế đẹp.', 4),
(1, 18, 'Surface Laptop 5 rất tốt!', 5),
(2, 19, 'LG Gram 16 siêu nhẹ, pin lâu.', 5),
(3, 19, 'LG Gram 16 rất tiện cho di chuyển.', 4),
(4, 20, 'Razer Blade 14 mạnh mẽ, chơi game đỉnh.', 5),
(5, 20, 'Razer Blade 14 đáng giá cho game thủ.', 4),
(1, 21, 'AirPods Pro 2 chống ồn tốt, âm thanh hay.', 5),
(2, 21, 'AirPods Pro 2 rất đáng mua!', 4),
(3, 22, 'Sony WH-1000XM5 âm thanh tuyệt vời.', 5),
(4, 22, 'Sony WH-1000XM5 chất lượng đỉnh cao.', 4),
(5, 23, 'Bose QC45 chống ồn tốt, đeo thoải mái.', 4),
(1, 23, 'Bose QC45 rất đáng giá.', 5),
(2, 24, 'JBL Live 660NC âm thanh cân bằng.', 4),
(3, 24, 'JBL Live 660NC giá tốt, chất lượng ổn.', 5),
(4, 25, 'Sennheiser Momentum 4 pin lâu, âm thanh hay.', 5),
(5, 25, 'Sennheiser Momentum 4 rất đáng mua.', 4),
(1, 26, 'Anker Soundcore Q30 giá rẻ, chất lượng tốt.', 4),
(2, 26, 'Anker Soundcore Q30 rất đáng giá.', 5),
(3, 27, 'Beats Solo 4 bass mạnh, thiết kế đẹp.', 4),
(4, 27, 'Beats Solo 4 phù hợp nghe nhạc sôi động.', 5),
(5, 28, 'Sony WF-1000XM5 âm thanh lossless tuyệt vời.', 5),
(1, 28, 'Sony WF-1000XM5 nhỏ gọn, chất lượng cao.', 4),
(2, 29, 'Jabra Elite 85t chống ồn tốt, kết nối ổn.', 4),
(3, 29, 'Jabra Elite 85t rất đáng mua.', 5),
(4, 30, 'Samsung Galaxy Buds 2 Pro âm thanh 360 hay.', 5),
(5, 30, 'Galaxy Buds 2 Pro nhỏ gọn, tiện lợi.', 4),
(1, 31, 'Bose SoundLink Revolve âm thanh sống động.', 5),
(2, 31, 'Bose SoundLink Revolve rất đáng giá.', 4),
(3, 32, 'JBL Charge 5 pin lâu, chống nước tốt.', 5),
(4, 32, 'JBL Charge 5 chất lượng âm thanh tốt.', 4),
(5, 33, 'Sonos Roam nhỏ gọn, tiện lợi.', 4),
(1, 33, 'Sonos Roam hỗ trợ Wi-Fi tuyệt vời.', 5),
(2, 34, 'Harman Kardon Onyx Studio 7 thiết kế đẹp.', 5),
(3, 34, 'Harman Kardon Onyx Studio 7 âm thanh hay.', 4),
(4, 35, 'Ultimate Ears Boom 3 âm thanh mạnh, chống nước.', 4),
(5, 35, 'UE Boom 3 rất phù hợp cho dã ngoại.', 5),
(1, 36, 'Sony SRS-XB43 bass sâu, đèn LED đẹp.', 5),
(2, 36, 'Sony SRS-XB43 chất lượng tốt.', 4),
(3, 37, 'Anker Soundcore Motion+ âm thanh Hi-Res.', 4),
(4, 37, 'Anker Soundcore Motion+ giá tốt.', 5),
(5, 38, 'Bose Home Speaker 300 hỗ trợ Alexa tiện lợi.', 5),
(1, 38, 'Bose Home Speaker 300 âm thanh hay.', 4),
(2, 39, 'JBL PartyBox 110 công suất lớn, phù hợp tiệc.', 5),
(3, 39, 'JBL PartyBox 110 rất sôi động.', 4),
(4, 40, 'Sonos One âm thanh đa phòng tuyệt vời.', 5),
(5, 40, 'Sonos One thiết kế đẹp, chất lượng cao.', 4);
