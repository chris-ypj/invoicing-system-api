from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    contact_name = Column(String)
    contact_email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    projects = relationship("Project", back_populates="client")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="projects")
    invoices = relationship("Invoice", back_populates="project")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    invoice_number = Column(String, nullable=False, unique=True)

    lifecycle_status = Column(String, nullable=False, default="draft")
    payment_status = Column(String, nullable=False, default="unpaid")

    issue_date = Column(Date)
    due_date = Column(Date)

    subtotal = Column(Float, nullable=False, default=0)
    tax_rate = Column(Float, nullable=False, default=0.15)
    tax_amount = Column(Float, nullable=False, default=0)
    adjustment_total = Column(Float, nullable=False, default=0)
    credit_total = Column(Float, nullable=False, default=0)
    total_amount = Column(Float, nullable=False, default=0)

    created_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    sent_at = Column(DateTime)
    paid_at = Column(DateTime)

    rejection_reason = Column(Text)

    project = relationship("Project", back_populates="invoices")
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False, default=0)
    invoice = relationship("Invoice", back_populates="items")