import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from fastapi import Query
from client import should_reply
from agent.agent import process_message
from memory import process_memory
from whatsapp import send_whatsapp_message
from database import (
    message_exists,
    save_message,
    save_response,
    get_recent_messages,
    get_memories
)

load_dotenv()

app = FastAPI(
    title="Parnay AI ChatBot",
    description="AI-powered WhatsApp chatbot",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "ChatBot backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/webhook")
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


@app.post("/webhook")
async def receive_webhook(request: Request):

    data = await request.json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        sender = message["from"]
        message_id = message["id"]
        message_type = message["type"]

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
            message_id,
            sender,
            text,
            "incoming"
        )

        print("Message saved to database.")

        process_memory(
                sender,
                text
            )       

        reply_needed = should_reply(text)

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
            sender,
            limit=10
        )

        long_term_memories = get_memories(sender)
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
            sender,
            text
        )

        reply = agent_result["response"]

        print("Agent Result:", agent_result)
        print("AI Reply:", reply)

        # Save AI response
        save_response(
            message_id,
            reply
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