/* 
===================================================================================
Title: Module 9.1 Wilson Financial Create Schema- Milestone 2
Original Author: Wade Eckert, Trenten Coffman
Date Modified: 18 February 2026
Description: This script creates the database schema for Wilson Financial, a fictional 
financial advisory firm. The schema includes tables for employees, clients, accounts, 
assets, holdings, and transactions, along with appropriate relationships and constraints 
to ensure data integrity. 
===================================================================================
*/

DROP DATABASE IF EXISTS wilson_financial;
CREATE DATABASE wilson_financial
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE wilson_financial;

-- ------------------------------------------------------------
-- Employees
-- ------------------------------------------------------------
CREATE TABLE employees (
  employee_id INT NOT NULL AUTO_INCREMENT,
  first_name  VARCHAR(50) NOT NULL,
  last_name   VARCHAR(50) NOT NULL,
  role        VARCHAR(100) NOT NULL,
  hire_date   DATE NOT NULL,
  active_flag TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (employee_id),
  CONSTRAINT chk_employees_active_flag CHECK (active_flag IN (0, 1))
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Clients (each client is assigned to one advisor, an employee)
-- ------------------------------------------------------------
CREATE TABLE clients (
  client_id   INT NOT NULL AUTO_INCREMENT,
  advisor_id  INT NOT NULL,
  first_name  VARCHAR(50) NOT NULL,
  last_name   VARCHAR(50) NOT NULL,
  email       VARCHAR(255) NULL,
  phone       VARCHAR(25) NULL,
  start_date  DATE NOT NULL,
  active_flag TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (client_id),
  KEY idx_clients_advisor_id (advisor_id),
  CONSTRAINT fk_clients_advisor
    FOREIGN KEY (advisor_id) REFERENCES employees(employee_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT chk_clients_active_flag CHECK (active_flag IN (0, 1))
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Accounts (each account belongs to one client)
-- ------------------------------------------------------------
CREATE TABLE accounts (
  account_id   INT NOT NULL AUTO_INCREMENT,
  client_id    INT NOT NULL,
  account_type VARCHAR(50) NULL,
  opened_date  DATE NOT NULL,
  active_flag  TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (account_id),
  KEY idx_accounts_client_id (client_id),
  CONSTRAINT fk_accounts_client
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT chk_accounts_active_flag CHECK (active_flag IN (0, 1))
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Assets (catalog of investable assets)
-- ------------------------------------------------------------
CREATE TABLE assets (
  asset_id        INT NOT NULL AUTO_INCREMENT,
  symbol          VARCHAR(15) NULL,
  asset_name      VARCHAR(150) NOT NULL,
  asset_category  VARCHAR(50) NULL,
  PRIMARY KEY (asset_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Holdings (bridge between accounts and assets)
-- UNIQUE(account_id, asset_id) prevents duplicate rows for the same asset in the same account
-- ------------------------------------------------------------
CREATE TABLE holdings (
  holding_id       INT NOT NULL AUTO_INCREMENT,
  account_id       INT NOT NULL,
  asset_id         INT NOT NULL,
  quantity         DECIMAL(18,6) NULL,
  value_usd        DECIMAL(14,2) NOT NULL,
  value_as_of_date DATE NOT NULL,
  PRIMARY KEY (holding_id),
  UNIQUE KEY uq_holdings_account_asset (account_id, asset_id),
  KEY idx_holdings_account_id (account_id),
  KEY idx_holdings_asset_id (asset_id),
  CONSTRAINT fk_holdings_account
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT fk_holdings_asset
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Transactions (activity on an account)
-- ------------------------------------------------------------
CREATE TABLE transactions (
  transaction_id   INT NOT NULL AUTO_INCREMENT,
  account_id       INT NOT NULL,
  transaction_date DATE NOT NULL,
  transaction_type VARCHAR(50) NOT NULL,
  amount_usd       DECIMAL(14,2) NOT NULL,
  description      VARCHAR(255) NULL,
  PRIMARY KEY (transaction_id),
  KEY idx_transactions_account_id (account_id),
  CONSTRAINT fk_transactions_account
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT chk_transactions_amount CHECK (amount_usd >= 0)
) ENGINE=InnoDB;
