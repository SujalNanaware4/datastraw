from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
import os

app = FastAPI()

DATABASE_URL = "sqlite:///./tickets.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True)
    customer_name = Column(String, index=True)
    customer_email = Column(String, index=True)
    subject = Column(String, index=True)
    description = Column(Text)
    category = Column(String, default="General")
    priority = Column(String, default="Medium")
    status = Column(String, default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    notes = relationship("Note", back_populates="ticket", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, ForeignKey("tickets.ticket_id"))
    note_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    ticket = relationship("Ticket", back_populates="notes")


class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, ForeignKey("tickets.ticket_id"))
    to_email = Column(String)
    subject = Column(String)
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# First create all tables (for fresh deployments)
Base.metadata.create_all(bind=engine)

# Check if columns exist and add them if missing (for existing databases)
from sqlalchemy import text
with engine.connect() as conn:
    # Check for category column
    result = conn.execute(text("PRAGMA table_info(tickets)"))
    columns = [row[1] for row in result]
    if 'category' not in columns:
        conn.execute(text("ALTER TABLE tickets ADD COLUMN category TEXT DEFAULT 'General'"))
    if 'priority' not in columns:
        conn.execute(text("ALTER TABLE tickets ADD COLUMN priority TEXT DEFAULT 'Medium'"))
    conn.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TicketCreate(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    description: str
    category: Optional[str] = "General"
    priority: Optional[str] = "Medium"


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    note_text: str
    created_at: datetime


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    to_email: str
    subject: str
    body: str
    created_at: datetime


class TicketListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    status: str
    category: str
    priority: str
    created_at: datetime


class TicketDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    category: str
    priority: str
    created_at: datetime
    updated_at: datetime
    notes: List[NoteResponse] = []
    emails: List[EmailResponse] = []


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Ticket).count()
    open_count = db.query(Ticket).filter(Ticket.status == "Open").count()
    in_progress = db.query(Ticket).filter(Ticket.status == "In Progress").count()
    closed = db.query(Ticket).filter(Ticket.status == "Closed").count()
    total_emails = db.query(Email).count()
    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "closed": closed,
        "total_emails": total_emails
    }

@app.get("/api/emails", response_model=List[EmailResponse])
def get_all_emails(db: Session = Depends(get_db)):
    emails = db.query(Email).order_by(Email.created_at.desc()).all()
    return emails


@app.post("/api/tickets", response_model=dict)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    last_ticket = db.query(Ticket).order_by(Ticket.id.desc()).first()
    if last_ticket:
        last_num = int(last_ticket.ticket_id.split("-")[1])
        new_num = last_num + 1
    else:
        new_num = 1
    ticket_id_str = f"TKT-{new_num:03d}"

    db_ticket = Ticket(
        ticket_id=ticket_id_str,
        customer_name=ticket.customer_name,
        customer_email=ticket.customer_email,
        subject=ticket.subject,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Simulate email when ticket is created
    email_subject = f"New Ticket Created - {ticket_id_str}"
    email_body = f"Hello {ticket.customer_name},\n\nYour support ticket \"{ticket.subject}\" has been created successfully.\n\nTicket ID: {ticket_id_str}\nStatus: Open\n\nBest regards,\nDatastraw Support Team"
    new_email = Email(
        ticket_id=ticket_id_str,
        to_email=ticket.customer_email,
        subject=email_subject,
        body=email_body
    )
    db.add(new_email)
    db.commit()
    
    return {"ticket_id": db_ticket.ticket_id, "created_at": db_ticket.created_at}


@app.get("/api/tickets", response_model=List[TicketListResponse])
def get_tickets(status: Optional[str] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if search:
        search_lower = search.lower()
        query = query.filter(
            (Ticket.customer_name.ilike(f"%{search}%")) |
            (Ticket.customer_email.ilike(f"%{search}%")) |
            (Ticket.subject.ilike(f"%{search}%")) |
            (Ticket.ticket_id.ilike(f"%{search}%")) |
            (Ticket.description.ilike(f"%{search}%"))
        )
    tickets = query.order_by(Ticket.created_at.desc()).all()
    return tickets


@app.get("/api/tickets/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.put("/api/tickets/{ticket_id}", response_model=dict)
def update_ticket(ticket_id: str, update: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if update.status:
        ticket.status = update.status
        # Simulate status update email
        email_subject = f"Ticket Status Update - {ticket_id}"
        email_body = f"Hello {ticket.customer_name},\n\nYour support ticket \"{ticket.subject}\" has been updated.\n\nNew Status: {update.status}\n\nBest regards,\nDatastraw Support Team"
        new_email = Email(
            ticket_id=ticket_id,
            to_email=ticket.customer_email,
            subject=email_subject,
            body=email_body
        )
        db.add(new_email)
    if update.notes:
        new_note = Note(
            ticket_id=ticket_id,
            note_text=update.notes
        )
        db.add(new_note)
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return {"success": True, "updated_at": ticket.updated_at}


@app.get("/api/tickets/{ticket_id}/emails", response_model=List[EmailResponse])
def get_ticket_emails(ticket_id: str, db: Session = Depends(get_db)):
    emails = db.query(Email).filter(Email.ticket_id == ticket_id).order_by(Email.created_at.desc()).all()
    return emails


@app.delete("/api/emails", response_model=dict)
def clear_emails(db: Session = Depends(get_db)):
    db.query(Email).delete()
    db.commit()
    return {"success": True, "message": "All emails cleared"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.get("/create")
def read_create():
    return FileResponse("static/create.html")


@app.get("/ticket/{ticket_id}")
def read_ticket(ticket_id: str):
    return FileResponse("static/detail.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))
    print(f"\nServer starting up!")
    print(f"Access at: http://localhost:{port}")
    print("Press CTRL+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=port)