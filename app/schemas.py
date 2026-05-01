from typing import Any, Optional, List
from datetime import date
from pydantic import BaseModel

# Lightweight wrapper for successful responses
# Keeps response format consistent without adding too much complexity
class APIResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Any] = None

# Request schema for creating a new client
class ClientCreate(BaseModel):
  company_name: str
  contact_name: Optional[str] = None
  contact_email: Optional[str] = None

# Response schema for returning client details
class ClientResponse(BaseModel):
  id: int
  company_name: str
  contact_name: Optional[str] = None
  contact_email: Optional[str] = None

class ProjectCreate(BaseModel):
  client_id: int
  name: str
  description: Optional[str] = None

class ProjectResponse(BaseModel):
  id: int
  client_id: int
  name: str
  description: Optional[str] = None

class InvoiceItemCreate(BaseModel):
    description: str
    quantity: float
    unit_price: float

class InvoiceCreate(BaseModel):
    project_id: int
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    items: List[InvoiceItemCreate]
    adjustment_total: Optional[float] = 0
    credit_total: Optional[float] = 0

class InvoiceItemUpdate(BaseModel):
  description: str
  quantity: float
  unit_price: float

class InvoiceUpdate(BaseModel):
  items: Optional[List[InvoiceItemUpdate]] = None
  adjustment_total: Optional[float] = None
  credit_total: Optional[float] = None
  due_date: Optional[date] = None

class RejectInvoiceRequest(BaseModel):
  reason: Optional[str] = None

class InvoiceResponse(BaseModel):
  id: int
  invoice_number: str
  lifecycle_status: str
  payment_status: str
  subtotal: float
  tax_amount: float
  adjustment_total: float
  credit_total: float
  total_amount: float