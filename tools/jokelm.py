import json
from os import environ

from registry import register_tool


def generate_jokes(client, topic: str) -> dict:
    """Fetches jokes as a raw JSON string and parses it with Python's built-in json module."""

    # Lazy import: Only loaded when a joke is actively being generated
    from google.genai import types

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        # Explicitly instruct the model on the exact JSON shape since we removed Pydantic
        contents=f"Give me 3 funny jokes about {topic} with answers. "
        f"Respond ONLY with a JSON object containing a 'jokes' key. "
        f"The value must be a list of objects with 'joke' and 'answer' keys.",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            response_mime_type="application/json",
        ),
    )

    # Parse the text response into a standard Python dictionary
    return json.loads(response.text)


@register_tool(name="jokelm", help_text="A tool for coming up with jokes on a specific topic.")
def jokes(topic: str) -> list[str]:
    """Takes a topic string and returns a flat list alternating between jokes and answers for LCD slides."""

    # --- LAZY IMPORTS ---
    # These execute only when the tool is called, keeping your app startup fast!
    from dotenv import load_dotenv
    from google import genai

    # Load environment variables
    load_dotenv()

    # Initialize the client
    client = genai.Client(api_key=environ.get("GEMINI_API_KEY"))

    # Pass the client and topic to the generation function
    jokes_data = generate_jokes(client=client, topic=topic)

    # Converts the jokes and answers to a flat list of slides for the LCD
    slides = []

    # Access the list of dictionaries safely
    for item in jokes_data.get("jokes", []):
        slides.append(item.get("joke", ""))
        slides.append(item.get("answer", ""))

    return slides


if __name__ == '__main__':
    # Test the execution
    print(jokes('tigers'))
