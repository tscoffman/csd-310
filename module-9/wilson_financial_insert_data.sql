/* 
===================================================================================
Title: Module 9.1 Wilson Financial Insert Data - Milestone 2
Original Author: Wade Eckert, Trenten Coffman
Date Modified: 18 February 2026
Description: This script inserts data into the Wilson Financial database schema, which 
includes tables for employees, clients, accounts, assets, holdings, and transactions. 
===================================================================================
*/

/*
  Insert order (FK-safe):
  1) employees
  2) clients
  3) accounts
  4) assets
  5) holdings
  6) transactions
*/

USE wilson_financial;

-- Reset for repeatable runs (Just for development/testing for school project - in production settings, we would not typically truncate like this)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE transactions;
TRUNCATE TABLE holdings;
TRUNCATE TABLE assets;
TRUNCATE TABLE accounts;
TRUNCATE TABLE clients;
TRUNCATE TABLE employees;
SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- 1) employees - 4 total, including 2 advisors 
-- ------------------------------------------------------------
INSERT INTO employees (employee_id, first_name, last_name, role, hire_date, active_flag) VALUES
(1, 'Jake',    'Willson',   'Co-Founder, Financial Advisor (CFA)',           '2023-01-02', 1),
(2, 'Ned',     'Willson',   'Co-Founder, Financial Advisor (CFA, MBA)',      '2023-01-02', 1),
(3, 'Phoenix', 'Two Star',  'Office Administrator (Scheduling, Supplies)',   '2023-01-15', 1),
(4, 'June',    'Santos',    'Compliance Manager (Part-Time, SEC Compliance)','2023-02-01', 1);

-- ------------------------------------------------------------
-- 2) clients
--   - 2 older clients (NOT in last 6 months)
--   - 4 clients within last 6 months (for the “clients added past six months” report)
-- Advisors: Jake=1, Ned=2
-- ------------------------------------------------------------
INSERT INTO clients (client_id, advisor_id, first_name, last_name, email, phone, start_date, active_flag) VALUES
(1, 1, 'Miguel',   'Ortega',    'miguel.ortega@example.com',    '505-555-0111', '2024-05-10', 1),
(2, 2, 'Evelyn',   'Hart',      'evelyn.hart@example.com',     '505-555-0120', '2025-02-18', 1),
(3, 1, 'Carla',    'Ortega',    'carla.ortega@example.com',     '505-555-0112', '2025-09-03', 1),
(4, 2, 'Dwayne',   'Fletcher',  'dwayne.fletcher@example.com', '505-555-0130', '2025-11-12', 1),
(5, 1, 'Rosa',     'Delgado',   'rosa.delgado@example.com',    '505-555-0140', '2025-12-05', 1),
(6, 2, 'Harold',   'Bennett',   'harold.bennett@example.com',  '505-555-0150', '2026-01-09', 1);

-- ------------------------------------------------------------
-- 3) accounts (1 per client for clarity)
-- ------------------------------------------------------------
INSERT INTO accounts (account_id, client_id, account_type, opened_date, active_flag) VALUES
(1, 1, 'Taxable Brokerage', '2024-05-15', 1),
(2, 2, 'Traditional IRA',   '2025-02-20', 1),
(3, 3, 'Roth IRA',          '2025-09-07', 1),
(4, 4, 'Taxable Brokerage', '2025-11-14', 1),
(5, 5, 'SEP IRA',           '2025-12-07', 1),
(6, 6, 'Taxable Brokerage', '2026-01-12', 1);

-- ------------------------------------------------------------
-- 4) assets - 6 total, mix of stocks and ETFs, with real ticker symbols for realism
-- ------------------------------------------------------------
INSERT INTO assets (asset_id, symbol, asset_name, asset_category) VALUES
(1, 'VTI',  'Vanguard Total Stock Market ETF',        'ETF'),
(2, 'VXUS', 'Vanguard Total International Stock ETF', 'ETF'),
(3, 'BND',  'Vanguard Total Bond Market ETF',         'ETF'),
(4, 'AAPL', 'Apple Inc.',                              'Stock'),
(5, 'MSFT', 'Microsoft Corp.',                         'Stock'),
(6, 'TLT',  'iShares 20+ Year Treasury Bond ETF',      'ETF');

-- ------------------------------------------------------------
-- 5) holdings
-- Purposeful totals so “average assets per client” yields meaningful variation.
-- Each account has 2 holdings, totals differ per client.
-- Note: UNIQUE(account_id, asset_id) respected.
-- ------------------------------------------------------------
INSERT INTO holdings (holding_id, account_id, asset_id, quantity, value_usd, value_as_of_date) VALUES
-- Account 1 (Client 1) 
(1, 1, 1, 120.000000, 28800.00, '2026-02-01'),  -- VTI
(2, 1, 2,  60.000000,  3600.00, '2026-02-01'),  -- VXUS

-- Account 2 (Client 2) 
(3, 2, 3, 140.000000, 10920.00, '2026-02-01'),  -- BND
(4, 2, 6,  35.000000,  3325.00, '2026-02-01'),  -- TLT

-- Account 3 (Client 3) 
(5, 3, 1,  25.000000,  6000.00, '2026-02-01'),  -- VTI
(6, 3, 3,  30.000000,  2340.00, '2026-02-01'),  -- BND

-- Account 4 (Client 4) 
(7, 4, 4,  20.000000,  3800.00, '2026-02-01'),  -- AAPL
(8, 4, 5,  18.000000,  7200.00, '2026-02-01'),  -- MSFT

-- Account 5 (Client 5) 
(9,  5, 1,  35.000000,  8400.00, '2026-02-01'), -- VTI
(10, 5, 2,  25.000000,  1500.00, '2026-02-01'), -- VXUS

-- Account 6 (Client 6) 
(11, 6, 6,  12.000000,  1140.00, '2026-02-01'), -- TLT
(12, 6, 3,  20.000000,  1560.00, '2026-02-01'); -- BND

-- ------------------------------------------------------------
-- 6) transactions
-- Requirements:
--   - Keep 11 transactions for account 1 in Jan 2026 (for the >10/month report)
-- Notes:
--   - amount_usd must be >= 0
-- ------------------------------------------------------------
INSERT INTO transactions (transaction_id, account_id, transaction_date, transaction_type, amount_usd, description) VALUES
-- Account 1: 11 transactions in Jan 2026 (the >10 in a month report)
(1,  1, '2026-01-02', 'Deposit',  5000.00, 'Monthly funding'),
(2,  1, '2026-01-03', 'Buy',       900.00, 'Buy VTI'),
(3,  1, '2026-01-04', 'Buy',       450.00, 'Buy VXUS'),
(4,  1, '2026-01-06', 'Buy',       600.00, 'Buy VTI'),
(5,  1, '2026-01-08', 'Buy',       300.00, 'Buy BND'),
(6,  1, '2026-01-10', 'Buy',       250.00, 'Buy VTI'),
(7,  1, '2026-01-12', 'Deposit',   700.00, 'Additional funding'),
(8,  1, '2026-01-14', 'Buy',       400.00, 'Buy VXUS'),
(9,  1, '2026-01-18', 'Buy',       200.00, 'Buy BND'),
(10, 1, '2026-01-22', 'Buy',       350.00, 'Buy VTI'),
(11, 1, '2026-01-28', 'Buy',       500.00, 'Buy VTI'),

-- Other accounts: a few in Jan 2026 (still below 10), plus some in Dec 2025
(12, 2, '2025-12-05', 'Contribution',  600.00, 'Year-end IRA contribution'),
(13, 2, '2026-01-07', 'Buy',           400.00, 'Buy BND'),
(14, 2, '2026-01-21', 'Buy',           300.00, 'Buy TLT'),

(15, 3, '2025-12-12', 'Contribution',  350.00, 'Roth IRA contribution'),
(16, 3, '2026-01-09', 'Buy',           250.00, 'Buy VTI'),
(17, 3, '2026-01-23', 'Buy',           150.00, 'Buy BND'),

(18, 4, '2026-01-05', 'Deposit',      1200.00, 'Account funding'),
(19, 4, '2026-01-06', 'Buy',           600.00, 'Buy MSFT'),
(20, 4, '2026-01-20', 'Buy',           400.00, 'Buy AAPL'),

(21, 5, '2025-12-18', 'Contribution',  500.00, 'SEP IRA contribution'),
(22, 5, '2026-01-11', 'Buy',           300.00, 'Buy VTI'),
(23, 5, '2026-01-27', 'Buy',           200.00, 'Buy VXUS'),

(24, 6, '2026-01-13', 'Deposit',       800.00, 'Initial funding'),
(25, 6, '2026-01-14', 'Buy',           300.00, 'Buy BND'),
(26, 6, '2026-01-29', 'Buy',           200.00, 'Buy TLT');
