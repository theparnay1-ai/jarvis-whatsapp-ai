# AI-Powered WhatsApp Business Agent

AI-powered WhatsApp customer support agent built with Python, FastAPI,
Google Gemini, SQLite, and Google Calendar.

## 🚀 Features

- WhatsApp customer conversations
- Gemini-powered intent classification
- Conversation memory
- Customer context retrieval
- Complaint and issue management
- Priority detection
- Owner notifications
- Meeting scheduling
- Google Calendar integration
- Availability checking
- Alternative meeting slots
- Customer confirmation before booking
- Real-time calendar conflict checking
- REST API with FastAPI

## 🧠 Agent Workflow

WhatsApp Message
      ↓
FastAPI Webhook
      ↓
AI Agent
      ↓
Intent + Priority
      ↓
Tool Selection
      ↓
Database / Calendar / Notification
      ↓
AI Response
      ↓
WhatsApp

## 📅 Meeting Workflow

Customer requests meeting
        ↓
Extract date & time
        ↓
Check Google Calendar
        ↓
Available?
   ↓             ↓
 Yes            No
   ↓             ↓
Propose       Find alternatives
   ↓             ↓
Wait          Customer selects
confirmation       ↓
   ↓          Wait confirmation
Yes              ↓
   ↓          Re-check calendar
Book                ↓
   ↓              Book
Google Calendar



👨‍💻 Author



Parnay Rao



GitHub: https://github.com/theparnay1-ai



LinkedIn: https://www.linkedin.com/in/parnay-rao

