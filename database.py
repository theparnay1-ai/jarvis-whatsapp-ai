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