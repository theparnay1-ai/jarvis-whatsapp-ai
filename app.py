import os
from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from fastapi import Query
from client import should_reply
from agent.agent import process_message
from memory import process_memory
from whatsapp import send_whatsapp_message
from database import (
    BusinessUser,
    SessionLocal,
    message_exists,
    save_message,
    save_response,
    get_recent_messages,
    get_memories,
    get_customer,
    create_customer,
    Customer,
    Lead,
    Issue,
    Knowledge,
    Meeting
)
import bcrypt
from jose import jwt
from datetime import timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from rag import add_knowledge, update_knowledge, delete_knowledge
security = HTTPBearer()

business_id = 1

load_dotenv()


SECRET = os.getenv("JWT_SECRET")
if not SECRET:
    raise RuntimeError("JWT_SECRET is missing")

app = FastAPI(
    title="AI WhatsApp Customer Management Agent",
    description=(
        "AI-powered WhatsApp automation backend with "
        "customer CRM, lead qualification, issue tracking, "
        "Google Calendar scheduling, and protected admin APIs."
    ),
    version="2.0.0"
)

@app.post("/login")
def login(email: str, password: str):

    db = SessionLocal()
    user = db.query(BusinessUser).filter(BusinessUser.email == email).first()
    db.close()

    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {"user_id": user.id, "business_id": user.business_id},
        SECRET,
        algorithm="HS256"
    )

    return {"access_token": token}

def get_business_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        data = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
        return data["business_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def admin_dashboard():

    with open("templates/admin.html", "r", encoding="utf-8") as file:
        html = file.read()

    return HTMLResponse(content=html)


@app.get("/", tags=["System"])
def home():
    return {
        "status": "online",
        "message": "ChatBot backend is running"
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "healthy"
    }


@app.get("/webhook", tags=["WhatsApp"])
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):

    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")

    if (
        hub_mode == "subscribe"
        and hub_verify_token == verify_token
    ):
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse(
        "Verification failed",
        status_code=403
    )


@app.post("/webhook", tags=["WhatsApp"])
async def receive_webhook(request: Request):

    data = await request.json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        sender = message["from"]
        message_id = message["id"]
        message_type = message["type"]

        # Create customer profile if this is a new customer
        customer = get_customer(business_id, sender)

        if not customer:
            create_customer(business_id, sender)

            print("New customer profile created.")

        else:
            print("Existing customer profile found.")

        # Ignore non-text messages
        if message_type != "text":
            return {"status": "ignored"}

        text = message["text"]["body"]

        print("=" * 50)
        print("NEW WHATSAPP MESSAGE")
        print("Sender:", sender)
        print("Message:", text)
        print("Message ID:", message_id)
        print("=" * 50)

        # Check if we already processed this message
        if message_exists(message_id):

            print("Duplicate message ignored.")

            return {
                "status": "duplicate"
            }

                # Save incoming message
        save_message(
    business_id=business_id,
    message_id=message_id,
    sender=sender,
    text=text,
    direction="incoming"
)

        print("Message saved to database.")

        process_memory(
                business_id,
                sender,
                text
            )

        print("Message saved to database.")

        # Decide whether JARVIS should reply
        reply_needed = should_reply(text)

        print("Should reply:", reply_needed)

        if not reply_needed:

            print("Message ignored.")

            return {
                "status": "ignored"
            }

        # Get recent conversation
        recent_messages = get_recent_messages(
            business_id,
            sender,
            limit=10
        )

        long_term_memories = get_memories(
            business_id,
            sender)
        memory_context = []

        for memory in long_term_memories:
            memory_context.append(
                memory.memory
            )

        conversation_history = []

        for item in recent_messages:

            conversation_history.append({
                "message": item.message,
                "response": item.response
            })

        # Generate AI response
        # Process message through the AI agent
        agent_result = process_message(
            business_id,
            sender,
            text
        )

        reply = agent_result["response"]

        print("Agent Result:", agent_result)
        print("AI Reply:", reply)

        # Save AI response
        save_response(
    business_id=business_id,
    message_id=message_id,
    response=reply
)

        # Send response to WhatsApp
        send_whatsapp_message(
            sender,
            reply
        )

        return {
            "status": "replied"
        }

    except (KeyError, IndexError, TypeError) as e:

        print("Webhook event ignored:", e)

        return {
            "status": "ignored"
        }
    

def verify_business(
    business_id: int = Depends(get_business_id)
):
    return business_id

@app.get("/admin/knowledge")
def get_admin_knowledge(
    business_id: int = Depends(verify_business)
):
    db = SessionLocal()
    items = db.query(Knowledge).filter(
        Knowledge.business_id == business_id
    ).all()
    db.close()
    return items

@app.post("/admin/knowledge")
def create_knowledge(
    title: str,
    content: str,
    business_id: int = Depends(verify_business)
):
    return add_knowledge(business_id, title, content)

@app.patch("/admin/knowledge/{knowledge_id}")
def update_admin_knowledge(
    knowledge_id: int,
    title: str,
    content: str,
    business_id: int = Depends(verify_business)
):
    item = update_knowledge(business_id, knowledge_id, title, content)

    if not item:
        raise HTTPException(status_code=404, detail="Knowledge not found")

    return item

@app.delete("/admin/knowledge/{knowledge_id}")
def delete_admin_knowledge(
    knowledge_id: int,
    business_id: int = Depends(verify_business)
):
    if not delete_knowledge(business_id, knowledge_id):
        raise HTTPException(status_code=404, detail="Knowledge not found")

    return {"success": True}
    
@app.get(
    "/admin/customers",
    tags=["Admin"],
    summary="View customers",
    description="Retrieve customer profiles stored by the WhatsApp AI agent."
)
def get_admin_customers(
    business_id: int = Depends(verify_business)
):

    db = SessionLocal()

    customers = db.query(Customer).filter(
    Customer.business_id == business_id
).all()

    result = []

    for customer in customers:

        result.append({
            "id": customer.id,
            "sender": customer.sender,
            "name": customer.name,
            "email": customer.email,
            "created_at": customer.created_at,
            "last_interaction": customer.last_interaction
        })

    db.close()

    return {
        "count": len(result),
        "customers": result
    }

@app.patch("/admin/customers/{customer_id}", tags=["Admin"])
def update_admin_customer(
    customer_id: int,
    name: str = None,
    email: str = None,
    business_id: int = Depends(verify_business)
):
    db = SessionLocal()

    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.business_id == business_id
    ).first()

    if not customer:
        db.close()
        raise HTTPException(status_code=404, detail="Customer not found")

    if name is not None:
        customer.name = name
    if email is not None:
        customer.email = email

    db.commit()
    db.refresh(customer)
    db.close()

    return {
        "success": True,
        "customer": {
            "id": customer.id,
            "sender": customer.sender,
            "name": customer.name,
            "email": customer.email,
            "created_at": customer.created_at,
            "last_interaction": customer.last_interaction
        }
    }
@app.get("/admin/leads", tags=["Admin"])
def get_admin_leads(
    business_id: int = Depends(verify_business),
    status: str = None,
    priority: str = None
):
    db = SessionLocal()

    query = db.query(Lead).filter(Lead.business_id == business_id)

    if status:
        query = query.filter(Lead.status == status)
    if priority:
        query = query.filter(Lead.priority == priority)

    leads = query.all()

    result = [{
        "id": lead.id,
        "sender": lead.sender,
        "requirement": lead.requirement,
        "priority": lead.priority,
        "status": lead.status,
        "created_at": lead.created_at
    } for lead in leads]

    db.close()

    return {"count": len(result), "leads": result}

@app.patch("/admin/leads/{lead_id}", tags=["Admin"])
def update_admin_lead(
    lead_id: int,
    status: str = None,
    priority: str = None,
    business_id: int = Depends(verify_business)
):
    db = SessionLocal()

    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.business_id == business_id
    ).first()

    if not lead:
        db.close()
        raise HTTPException(status_code=404, detail="Lead not found")

    if status:
        lead.status = status
    if priority:
        lead.priority = priority

    db.commit()
    db.refresh(lead)
    db.close()

    return {
        "success": True,
        "lead": {
            "id": lead.id,
            "sender": lead.sender,
            "requirement": lead.requirement,
            "priority": lead.priority,
            "status": lead.status,
            "created_at": lead.created_at
        }
    }

@app.get("/admin/issues", tags=["Admin"])
def get_admin_issues(
    business_id: int = Depends(verify_business),
    status: str = None,
    priority: str = None
):
    db = SessionLocal()

    query = db.query(Issue).filter(Issue.business_id == business_id)

    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)

    issues = query.all()

    result = [{
        "id": issue.id,
        "sender": issue.sender,
        "description": issue.description,
        "priority": issue.priority,
        "status": issue.status,
        "created_at": issue.created_at
    } for issue in issues]

    db.close()

    return {"count": len(result), "issues": result}


@app.get("/admin/meetings", tags=["Admin"])
def get_admin_meetings(
    business_id: int = Depends(verify_business),
    status: str = None
):
    db = SessionLocal()

    query = db.query(Meeting).filter(Meeting.business_id == business_id)

    if status:
        query = query.filter(Meeting.status == status)

    meetings = query.all()

    result = [{
        "id": meeting.id,
        "sender": meeting.sender,
        "requested_start": meeting.requested_start,
        "requested_end": meeting.requested_end,
        "status": meeting.status,
        "calendar_event_id": meeting.calendar_event_id,
        "created_at": meeting.created_at
    } for meeting in meetings]

    db.close()

    return {"count": len(result), "meetings": result}

@app.get("/admin/stats", tags=["Admin"])
def get_admin_stats(business_id: int = Depends(verify_business)):
    db = SessionLocal()

    total_customers = db.query(Customer).filter(Customer.business_id == business_id).count()
    total_leads = db.query(Lead).filter(Lead.business_id == business_id).count()
    open_issues = db.query(Issue).filter(Issue.business_id == business_id, Issue.status == "open").count()
    booked_meetings = db.query(Meeting).filter(Meeting.business_id == business_id, Meeting.status == "booked").count()
    pending_meetings = db.query(Meeting).filter(Meeting.business_id == business_id, Meeting.status == "awaiting_confirmation").count()

    db.close()

    return {
        "customers": total_customers,
        "leads": total_leads,
        "open_issues": open_issues,
        "booked_meetings": booked_meetings,
        "pending_meetings": pending_meetings
    }
@app.patch("/admin/issues/{issue_id}", tags=["Admin"])
def update_admin_issue(
    issue_id: int,
    status: str = None,
    priority: str = None,
    business_id: int = Depends(verify_business)
):
    db = SessionLocal()

    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.business_id == business_id
    ).first()

    if not issue:
        db.close()
        raise HTTPException(status_code=404, detail="Issue not found")

    if status:
        issue.status = status
    if priority:
        issue.priority = priority

    db.commit()
    db.refresh(issue)
    db.close()

    return {
        "success": True,
        "issue": {
            "id": issue.id,
            "sender": issue.sender,
            "description": issue.description,
            "priority": issue.priority,
            "status": issue.status,
            "created_at": issue.created_at
        }
    }

@app.patch("/admin/meetings/{meeting_id}", tags=["Admin"])
def update_admin_meeting(
    meeting_id: int,
    status: str = None,
    business_id: int = Depends(verify_business)
):
    db = SessionLocal()

    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.business_id == business_id
    ).first()

    if not meeting:
        db.close()
        raise HTTPException(status_code=404, detail="Meeting not found")

    if status:
        meeting.status = status

    db.commit()
    db.refresh(meeting)
    db.close()

    return {
        "success": True,
        "meeting": {
            "id": meeting.id,
            "sender": meeting.sender,
            "requested_start": meeting.requested_start,
            "requested_end": meeting.requested_end,
            "status": meeting.status,
            "calendar_event_id": meeting.calendar_event_id
        }
    }