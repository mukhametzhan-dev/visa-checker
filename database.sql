CREATE DATABASE bot_db;

USE bot_db;

CREATE TABLE Available_dates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE User_info (
    user_id BIGINT PRIMARY KEY,
    user_date VARCHAR(20) NOT NULL
);
