import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.6-flash")


def generate_outline(topic, purpose, audience):

    prompt = f"""
    Create a professional presentation outline.

    Topic: {topic}
    Purpose: {purpose}
    Audience: {audience}

    Return only slide titles.
    """

    response = model.generate_content(prompt)

    return response.text


def generate_all_slide_content(outline):

    outline_text = "\n".join(
        [f"{item['id']}. {item['title']}" for item in outline]
    )

    prompt = f"""
    Create presentation content.

    Slides:
    {outline_text}

    Return ONLY valid JSON.

    Format:

    {{
      "slides": [
        {{
          "id": 1,
          "title": "Slide Title",
          "content": [
            "Bullet 1",
            "Bullet 2",
            "Bullet 3",
            "Bullet 4"
          ]
        }}
      ]
    }}

    Requirements:
    - Create content for ALL slides
    - Exactly 4 bullet points per slide
    - Executive-level language
    - Return valid JSON only
    - No markdown
    - No explanation
    """

    response = model.generate_content(prompt)

    return response.text