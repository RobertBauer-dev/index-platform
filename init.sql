-- Initialize database with sample data
-- This script runs when the database container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Insert sample securities
INSERT INTO securities (symbol, name, exchange, currency, sector, industry, country, market_cap, is_active, created_at, updated_at)
VALUES
    ('AAPL', 'Apple Inc.', 'NASDAQ', 'USD', 'Technology', 'Consumer Electronics', 'USA', 3000000000000, true, NOW(), NOW()),
    ('MSFT', 'Microsoft Corporation', 'NASDAQ', 'USD', 'Technology', 'Software', 'USA', 2500000000000, true, NOW(), NOW()),
    ('GOOGL', 'Alphabet Inc.', 'NASDAQ', 'USD', 'Technology', 'Internet Services', 'USA', 1800000000000, true, NOW(), NOW()),
    ('AMZN', 'Amazon.com Inc.', 'NASDAQ', 'USD', 'Consumer Discretionary', 'E-commerce', 'USA', 1500000000000, true, NOW(), NOW()),
    ('TSLA', 'Tesla Inc.', 'NASDAQ', 'USD', 'Automotive', 'Electric Vehicles', 'USA', 800000000000, true, NOW(), NOW()),
    ('META', 'Meta Platforms Inc.', 'NASDAQ', 'USD', 'Technology', 'Social Media', 'USA', 700000000000, true, NOW(), NOW()),
    ('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'USD', 'Technology', 'Semiconductors', 'USA', 1200000000000, true, NOW(), NOW()),
    ('JPM', 'JPMorgan Chase & Co.', 'NYSE', 'USD', 'Financials', 'Banking', 'USA', 400000000000, true, NOW(), NOW()),
    ('JNJ', 'Johnson & Johnson', 'NYSE', 'USD', 'Healthcare', 'Pharmaceuticals', 'USA', 450000000000, true, NOW(), NOW()),
    ('V', 'Visa Inc.', 'NYSE', 'USD', 'Financials', 'Payment Processing', 'USA', 500000000000, true, NOW(), NOW());

-- Insert sample price data (last 30 days)
-- This would normally be populated by the data ingestion process
-- For demo purposes, we'll insert some sample data

-- Insert sample index definitions
INSERT INTO index_definitions (name, description, weighting_method, rebalance_frequency, max_constituents, is_active, created_at, updated_at)
VALUES
    ('Tech Giants Index', 'Equal-weighted index of major technology companies', 'equal_weight', 'monthly', 10, true, NOW(), NOW()),
    ('Large Cap Index', 'Market cap weighted index of large capitalization stocks', 'market_cap_weight', 'quarterly', 50, true, NOW(), NOW()),
    ('US Blue Chip Index', 'Equal-weighted index of US blue chip stocks', 'equal_weight', 'monthly', 30, true, NOW(), NOW());

-- Create default admin user
-- Password is 'admin123' (hashed with bcrypt)
INSERT INTO users (email, username, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
VALUES
    ('admin@indexplatform.com', 'admin', 'System Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7K1w8dF8eW', true, true, NOW(), NOW());
