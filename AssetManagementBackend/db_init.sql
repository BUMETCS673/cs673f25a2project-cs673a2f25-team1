-- Database initialization script for Microsoft SQL Server
-- Run this script to create the database and tables

CREATE DATABASE AssetManagement;
GO

USE AssetManagement;
GO

-- Create portfolios table
CREATE TABLE portfolios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    manager NVARCHAR(100) NOT NULL,
    total_assets FLOAT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Create assets table
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

-- Create fees table
CREATE TABLE fees (
    id INT IDENTITY(1,1) PRIMARY KEY,
    portfolio_id INT NOT NULL,
    amount FLOAT NOT NULL,
    date DATE NOT NULL,
    fee_type NVARCHAR(50) NOT NULL,
    description NVARCHAR(MAX) NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

-- Create anomalies table
CREATE TABLE anomalies (
    id INT IDENTITY(1,1) PRIMARY KEY,
    portfolio_id INT NOT NULL,
    fee_id INT NOT NULL,
    anomaly_score FLOAT NOT NULL,
    detected_at DATETIME2 DEFAULT GETDATE(),
    reviewed BIT DEFAULT 0,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
    FOREIGN KEY (fee_id) REFERENCES fees(id)
);

-- Create indexes for better performance
CREATE INDEX idx_assets_portfolio_id ON assets(portfolio_id);
CREATE INDEX idx_fees_portfolio_id ON fees(portfolio_id);
CREATE INDEX idx_fees_date ON fees(date);
CREATE INDEX idx_anomalies_portfolio_id ON anomalies(portfolio_id);
CREATE INDEX idx_anomalies_fee_id ON anomalies(fee_id);

-- Insert sample data
INSERT INTO portfolios (name, manager, total_assets) VALUES
('Tech Growth Fund', 'Jane Smith', 50000000.00),
('Balanced Portfolio', 'John Doe', 25000000.00),
('Conservative Fund', 'Alice Johnson', 100000000.00);

INSERT INTO assets (portfolio_id, symbol, name, quantity, purchase_price, current_price, purchase_date) VALUES
(1, 'AAPL', 'Apple Inc.', 1000, 150.00, 175.00, '2023-01-15'),
(1, 'MSFT', 'Microsoft Corp.', 500, 300.00, 350.00, '2023-02-01'),
(2, 'GOOGL', 'Alphabet Inc.', 200, 2500.00, 2700.00, '2023-03-10');

INSERT INTO fees (portfolio_id, amount, date, fee_type, description) VALUES
(1, 0.015, '2023-01-31', 'management', 'Monthly management fee'),
(1, 0.016, '2023-02-28', 'management', 'Monthly management fee'),
(1, 0.014, '2023-03-31', 'management', 'Monthly management fee'),
(1, 0.020, '2023-04-30', 'management', 'Monthly management fee - anomalous'),
(1, 0.015, '2023-05-31', 'management', 'Monthly management fee'),
(2, 0.012, '2023-01-31', 'management', 'Monthly management fee'),
(2, 0.013, '2023-02-28', 'management', 'Monthly management fee'),
(2, 0.011, '2023-03-31', 'management', 'Monthly management fee'),
(2, 0.018, '2023-04-30', 'management', 'Monthly management fee - anomalous');

GO
