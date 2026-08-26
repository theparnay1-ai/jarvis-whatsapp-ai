from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
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


class Message(Base):

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    whatsapp_message_id = Column(
        String,
        unique=True,
        index=True
    )

    sender = Column(String, index=True)

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
    message_id,
    sender,
    text,
    direction="incoming"
):

    db = SessionLocal()

    message = Message(
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


def save_response(message_id, response):

    db = SessionLocal()

    message = db.query(Message).filter(
        Message.whatsapp_message_id == message_id
    ).first()

    if message:

        message.response = response
        message.replied = 1

        db.commit()

    db.close()

def get_recent_messages(sender, limit=10):

    db = SessionLocal()

    messages = (
        db.query(Message)
        .filter(Message.sender == sender)
        .order_by(Message.timestamp.desc())
        .limit(limit)
        .all()
    )

    db.close()

    return list(reversed(messages))

class Memory(Base):

    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)

    sender = Column(
        String,
        index=True
    )

    memory = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

def save_memory(sender, memory_text):

    db = SessionLocal()

    memory = Memory(
        sender=sender,
        memory=memory_text
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    db.close()

    return memory

def get_memories(sender):

    db = SessionLocal()

    memories = (
        db.query(Memory)
        .filter(Memory.sender == sender)
        .order_by(Memory.created_at.asc())
        .all()
    )

    db.close()

    return memories

Base.metadata.create_all(bind=engine)

def update_memory(memory_id, new_memory):

    db = SessionLocal()

    memory = db.query(Memory).filter(
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
    sender,
    description,
    priority="normal"
):

    db = SessionLocal()

    issue = Issue(
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

def get_issue(issue_id):

    db = SessionLocal()

    issue = db.query(Issue).filter(
        Issue.id == issue_id
    ).first()

    db.close()

    return issue

def update_issue(
    issue_id,
    status=None,
    priority=None
):

    db = SessionLocal()

    issue = db.query(Issue).filter(
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
    sender,
    requirement,
    priority="normal"
):

    db = SessionLocal()

    lead = Lead(
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

def get_lead(lead_id):

    db = SessionLocal()

    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    db.close()

    return lead

def update_lead(
    lead_id,
    status=None,
    priority=None
):

    db = SessionLocal()

    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if lead:

        if status:
            lead.status = status

        if priority:
            lead.priority = priority

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
    sender,
    requested_start,
    requested_end,
    alternative_slots=None
):

    db = SessionLocal()

    meeting = Meeting(
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

    db = SessionLocal()

    meeting = Meeting(
        sender=sender,
        requested_start=requested_start,
        requested_end=requested_end,
        status="awaiting_confirmation"
    )

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    db.close()

    return meeting

def update_meeting(
    meeting_id,
    status=None,
    calendar_event_id=None
):

    db = SessionLocal()

    meeting = db.query(Meeting).filter(
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

def get_pending_meeting(sender):

    db = SessionLocal()

    meeting = (
        db.query(Meeting)
        .filter(
            Meeting.sender == sender,
            Meeting.status == "awaiting_confirmation"
        )
        .order_by(Meeting.created_at.desc())
        .first()
    )

    db.close()

    return meeting