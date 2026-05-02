# Invoicing System API
This project is a lightweight backend service for managing invoices, including creation, approval workflow, and reporting.
It demonstrates API design, business logic modelling, and access control in a realistic invoicing scenario.
---
## Features
- Client and project management
- Invoice creation and editing (draft mode)
- Invoice lifecycle workflow:
  - draft → pending approval → approved → sent → paid
  - support for reject and withdraw
- Role-based and ownership-based access control
- Reporting:
  - outstanding balances
  - billing history
- Mock authentication via request headers
---
## Tech Stack
- Python
- FastAPI
- SQLAlchemy
- SQLite

## Setup
Create and activate a virtual environment.
macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
Windows:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Database Setup
This project uses SQLite.
To create the local database and load sample data, run the following command:
```bash
sqlite3 invoicing.db < invoice_schema.sql
sqlite3 invoicing.db < seed.sql
```
On Windows, if sqlite3 is not available, install SQLite first or use a SQLite GUI tool to run invoice_schema.sql and seed.sql.

---
## Run the backend
```bash
uvicorn app.main:app --reload
```
Swagger documentation:
http://localhost:8000/docs
---
## Mock Authentication
The project uses request headers to simulate a logged-in user.
Example staff user:
X-User-Id: 1
X-User-Role: staff
Example manager user:
X-User-Id: 2
X-User-Role: manager
Default values are provided for local testing.
---
## API Overview
Clients
* POST /v1/clients – Create a new client
* GET /v1/clients – List all clients
Projects
* POST /v1/projects – Create a new project
* GET /v1/projects – List all projects
* GET /v1/projects/{project_id} – Get project details
Invoices
* POST /v1/invoices – Create invoice (draft)
* GET /v1/invoices – List invoices
* GET /v1/invoices/{invoice_id} – Get invoice details
* PATCH /v1/invoices/{invoice_id} – Update invoice (draft only)
Invoice Workflow
* POST /v1/invoices/{invoice_id}/submit – Submit for approval
* POST /v1/invoices/{invoice_id}/withdraw – Withdraw to draft
* POST /v1/invoices/{invoice_id}/approve – Approve (manager only)
* POST /v1/invoices/{invoice_id}/reject – Reject (manager only)
* POST /v1/invoices/{invoice_id}/send – Send invoice
* POST /v1/invoices/{invoice_id}/mark-paid – Mark as paid
Approval
* GET /v1/invoices/pending-approval – List invoices pending approval (manager only)
Utilities
* GET /v1/invoices/{invoice_id}/download – Get invoice download URL
Reports
* GET /v1/reports/outstanding – Outstanding balances grouped by project
* GET /v1/reports/billing-history – Billing history
---
## Notes
* SQLite is used for local development.
* Authentication is mocked for this prototype.
* Invoice PDF generation is not implemented; the download endpoint returns a mock URL.