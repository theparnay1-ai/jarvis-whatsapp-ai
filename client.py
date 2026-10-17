import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def should_reply(message):
    return bool(message and message.strip())


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
You are a memory extraction system for a multi-customer
WhatsApp business AI agent.

Analyze the customer's message and extract only useful,
explicitly stated information about THAT CUSTOMER.

IMPORTANT RULES:
- The customer is the person who sent the message.
- Never assume the customer's name or identity.
- Never use the business owner's name as the customer's name.
- Never invent personal details.
- Do not infer a name from phrases such as:
  "I am interested", "I am looking", or "I want a chatbot".
- Only record a customer's name when they explicitly introduce
  themselves, for example: "My name is Rahul."
- Only record preferences, goals, or requirements that the
  customer actually states.
- Do not convert a business enquiry into a personal fact.
- Do not save information about the AI assistant's owner.
- Do not save information that is not useful for future
  conversations with this same customer.

Examples:

Customer message:
"I am interested in getting a WhatsApp chatbot for my business."

Output:
NONE

Customer message:
"My name is Rahul. I own a clothing store."

Output:
The customer introduced himself as Rahul and owns a clothing store.

Customer message:
"I want to automate customer enquiries for my restaurant."

Output:
The customer wants to automate customer enquiries for their restaurant.

Customer message:
"How much does your service cost?"

Output:
NONE

Return NONE if the message contains no useful, explicitly
stated information about the customer.

Return ONLY NONE or one concise sentence describing the memory.

Customer message:
{message}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-3.5-flash-lite",
            contents=prompt
        )

        if not response.text:
            return None

        result = response.text.strip()

        if result.upper() == "NONE":
            return None

        return result

    except Exception as e:
        print(
            f"Memory extraction failed: "
            f"{type(e).__name__}: {e}"
        )
        return None