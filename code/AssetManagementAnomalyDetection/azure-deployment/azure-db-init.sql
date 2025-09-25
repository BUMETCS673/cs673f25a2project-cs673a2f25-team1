-- Azure SQL Database initialization script
-- Run this script in Azure SQL Database after creating the database

-- Create tables for Asset Management Anomaly Detection System
CREATE TABLE portfolios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    manager NVARCHAR(100) NOT NULL,
    total_assets FLOAT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE()
);

CREATE TABLE assets (
    id INT IDENTITY(1,1) PRIMARY KEY,
    portfolio_id INT NOT NULL,
    symbol NVARCHAR(10) NOT NULL,
    name NVARCHAR(100) NOT NULL,
    quantity FLOAT NOT NULL,
    purchase_price FLOAT NOT NULL,
    current_price FLOAT NULL,
    purchase_date DATE NOT NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

CREATE TABLE fees (
    id INT IDENTITY(1,1) PRIMARY KEY,
    portfolio_id INT NOT NULL,
    amount FLOAT NOT NULL,
    date DATE NOT NULL,
    fee_type NVARCHAR(50) NOT NULL,
    description NVARCHAR(MAX) NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

CREATE TABLE anomalies (
    id INT IDENTITY(1,1) PRIMARY KEY,
    portfolio_id INT NOT NULL,
    fee_id INT NOT NULL,
    anomaly_score FLOAT NOT NULL,
    detected_at DATETIME2 DEFAULT GETUTCDATE(),
    reviewed BIT DEFAULT 0,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
    FOREIGN KEY (fee_id) REFERENCES fees(id)
);

-- Insert sample data for testing
INSERT INTO portfolios (name, manager, total_assets) VALUES
('Tech Growth Fund', 'Alpha Asset Management', 1000000.00),
('Balanced Portfolio', 'Beta Investment Co', 2500000.00),
('Conservative Fund', 'Gamma Financial', 500000.00);

INSERT INTO assets (portfolio_id, symbol, name, quantity, purchase_price, current_price, purchase_date) VALUES
(1, 'AAPL', 'Apple Inc', 100, 150.00, 175.00, '2023-01-15'),
(1, 'GOOGL', 'Alphabet Inc', 50, 2800.00, 3200.00, '2023-02-20'),
(2, 'MSFT', 'Microsoft Corp', 200, 300.00, 350.00, '2023-03-10'),
(2, 'TSLA', 'Tesla Inc', 25, 200.00, 250.00, '2023-04-05');

INSERT INTO fees (portfolio_id, amount, date, fee_type, description) VALUES
(1, 5000.00, '2023-01-01', 'management', 'Monthly management fee'),
(1, 5200.00, '2023-02-01', 'management', 'Monthly management fee'),
(1, 15000.00, '2023-03-01', 'management', 'Anomalous high fee'),
(2, 12000.00, '2023-01-01', 'management', 'Monthly management fee'),
(2, 12500.00, '2023-02-01', 'management', 'Monthly management fee'),
(3, 2500.00, '2023-01-01', 'management', 'Monthly management fee');

PRINT 'Azure SQL Database tables created successfully with sample data';
