from fastapi import FastAPI, Depends, APIRouter
from requests import Request
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas import *
from app.services import *


app = FastAPI()
api_router = APIRouter(prefix="/v1")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_user_role(request: Request) -> str:
    return request.headers.get("X-User-Role", "staff")

def get_user_id(request: Request) -> int:
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return int(user_id)

def require_manager(request: Request):
    if get_user_role(request) != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can perform this action"
        )
def require_creator_or_manager(request: Request, invoice):
    user_id = get_user_id(request)
    role = get_user_role(request)
    if role != "manager" and invoice.created_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the creator or a manager can perform this action"
        )
@api_router.post("/clients")
def create_client_api(data: ClientCreate, db: Session = Depends(get_db)):
    client = create_client(db, data)
    return APIResponse(
        status="success",
        message="Client created successfully",
        data=ClientResponse(
            id=client.id,
            company_name=client.company_name,
            contact_name=client.contact_name,
            contact_email=client.contact_email,
        )
    )
@api_router.get("/clients")
def list_clients(db: Session = Depends(get_db)):
    clients = get_clients(db)
    return APIResponse(
        status="success",
        message="Clients retrieved successfully",
        data=[
            ClientResponse(
                id=c.id,
                company_name=c.company_name,
                contact_name=c.contact_name,
                contact_email=c.contact_email,
            )
            for c in clients
        ],
    )
@api_router.post("/projects")
def create_project_api(data: ProjectCreate, db: Session = Depends(get_db)):
    project = create_project(db, data)
    return APIResponse(
        status="success",
        message="Project created successfully",
        data=ProjectResponse(
            id=project.id,
            client_id=project.client_id,
            name=project.name,
            description=project.description,
        ),
    )
@api_router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    projects = get_projects(db)
    return APIResponse(
        status="success",
        message="Projects retrieved successfully",
        data=[
            ProjectResponse(
                id=p.id,
                client_id=p.client_id,
                name=p.name,
                description=p.description,
            )
            for p in projects
        ],
    )
@api_router.get("/projects/{project_id}")
def get_project_api(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    return APIResponse(
        status="success",
        message="Project retrieved successfully",
        data=ProjectResponse(
            id=project.id,
            client_id=project.client_id,
            name=project.name,
            description=project.description,
        ),
    )

def to_invoice_response(invoice):
    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        lifecycle_status=invoice.lifecycle_status,
        payment_status=invoice.payment_status,
        subtotal=invoice.subtotal,
        tax_amount=invoice.tax_amount,
        adjustment_total=invoice.adjustment_total,
        credit_total=invoice.credit_total,
        total_amount=invoice.total_amount,
    )
@api_router.post("/invoices")
def create_invoice_api(data: InvoiceCreate, request: Request,db: Session = Depends(get_db)):
    user_id = get_user_id(request)
    invoice = create_invoice(db, data, user_id)
    return APIResponse(
        status="success",
        message="Invoice created successfully",
        data=to_invoice_response(invoice),
    )
@api_router.get("/invoices")
def list_invoices(db: Session = Depends(get_db)):
    invoices = get_invoices(db)
    return APIResponse(
        status="success",
        message="Invoices retrieved successfully",
        data=[to_invoice_response(invoice) for invoice in invoices],
    )
@api_router.get("/invoices/{invoice_id}")
def get_invoice_api(invoice_id: int, db: Session = Depends(get_db)):
    invoice = get_invoice_by_id(db, invoice_id)
    return APIResponse(
        status="success",
        message="Invoice retrieved successfully",
        data=to_invoice_response(invoice)
    )
@api_router.get("/invoices/pending-approval")
def get_pending_approval_api(request: Request, db: Session = Depends(get_db)):
    # Only managers can view pending approval invoices
    require_manager(request)
    invoices = get_pending_approval_invoices(db)
    return APIResponse(
        status="success",
        message="Pending approval invoices retrieved",
        data=[to_invoice_response(invoice) for invoice in invoices],
    )
@api_router.patch("/invoices/{invoice_id}")
def update_invoice_api(invoice_id: int, data: InvoiceUpdate, request: Request, db: Session = Depends(get_db)):
    user_id = get_user_id(request)
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice.created_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the creator can update this invoice"
        )
    invoice = update_invoice(db, invoice_id, data)
    return APIResponse(
        status="success",
        message="Invoice updated successfully",
        data=to_invoice_response(invoice),
    )
@api_router.post("/invoices/{invoice_id}/submit")
def submit_invoice_api(
    invoice_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = get_user_id(request)
    invoice = get_invoice_by_id(db, invoice_id)

    if invoice.created_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the creator can submit this invoice"
        )
    invoice = submit_invoice(db, invoice_id)
    return APIResponse(
        status="success",
        message="Invoice submitted for approval",
        data=to_invoice_response(invoice),
    )
@api_router.post("/invoices/{invoice_id}/withdraw")
def withdraw_invoice_api(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = get_user_id(request)
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice.created_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the creator can withdraw this invoice"
        )
    invoice = withdraw_invoice(db, invoice_id)
    return APIResponse(
        status="success",
        message="Invoice withdrawn to draft",
        data=to_invoice_response(invoice),
    )
@api_router.post("/invoices/{invoice_id}/approve")
def approve_invoice_api(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    require_manager(request)
    user_id = get_user_id(request)
    invoice = approve_invoice(db, invoice_id, user_id=user_id)
    return APIResponse(
        status="success",
        message="Invoice approved successfully",
        data=to_invoice_response(invoice),
    )
@api_router.post("/invoices/{invoice_id}/reject")
def reject_invoice_api(invoice_id: int, data: RejectInvoiceRequest, request: Request, db: Session = Depends(get_db),):
    require_manager(request)
    invoice = reject_invoice(db, invoice_id, data.reason)
    return APIResponse(
        status="success",
        message="Invoice rejected and returned to draft",
        data=to_invoice_response(invoice),
    )
@api_router.post("/invoices/{invoice_id}/send")
def send_invoice_api(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    invoice = get_invoice_by_id(db, invoice_id)
    require_creator_or_manager(request, invoice)
    invoice = send_invoice(db, invoice_id)
    return APIResponse(
        status="success",
        message="Invoice sent successfully",
        data=to_invoice_response(invoice),
    )
@api_router.post("/invoices/{invoice_id}/mark-paid")
def mark_invoice_paid_api(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    invoice = get_invoice_by_id(db, invoice_id)
    require_creator_or_manager(request, invoice)
    invoice = mark_invoice_paid(db, invoice_id)
    return APIResponse(
        status="success",
        message="Invoice marked as paid",
        data=to_invoice_response(invoice),
    )
@api_router.get("/invoices/{invoice_id}/download")
def download_invoice_api(invoice_id: int, db: Session = Depends(get_db)):
    data = get_invoice_download_url(db, invoice_id)
    return APIResponse(
        status="success",
        message="Invoice download URL generated",
        data=data,
    )
app.include_router(api_router)