\# 🤖 JARVIS — WhatsApp AI Assistant



JARVIS is an AI-powered WhatsApp assistant built with Python, FastAPI, Google Gemini, and the WhatsApp Cloud API.



The project combines natural-language AI, WhatsApp messaging, conversation memory, and long-term user memory into a modular backend system.



\---



\## 🚀 Features



\- 💬 AI-powered WhatsApp conversations

\- 🧠 Recent conversation memory

\- 🧠 Long-term user memory

\- 🤖 Google Gemini integration

\- 📱 WhatsApp Cloud API integration

\- ⚡ FastAPI webhook backend

\- 🗄️ SQLite database with SQLAlchemy

\- 🔐 Environment-variable based API credentials

\- 🔄 Duplicate WhatsApp message detection

\- 🇮🇳 English and Hinglish-friendly responses



\---



\## 🧠 How It Works



```text

&#x20;                   WhatsApp User

&#x20;                         │

&#x20;                         ▼

&#x20;                WhatsApp Cloud API

&#x20;                         │

&#x20;                         ▼

&#x20;                   FastAPI Webhook

&#x20;                         │

&#x20;                         ▼

&#x20;                Message Processing

&#x20;                         │

&#x20;             ┌───────────┴───────────┐

&#x20;             │                       │

&#x20;             ▼                       ▼

&#x20;     Conversation Memory       Long-Term Memory

&#x20;       Recent messages        Important user facts

&#x20;             │                       │

&#x20;             └───────────┬───────────┘

&#x20;                         ▼

&#x20;                    Google Gemini

&#x20;                         │

&#x20;                         ▼

&#x20;                   AI Response

&#x20;                         │

&#x20;                         ▼

&#x20;                WhatsApp Cloud API

&#x20;                         │

&#x20;                         ▼

&#x20;                   WhatsApp User



🛠️ Tech Stack

| Technology         | Purpose                   |

| ------------------ | ------------------------- |

| Python             | Core application          |

| FastAPI            | Webhook/API backend       |

| Google Gemini      | AI processing             |

| WhatsApp Cloud API | Messaging                 |

| SQLAlchemy         | Database ORM              |

| SQLite             | Local database            |

| Requests           | HTTP requests             |

| python-dotenv      | Environment configuration |

| Uvicorn            | ASGI server               |



📂 Project Structure

jarvis-whatsapp-ai/

│

├── app.py

├── client.py

├── database.py

├── whatsapp.py

│

├── requirements.txt

├── .env.example

├── .gitignore

└── README.md



File Responsibilities



app.py



Main FastAPI application and WhatsApp webhook.



client.py



Handles Gemini AI processing, reply detection, conversation context, and memory extraction.



database.py



Handles SQLite database models, messages, conversation history, and long-term memories.



whatsapp.py



Handles sending messages through the WhatsApp Cloud API.



File Responsibilities



app.py



Main FastAPI application and WhatsApp webhook.



client.py



Handles Gemini AI processing, reply detection, conversation context, and memory extraction.



database.py



Handles SQLite database models, messages, conversation history, and long-term memories.



whatsapp.py



Handles sending messages through the WhatsApp Cloud API.



⚙️ Installation

1\. Clone the repository

git clone https://github.com/theparnay1-ai/jarvis-whatsapp-ai.git

cd jarvis-whatsapp-ai

2\. Create a virtual environment



Windows:



python -m venv .venv



Activate it:



.venv\\Scripts\\Activate.ps1

3\. Install dependencies

pip install -r requirements.txt

🔐 Environment Variables



Create a .env file in the project root.



Use .env.example as a template:



GEMINI\_API\_KEY=your\_gemini\_api\_key\_here



ACCESS\_TOKEN=your\_whatsapp\_access\_token\_here

PHONE\_NUMBER\_ID=your\_whatsapp\_phone\_number\_id\_here



WHATSAPP\_VERIFY\_TOKEN=your\_webhook\_verify\_token\_here



Never commit .env to GitHub.



▶️ Running the Application



Start the FastAPI server:



uvicorn app:app --reload



The application will run on:



http://127.0.0.1:8000



For local WhatsApp webhook development, expose the server using ngrok:



ngrok http 8000



Configure the Meta webhook endpoint as:



https://YOUR-NGROK-URL/webhook

🧠 Memory System



JARVIS currently uses two types of memory.



Conversation Memory



The assistant retrieves recent messages from the database and provides them to Gemini as context.



Example:



User: My favorite language is Python.

Assistant: Nice! Python is a great choice.



User: What is my favorite language?



Assistant: Your favorite language is Python.

Long-Term Memory



JARVIS uses Gemini to identify useful information that should persist across conversations.



For example:



User: I am learning FastAPI.



The memory system can store:



User is learning FastAPI.



Temporary questions and casual messages are not stored as long-term memories.



🔒 Security



Sensitive credentials are stored using environment variables.



The following files are intentionally excluded from Git:



.env

.venv/

\_\_pycache\_\_/

\*.pyc

chatbot.db

chatbot\_backup.db



Never commit:



API keys

Access tokens

Passwords

Webhook secrets

Database files containing private user data

🗺️ Roadmap



Planned improvements:



&#x20;Smarter memory management

&#x20;Memory updates and deletion

&#x20;Duplicate memory detection

&#x20;Tool calling

&#x20;Web search tools

&#x20;RAG-based knowledge retrieval

&#x20;Document processing

&#x20;AI agent workflows

&#x20;Production database

&#x20;Production deployment

&#x20;Authentication and rate limiting

&#x20;Improved observability

&#x20;Modular plugin architecture

📌 Project Status



JARVIS is an actively developed AI assistant project.



The current version focuses on WhatsApp communication, Gemini-powered responses, conversation memory, and long-term user memory.



Future versions will expand JARVIS into a more capable AI agent with tools, retrieval, and autonomous workflows.



👨‍💻 Author



Parnay Rao



GitHub: https://github.com/theparnay1-ai



LinkedIn: https://www.linkedin.com/in/parnay-rao

