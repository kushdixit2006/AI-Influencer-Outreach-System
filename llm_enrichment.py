import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_creator(
    influencer,
    niche
):
    """
    Analyze a creator's real YouTube content
    and generate content themes and a brief.
    """

    name = influencer.get(
        "name",
        ""
    )

    description = influencer.get(
        "description",
        ""
    )

    recent_titles = influencer.get(
        "recent_video_titles",
        ""
    )

    recent_descriptions = influencer.get(
        "recent_video_descriptions",
        ""
    )

    prompt = f"""
You are analyzing a YouTube micro-influencer
for a brand collaboration campaign.

Target niche:
{niche}

Creator name:
{name}

Channel description:
{description}

Recent video titles:
{recent_titles}

Recent video descriptions:
{recent_descriptions}

Based ONLY on the information provided above,
analyze this creator.

Return ONLY valid JSON:

{{
    "content_themes": [
        "theme 1",
        "theme 2",
        "theme 3"
    ],
    "creator_brief": "A concise 2-3 sentence summary of the creator's content, style, and likely audience."
}}

Requirements:

- Identify 3-5 genuine content themes.
- Do not invent information.
- Do not guess demographic information.
- Base the brief on the provided content.
"""

    response = llm.invoke(prompt)

    result = response.content.strip()

    try:

        return json.loads(result)

    except json.JSONDecodeError:

        # Remove accidental markdown
        result = result.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        return json.loads(result)