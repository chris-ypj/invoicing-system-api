from datetime import datetime
from fastapi import HTTPException
from app import models
from sqlalchemy.orm import Session
from app.config import TAX_RATE
from datetime import datetime
from app.config import NZ_TZ
datetime.now(NZ_TZ)

def calculate_invoice_totals(items, adjustment_total=0, credit_total=0):
    subtotal = 0
    for item in items:
        subtotal += item.quantity * item.unit_price
    tax_amount = subtotal * TAX_RATE
    total_amount = subtotal + tax_amount + adjustment_total - credit_total
    return {
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
    }

def create_client(db: Session, data):
    client = models.Client(
        company_name=data.company_name,
        contact_name=data.contact_name,
        contact_email=data.contact_email,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

def get_clients(db):
    """
    Retrieve all clients
    Used for listing clients in the system
    """
    return db.query(models.Client).all()

def create_project(db: Session, data):
    """
    Create a new project under a client
    Ensures the referenced client exists before creating the project
    """
    # Validate client exists
    client = db.query(models.Client).filter(models.Client.id == data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    # Create project
    project = models.Project(
        client_id=data.client_id,
        name=data.name,
        description=data.description,
    )
    # Persist to database
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def get_projects(db: Session):
    return db.query(models.Project).all()

def get_project_by_id(db: Session, project_id: int):
    """
    Retrieve a single project by id
    Raises 404 if the project does not exist
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def create_invoice(db: Session, data, user_id: int):
    """
    Create a new invoice with items.
    Validates project and client, calculates financial fields,
    and persists invoice and items in a single transaction.
    """
    # Validate project exists
    project = db.query(models.Project).filter(models.Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Defensive check: ensure client exists
    client = db.query(models.Client).filter(models.Client.id == project.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    # Generate simple incremental invoice number
    invoice_count = db.query(models.Invoice).count()
    invoice_number = f"INV-{invoice_count + 1:03d}"

    adjustment_total = data.adjustment_total or 0
    credit_total = data.credit_total or 0

    # Calculate financial values
    totals = calculate_invoice_totals(
        data.items,
        adjustment_total,
        credit_total
    )

    invoice = models.Invoice(
        project_id=data.project_id,
        invoice_number=invoice_number,
        lifecycle_status="draft",
        payment_status="unpaid",
        issue_date=data.issue_date,
        due_date=data.due_date,
        subtotal=totals["subtotal"],
        tax_rate=TAX_RATE,
        tax_amount=totals["tax_amount"],
        adjustment_total=adjustment_total,
        credit_total=credit_total,
        total_amount=totals["total_amount"],
        created_by=user_id,
    )
    try:
        # Persist invoice first to obtain generated ID
        db.add(invoice)
        db.flush()

        # Create invoice items
        for item in data.items:
            db.add(models.InvoiceItem(
                invoice_id=invoice.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.quantity * item.unit_price,
            ))

        db.commit()
        db.refresh(invoice)
        return invoice

    except Exception:
        db.rollback()
        raise

# Retrieve all invoices
def get_invoices(db: Session):
    return db.query(models.Invoice).all()

def get_invoice_by_id(db: Session, invoice_id: int):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

def get_pending_approval_invoices(db: Session):
    return db.query(models.Invoice).filter(
        models.Invoice.lifecycle_status == "pending_approval"
    ).all()

def update_invoice(db: Session, invoice_id: int, data):
    """
    Update an existing invoice (partial update).
    Only draft invoices can be modified.
    Rebuilds items if provided and recalculates all financial values.
    """
    invoice = get_invoice_by_id(db, invoice_id)
    # Only allow updates in draft state
    if invoice.lifecycle_status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft invoices can be updated"
        )
    try:
        items_for_calculation = None
        # Rebuild items if provided
        if data.items is not None:
            db.query(models.InvoiceItem).filter(
                models.InvoiceItem.invoice_id == invoice.id
            ).delete()

            for item in data.items:
                db.add(models.InvoiceItem(
                    invoice_id=invoice.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.quantity * item.unit_price,
                ))
            items_for_calculation = data.items
        # Update adjustment / credit if provided
        if data.adjustment_total is not None:
            invoice.adjustment_total = data.adjustment_total

        if data.credit_total is not None:
            invoice.credit_total = data.credit_total

        # Update due date if provided
        if data.due_date is not None:
            invoice.due_date = data.due_date

        # Use existing items if not updated
        if items_for_calculation is None:
            items_for_calculation = invoice.items

        # Recalculate totals
        totals = calculate_invoice_totals(
            items_for_calculation,
            invoice.adjustment_total or 0,
            invoice.credit_total or 0
        )

        invoice.subtotal = totals["subtotal"]
        invoice.tax_amount = totals["tax_amount"]
        invoice.total_amount = totals["total_amount"]

        db.commit()
        db.refresh(invoice)
        return invoice

    except Exception:
        db.rollback()
        raise

def submit_invoice(db: Session, invoice_id: int):
    """
    Submit invoice for approval
    """
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice.lifecycle_status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft invoices can be submitted"
        )
    invoice.lifecycle_status = "pending_approval"
    invoice.submitted_at = datetime.now(NZ_TZ)
    db.commit()
    db.refresh(invoice)
    return invoice

def withdraw_invoice(db: Session, invoice_id: int):
    """
    Withdraw invoice back to draft
    """
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice.lifecycle_status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="Only pending approval invoices can be withdrawn"
        )
    invoice.lifecycle_status = "draft"
    db.commit()
    db.refresh(invoice)
    return invoice

def approve_invoice(db: Session, invoice_id: int, user_id: int):
    """
    Approve a pending invoice
    """
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice.lifecycle_status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="Only pending approval invoices can be approved"
        )
    invoice.lifecycle_status = "approved"
    invoice.approved_by = user_id
    invoice.approved_at = datetime.now(NZ_TZ)
    invoice.rejection_reason = None
    invoice.rejected_at = None
    db.commit()
    db.refresh(invoice)
    return invoice

def reject_invoice(db: Session, invoice_id: int, reason: str | None = None):
    """
    Reject a pending invoice back to draft
    """
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice.lifecycle_status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="Only pending approval invoices can be rejected"
        )
    invoice.lifecycle_status = "draft"
    invoice.rejected_at = datetime.now(NZ_TZ)
    invoice.rejection_reason = reason
    db.commit()
    db.refresh(invoice)
    return invoice

def send_invoice(db: Session, invoice_id: int):
    """
    Mark an approved invoice as sent
    """
    invoice = get_invoice_by_id(db, invoice_id)

    if invoice.lifecycle_status != "approved":
        raise HTTPException(
            status_code=400,
            detail="Only approved invoices can be sent"
        )
    invoice.lifecycle_status = "sent"
    invoice.sent_at = datetime.now(NZ_TZ)
    db.commit()
    db.refresh(invoice)
    return invoice

def mark_invoice_paid(db: Session, invoice_id: int):
    """
    Mark a sent invoice as paid
    """
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice.lifecycle_status != "sent":
        raise HTTPException(
            status_code=400,
            detail="Only sent invoices can be marked as paid"
        )
    if invoice.payment_status == "paid":
        raise HTTPException(
            status_code=400,
            detail="Invoice is already paid"
        )
    invoice.payment_status = "paid"
    invoice.paid_at = datetime.now(NZ_TZ)
    db.commit()
    db.refresh(invoice)
    return invoice

def get_invoice_download_url(db: Session, invoice_id: int):
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice.lifecycle_status not in ("sent", "approved"):
        raise HTTPException(
            status_code=400,
            detail="Invoice must be approved or sent before download"
        )
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        # In production, the PDF would be stored in AWS S3 and accessed via a URL.
        # Here we return a mock URL for simplicity.
        "download_url": f"https://storage.example.com/invoices/{invoice.invoice_number}.pdf",
    }

def get_outstanding_report(db: Session):
    """
    Reporting function to get total outstanding amounts grouped by project
    """
    invoices = db.query(models.Invoice).all()
    project_map = {}
    total_outstanding = 0

    for invoice in invoices:
        outstanding = 0 if invoice.payment_status == "paid" else invoice.total_amount
        total_outstanding += outstanding

        if invoice.project_id not in project_map:
            project_map[invoice.project_id] = {
                "project_id": invoice.project_id,
                "project_outstanding": 0,
                "invoices": [],
            }
        project_map[invoice.project_id]["project_outstanding"] += outstanding
        project_map[invoice.project_id]["invoices"].append({
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "lifecycle_status": invoice.lifecycle_status,
            "payment_status": invoice.payment_status,
            "subtotal": invoice.subtotal,
            "tax_amount": invoice.tax_amount,
            "adjustment_total": invoice.adjustment_total,
            "credit_total": invoice.credit_total,
            "total_amount": invoice.total_amount,
            "outstanding_amount": outstanding,
        })

    return {
        "total_outstanding": total_outstanding,
        "projects": list(project_map.values()),
    }

def get_billing_history_report(db: Session):
    """
    Reporting function to get all invoices sorted by creation date (newest first)
    Used for billing history report
    """
    invoices = db.query(models.Invoice).order_by(
        models.Invoice.created_at.desc()
    ).all()
    return invoices