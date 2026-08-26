import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools.registry import TOOLS


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def calculator_tool(expression: str):
    return TOOLS["calculate"](expression)


def main():

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents="What is 847 multiplied by 392?",
        config=types.GenerateContentConfig(
            tools=[
                calculator_tool
            ]
        )
    )

    print(response.text)


if __name__ == "__main__":
    main()