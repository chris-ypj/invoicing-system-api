DROP TABLE IF EXISTS invoice_items;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS users;
-- Enable foreign key constraints (important for SQLite)
PRAGMA foreign_keys = ON;
-- =========================
-- USERS
-- =========================
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('staff', 'manager')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- CLIENTS
-- =========================
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_name TEXT,
    contact_email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- PROJECTS
-- =========================
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- =========================
-- INVOICES
-- =========================
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    invoice_number TEXT NOT NULL UNIQUE,

    -- lifecycle status
    lifecycle_status TEXT NOT NULL DEFAULT 'draft'
        CHECK (lifecycle_status IN ('draft', 'pending_approval', 'approved', 'sent')),

    -- payment status
    payment_status TEXT NOT NULL DEFAULT 'unpaid'
        CHECK (payment_status IN ('unpaid', 'paid')),

    issue_date DATE,
    due_date DATE,

    -- financial fields
    subtotal REAL NOT NULL DEFAULT 0,
    tax_rate REAL NOT NULL DEFAULT 0.15,
    tax_amount REAL NOT NULL DEFAULT 0,
    adjustment_total REAL NOT NULL DEFAULT 0,
    credit_total REAL NOT NULL DEFAULT 0,
    total_amount REAL NOT NULL DEFAULT 0,

    -- minimal metadata
    created_by INTEGER,
    approved_by INTEGER,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    rejected_at DATETIME,
    sent_at DATETIME,
    paid_at DATETIME,

    rejection_reason TEXT,

    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- =========================
-- INVOICE ITEMS
-- =========================
CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity REAL NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    line_total REAL NOT NULL DEFAULT 0,

    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
);