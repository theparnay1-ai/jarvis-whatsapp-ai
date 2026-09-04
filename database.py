from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


DATABASE_URL = "sqlite:///./chatbot.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ==============================
# SaaS MULTI-TENANT FOUNDATION
# ==============================

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    price_monthly = Column(Integer, default=0)
    max_customers = Column(Integer, default=100)
    max_messages = Column(Integer, default=1000)


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    industry = Column(String)
    description = Column(Text)
    email = Column(String)
    phone = Column(String)
    timezone = Column(String, default="Asia/Kolkata")
    created_at = Column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    status = Column(String, default="active")
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


class BusinessUser(Base):
    __tablename__ = "business_users"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="owner")
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):

    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    business_id = Column(
        Integer,
        ForeignKey("businesses.id"),
        nullable=True,
        index=True
    )

    sender = Column(
        String,
        index=True
    )

    message = Column(Text)

    direction = Column(String)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    replied = Column(
        Integer,
        default=0
    )

    response = Column(
        Text,
        nullable=True
    )


Base.metadata.create_all(bind=engine)


def message_exists(message_id):

    db = SessionLocal()

    message = db.query(Message).filter(
        Message.whatsapp_message_id == message_id
    ).first()

    db.close()

    return message is not None


def save_message(
    business_id,
    message_id,
    sender,
    text,
    direction="incoming"
):

    db = SessionLocal()

    message = Message(
        business_id=business_id,
        whatsapp_message_id=message_id,
        sender=sender,
        message=text,
        direction=direction
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    db.close()

    return message


def save_response(
    business_id,
    message_id,
    response
):

    db = SessionLocal()

    message = db.query(Message).filter(
        Message.business_id == business_id,
        Message.whatsapp_message_id == message_id
    ).first()

    if message:

        message.response = response
        message.replied = 1

        db.commit()

    db.close()

def get_recent_messages(
    business_id,
    sender,
    limit=10
):

    db = SessionLocal()

    messages = (
        db.query(Message)
        .filter(
            Message.business_id == business_id,
            Message.sender == sender
        )
        .order_by(Message.timestamp.desc())
        .limit(limit)
        .all()
    )

    db.close()

    return list(reversed(messages))

class Memory(Base):

    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)

    business_id = Column(
        Integer,
        ForeignKey("businesses.id"),
        nullable=True,
        index=True
    )

    sender = Column(
        String,
        index=True
    )

    memory = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

def save_memory(business_id, sender, memory_text):

    db = SessionLocal()

    memory = Memory(
        business_id=business_id,
        sender=sender,
        memory=memory_text
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    db.close()

    return memory

def get_memories(business_id, sender):

    db = SessionLocal()

    memories = (
        db.query(Memory)
        .filter(
            Memory.business_id == business_id,
            Memory.sender == sender
        )
        .order_by(Memory.created_at.asc())
        .all()
    )

    db.close()

    return memories

Base.metadata.create_all(bind=engine)

def update_memory(business_id, memory_id, new_memory):

    db = SessionLocal()

    memory = db.query(Memory).filter(
    Memory.business_id == business_id,
    Memory.id == memory_id
).first()

    if memory:

        memory.memory = new_memory

        db.commit()
        db.refresh(memory)

    db.close()

    return memory

class Issue(Base):

    __tablename__ = "issues"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    business_id = Column(
        Integer,
        ForeignKey("businesses.id"),
        nullable=True,
        index=True
    )

    sender = Column(
        String,
        index=True
    )

    description = Column(
        Text
    )

    priority = Column(
        String,
        default="normal"
    )

    status = Column(
        String,
        default="open"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

def create_issue(
    business_id,
    sender,
    description,
    priority="normal"
):

    db = SessionLocal()

    issue = Issue(
    business_id=business_id,
    sender=sender,
    description=description,
    priority=priority,
    status="open"
)

    db.add(issue)
    db.commit()
    db.refresh(issue)

    db.close()

    return issue

def get_issue(business_id, issue_id):

    db = SessionLocal()

    issue = db.query(Issue).filter(
        Issue.business_id == business_id,
        Issue.id == issue_id
    ).first()

    db.close()

    return issue

def update_issue(
    business_id,
    issue_id,
    status=None,
    priority=None
):

    db = SessionLocal()

    issue = db.query(Issue).filter(
    Issue.business_id == business_id,
    Issue.id == issue_id
).first()

    if issue:

        if status:
            issue.status = status

        if priority:
            issue.priority = priority

        db.commit()
        db.refresh(issue)

    db.close()

    return issue

class Lead(Base):

    __tablename__ = "leads"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    business_id = Column(
        Integer,
        ForeignKey("businesses.id"),
        nullable=True,
        index=True
    )

    sender = Column(
        String,
        index=True
    )

    requirement = Column(
        Text
    )

    priority = Column(
        String,
        default="normal"
    )

    status = Column(
        String,
        default="new"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

def create_lead(
    business_id,
    sender,
    requirement,
    priority="normal"
):

    db = SessionLocal()

    lead = Lead(
    business_id=business_id,
    sender=sender,
    requirement=requirement,
    priority=priority,
    status="new"
)

    db.add(lead)
    db.commit()
    db.refresh(lead)

    db.close()

    return lead

def get_lead(business_id, lead_id):

    db = SessionLocal()

    lead = db.query(Lead).filter(
    Lead.business_id == business_id,
    Lead.id == lead_id
).first()

    db.close()

    return lead

def update_lead(
    business_id,
    lead_id,
    status=None,
    priority=None,
    requirement=None
):

    db = SessionLocal()

    lead = db.query(Lead).filter(
    Lead.business_id == business_id,
    Lead.id == lead_id
).first()

    if lead:

        if status is not None:
            lead.status = status

        if priority is not None:
            lead.priority = priority

        if requirement is not None:
            lead.requirement = requirement

        db.commit()
        db.refresh(lead)

    db.close()

    return lead

class Meeting(Base):

    __tablename__ = "meetings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    business_id = Column(
        Integer,
        ForeignKey("businesses.id"),
        nullable=True,
        index=True
    )

    sender = Column(
        String,
        index=True
    )

    requested_start = Column(
        DateTime
    )

    requested_end = Column(
        DateTime
    )

    status = Column(
        String,
        default="pending"
    )

    calendar_event_id = Column(
        String,
        nullable=True
    )

    alternative_slots = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

def create_meeting_request(
    business_id,
    sender,
    requested_start,
    requested_end,
    alternative_slots=None
):

    db = SessionLocal()

    meeting = Meeting(
        business_id=business_id,
        sender=sender,
        requested_start=requested_start,
        requested_end=requested_end,
        status="awaiting_confirmation",
        alternative_slots=alternative_slots
    )

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    db.close()

    return meeting

def update_meeting(
    business_id,
    meeting_id,
    status=None,
    calendar_event_id=None
):

    db = SessionLocal()

    meeting = db.query(Meeting).filter(
    Meeting.business_id == business_id,
    Meeting.id == meeting_id
).first()

    if meeting:

        if status:
            meeting.status = status

        if calendar_event_id:
            meeting.calendar_event_id = calendar_event_id

        db.commit()
        db.refresh(meeting)

    db.close()

    return meeting

def get_pending_meeting(
    business_id,
    sender
):

    db = SessionLocal()

    meeting = (
    db.query(Meeting)
    .filter(
        Meeting.business_id == business_id,
        Meeting.sender == sender,
        Meeting.status == "awaiting_confirmation"
    )
    .order_by(Meeting.created_at.desc())
    .first()
)

    db.close()

    return meeting

class Customer(Base):

    __tablename__ = "customers"

    __table_args__ = (
    UniqueConstraint(
        "business_id",
        "sender",
        name="uq_customer_business_sender"
    ),
)

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    business_id = Column(
        Integer,
        ForeignKey("businesses.id"),
        nullable=True,
        index=True
    )

    sender = Column(
    String,
    index=True
)

    name = Column(
        String,
        nullable=True
    )

    email = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    last_interaction = Column(
        DateTime,
        default=datetime.utcnow
    )

Base.metadata.create_all(bind=engine)

def create_customer(
    business_id,
    sender,
    name=None,
    email=None
):

    db = SessionLocal()

    customer = Customer(
    business_id=business_id,
    sender=sender,
    name=name,
    email=email
)

    db.add(customer)
    db.commit()
    db.refresh(customer)

    db.close()

    return customer


def get_customer(
    business_id,
    sender
):

    db = SessionLocal()

    customer = (
    db.query(Customer)
    .filter(
        Customer.business_id == business_id,
        Customer.sender == sender
    )
    .first()
)

    db.close()

    return customer

def update_customer(
    business_id,
    sender,
    name=None,
    email=None
):

    db = SessionLocal()

    customer = (
    db.query(Customer)
    .filter(
        Customer.business_id == business_id,
        Customer.sender == sender
    )
    .first()
)

    if customer:

        if name:
            customer.name = name

        if email:
            customer.email = email

        customer.last_interaction = datetime.utcnow()

        db.commit()
        db.refresh(customer)

    db.close()

    return customer