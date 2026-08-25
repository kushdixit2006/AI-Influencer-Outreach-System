import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_keywords(niche):

    prompt = f"""
You are an influencer discovery assistant.

Target niche:
{niche}

Generate search terms that can be used to find
YouTube creators in this niche.

Return ONLY valid JSON in this exact format:

{{
    "keywords": [
        "keyword 1",
        "keyword 2",
        "keyword 3"
    ],
    "topics": [
        "topic 1",
        "topic 2",
        "topic 3"
    ]
}}

Requirements:
- Generate 10 keywords.
- Generate 10 content topics.
- All terms must be strongly related to the given niche.
- Do not include unrelated niches.
- Do not provide explanations.
"""

    response = llm.invoke(prompt)

    result = response.content

    try:
        return json.loads(result)

    except json.JSONDecodeError:

        # Handle accidental markdown/text from the LLM
        start = result.find("{")
        end = result.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError(
                "LLM did not return valid JSON"
            )

        return json.loads(
            result[start:end]
        )




