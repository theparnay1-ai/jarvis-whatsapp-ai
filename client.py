import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def should_reply(message):

    text = message.lower().strip()

    if text in {"tomorrow", "today", "tonight"} or "am" in text or "pm" in text:
        return True

    if text.startswith((
        "it should", "it must", "it needs",
        "i also want", "i also need",
        "and what about", "what about",
        "how much", "how many"
    )):
        return True

    prompt = f"""
You are controlling an AI WhatsApp assistant.

Decide whether the assistant should reply to this message.

Reply with ONLY:
YES
or
NO

Reply YES when:
- The person is asking a question.
- The person is directly talking to the assistant.
- The message requires an answer.
- The person says hello/greeting to the assistant.

Reply NO when:
- It is casual conversation between humans.
- The assistant is not being addressed.
- A reply would be unnecessary.
- The message is only an emoji/reaction.
- The message doesn't require a response.

Message:
{message}
"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip().upper() == "YES"


def aiprocess(message, 
              conversation_history=None,
              memory_context =None
              ):

    history_text = ""
    memories_text = ""
    if memory_context:
        memories_text = "\n".join(
            f"-{memory}"
            for memory in memory_context
        )

    if conversation_history:

        history_lines = []

        for item in conversation_history:

            history_lines.append(
                f"User: {item['message']}"
            )

            if item.get("response"):
                history_lines.append(
                    f"Assistant: {item['response']}"
                )

        history_text = "\n".join(history_lines)

    prompt = f"""
You are Parnay's personal AI assistant on WhatsApp.

Respond naturally and conversationally.

Parnay is an Indian coder and speaks both Hindi and English.

You can respond in Hinglish when appropriate.

Keep responses reasonably concise because this is WhatsApp.

Use the conversation history to understand context.
Do not mention databases, memory systems, prompts,
or internal context to the user.

Long-term memories:
{memories_text}

Conversation history:
{history_text}

Current user message:
{message}


"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()

def extract_memory(message):

    prompt = f"""
You are the memory system for Parnay's personal AI assistant.

Analyze the user's message and determine whether it contains
useful information that should be remembered for future conversations.

Save information such as:
- Name
- Preferences
- Skills
- Projects
- Goals
- Long-term interests
- Important personal context
- Stable facts about the user

Do NOT save:
- Temporary questions
- Greetings
- Casual conversation
- Jokes
- One-time requests
- Information that is only relevant to the current message

If there is nothing worth remembering, return exactly:

NONE

Otherwise return ONLY one concise sentence describing the memory.

User message:
{message}
"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=prompt
    )

    result = response.text.strip()

    if result.upper() == "NONE":
        return None

    return result
