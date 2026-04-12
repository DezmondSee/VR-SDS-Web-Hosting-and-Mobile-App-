-- Phase 1: Database Setup
CREATE DATABASE IF NOT EXISTS vrsds_enterprise;
USE vrsds_enterprise;

-- Phase 2: Create Tables
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'user', -- 🔒 CHANGED: Now accepts specific job titles!
    is_active TINYINT(1) DEFAULT 1,
    security_question VARCHAR(255),
    security_answer VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE IF NOT EXISTS call_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    caller_id VARCHAR(20),
    scan_type VARCHAR(50) DEFAULT 'Voice',
    verdict ENUM('SCAM', 'SAFE') NOT NULL,
    confidence FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scam_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    reported_number VARCHAR(20) NOT NULL,
    description TEXT,
    status ENUM('pending', 'verified', 'dismissed') DEFAULT 'pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scan_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_name VARCHAR(255) NOT NULL,
    scam_probability FLOAT NOT NULL,
    prediction VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trusted_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    contact_name VARCHAR(100),
    phone_number VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Phase 3: Initial Data
-- 🔒 CHANGED: Injected the 3 specific separation-of-duties Admin accounts
INSERT INTO users (username, password_hash, email, role, is_active) 
VALUES 
('sys_admin', 'admin123', 'sys@uum.edu.my', 'System Administrator', 1),
('sec_admin', 'admin123', 'sec@uum.edu.my', 'Security Analyst', 1),
('res_admin', 'admin123', 'res@uum.edu.my', 'Research Lead', 1)
ON DUPLICATE KEY UPDATE role=VALUES(role);