select *from services-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) DEFAULT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    email_token VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    token_expiry TIMESTAMP DEFAULT NULL,
    reset_token VARCHAR(255) DEFAULT NULL,
    reset_expiry TIMESTAMP DEFAULT NULL
);

-- Services Table
CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    project_description TEXT,
    project_status VARCHAR(50) NOT NULL CHECK (project_status IN ('Active', 'Completed', 'Pending')),
    project_link VARCHAR(255),
    project_type VARCHAR(50) DEFAULT 'website',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admins Table
CREATE TABLE admins (
    admin_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Super Admin', 'Admin')) DEFAULT 'Admin',
    is_active BOOLEAN DEFAULT TRUE,
    email_token VARCHAR(255),
    token_expiry TIMESTAMP,
    reset_token VARCHAR(255),
    reset_expiry TIMESTAMP,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings Table
CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    service_id INT REFERENCES services(service_id),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Pending', 'Completed', 'Canceled'))
);

-- Payments Table
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    booking_id INT REFERENCES bookings(booking_id),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2) NOT NULL,
    payment_status VARCHAR(50) NOT NULL CHECK (payment_status IN ('Pending', 'Paid', 'Failed'))
);

-- Balance Table
CREATE TABLE balance (
    balance_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    balance DECIMAL(10, 2) DEFAULT 0.00,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clients Testimonial Table
CREATE TABLE clients_testimonial (
    testimonial_id SERIAL PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    client_picture VARCHAR(255),
    workplace VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    project_worked_on VARCHAR(255) NOT NULL,
    testimonial_text TEXT NOT NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teams Table
CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    team_member_name VARCHAR(255) NOT NULL,
    professionalism VARCHAR(255) NOT NULL,
    role_played VARCHAR(255) NOT NULL,
    image_url VARCHAR(255),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO admins (
    email, 
    phone, 
    password_hash, 
    role, 
    is_active, 
    email_token, 
    token_expiry, 
    reset_token, 
    reset_expiry
) 
VALUES (
    'wamilimohillarie@gmail.com', 
    '0710578792', 
    'scrypt:32768:8:1$CZRBmyPfdm3tRuBR$803633d669657334fd004d2070aff51d22646dda30909f2660b1ad78232259552e65c31e82e24e09467cbec0276a8ea4d5f13b84fdc029d3e255f8b1b8680eea', 
    'Super Admin',   -- ✅ notice the space
    TRUE, 
    'sample_email_token', 
    NOW() + INTERVAL '1 day', 
    NULL, 
    NULL
);

select  *from admins

TRUNCATE TABLE admins RESTART IDENTITY CASCADE;

UPDATE admins
SET password_hash = 'scrypt:32768:8:1$QBZlDSecTYDF7P4W$ed4e75f0b29b71b028bb5b136530b11106ffdb507487faa7da2993c2de74944bf0817f57b19e777d546e325f5b5692f7dc5e9ba0c7c23468349970f4fa3ef5c7',
    date_updated = NOW()
WHERE email = 'wamilimohillarie@gmail.com';

