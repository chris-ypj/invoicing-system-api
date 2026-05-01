INSERT INTO users (id, name, email, role) VALUES
(1, 'Alice', 'alice@company.com', 'staff'),
(2, 'Bob', 'bob@company.com', 'manager');

INSERT INTO clients (id, company_name, contact_name, contact_email) VALUES
(1, 'Acme Ltd', 'John Smith', 'john@acme.co.nz'),
(2, 'Bright Consulting', 'Emily Chen', 'emily@bright.co.nz');

INSERT INTO projects (id, client_id, name, description) VALUES
(1, 1, 'Website Redesign', 'Corporate website redesign'),
(2, 1, 'Advisory', 'Ongoing advisory services'),
(3, 2, 'System Review', 'Technical system review');

INSERT INTO invoices (
    id, project_id, invoice_number,
    lifecycle_status, payment_status,
    issue_date, due_date,
    subtotal, tax_rate, tax_amount,
    adjustment_total, credit_total, total_amount,
    created_by
) VALUES
(1, 1, 'INV-001', 'draft', 'unpaid', '2026-05-01', '2026-05-15', 1000, 0.15, 150, 0, 0, 1150, 1);

INSERT INTO invoices (
    id, project_id, invoice_number,
    lifecycle_status, payment_status,
    issue_date, due_date,
    subtotal, tax_rate, tax_amount,
    adjustment_total, credit_total, total_amount,
    created_by, approved_by, approved_at
) VALUES
(2, 2, 'INV-002', 'approved', 'unpaid', '2026-05-01', '2026-05-15', 2000, 0.15, 300, -100, 0, 2200, 1, 2, '2026-05-02');

INSERT INTO invoices (
    id, project_id, invoice_number,
    lifecycle_status, payment_status,
    issue_date, due_date,
    subtotal, tax_rate, tax_amount,
    adjustment_total, credit_total, total_amount,
    created_by, approved_by, approved_at, sent_at
) VALUES
(3, 3, 'INV-003', 'sent', 'unpaid', '2026-05-01', '2026-05-15', 1500, 0.15, 225, 0, 100, 1625, 1, 2, '2026-05-02', '2026-05-03');

INSERT INTO invoices (
    id, project_id, invoice_number,
    lifecycle_status, payment_status,
    issue_date, due_date,
    subtotal, tax_rate, tax_amount,
    adjustment_total, credit_total, total_amount,
    created_by, approved_by, approved_at, sent_at, paid_at
) VALUES
(4, 1, 'INV-004', 'sent', 'paid', '2026-05-01', '2026-05-15', 1200, 0.15, 180, 0, 0, 1380, 1, 2, '2026-05-02', '2026-05-03', '2026-05-05');

INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, line_total) VALUES
(1, 'Design workshop', 2, 500, 1000),
(2, 'Advisory service', 1, 2000, 2000),
(3, 'Technical review', 3, 500, 1500),
(4, 'Implementation work', 4, 300, 1200);