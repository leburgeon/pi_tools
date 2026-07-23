from pydantic import BaseModel
from google import genai
from google.genai import types
from os import environ
from dotenv import load_dotenv

from registry import register_tool

# --- Define the desired output structure ---


class JokeItem(BaseModel):
    joke: str
    answer: str


class JokeList(BaseModel):
    jokes: list[JokeItem]


def generate_jokes(client: genai.Client, topic: str) -> JokeList:
    """Fetches a list of jokes from Gemini and returns a structured Python object."""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"Give me 3 funny jokes about {topic} with answers.",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            response_mime_type="application/json",
            response_schema=JokeList,
        ),
    )

    # Parse the complete JSON response into your Pydantic model
    return JokeList.model_validate_json(response.text)


@register_tool(name="jokelm", help_text="A tool for coming up with jokes on a specific topic.")
def jokes(topic: str) -> list[str]:
    """Takes a topic string and returns a flat list alternating between jokes and answers for LCD slides."""

    # Load environment variables
    load_dotenv()

    # Initialize the client
    client = genai.Client(api_key=environ.get("GEMINI_API_KEY"))

    # Pass the client and topic to the generation function
    jokes_data = generate_jokes(client=client, topic=topic)

    # Converts the jokes and answers to a flat list of slides for the LCD
    slides = []

    # Access the 'jokes' list inside the JokeList Pydantic object
    for item in jokes_data.jokes:
        slides.append(item.joke)
        slides.append(item.answer)

    return slides


if __name__ == '__main__':
    print(jokes('tigers'))
