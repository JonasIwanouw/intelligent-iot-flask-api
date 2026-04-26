-- Denne fil køres automatisk, når MySQL-containeren starter første gang
USE flask_demo;

CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    last_seen DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS sensor_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL,
    sensor_type VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    message VARCHAR(255),
    created_at DATETIME DEFAULT NOW()
);

INSERT INTO devices (name, location, status, customer_name, last_seen)
VALUES
('Sensor-ALB-001', 'Aalborg Wind Farm 1', 'online', 'Vestas', NOW()),
('Sensor-ALB-002', 'Aalborg Wind Farm 1', 'maintenance', 'Vestas', NOW()),
('Sensor-UK-101', 'Offshore Wind Park UK', 'offline', 'Siemens Gamesa', NOW());