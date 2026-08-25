import os
import json
import pandas as pd

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# ==========================================
# Configuration
# ==========================================

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    api_key=os.getenv("GROQ_API_KEY")
)


# ==========================================
# Generate personalized messages
# ==========================================

def generate_messages(influencer):

    name = influencer.get(
        "name",
        ""
    )

    niche = influencer.get(
        "niche",
        ""
    )

    followers = influencer.get(
        "followers",
        ""
    )

    engagement_rate = influencer.get(
        "engagement_rate",
        ""
    )

    content_themes = influencer.get(
        "content_themes",
        ""
    )

    creator_brief = influencer.get(
        "creator_brief",
        ""
    )

    recent_videos = influencer.get(
        "recent_video_titles",
        ""
    )

    prompt = f"""
You are an influencer marketing specialist.

Create personalized outreach messages for this creator.

Creator:
{name}

Niche:
{niche}

Followers:
{followers}

Engagement rate:
{engagement_rate}%

Content themes:
{content_themes}

Creator brief:
{creator_brief}

Recent videos:
{recent_videos}

Generate TWO messages.

1. EMAIL

Requirements:
- 60–90 words.
- Address the creator by name.
- Mention their actual content/niche.
- Reference a relevant content theme or recent video.
- Propose a realistic collaboration.
- Explain the value of the collaboration.
- Sound natural and professional.
- Do not make unsupported claims.
- Do not use generic filler.

2. INSTAGRAM DM

Requirements:
- 15–30 words.
- Address the creator by name.
- Mention their content/niche.
- Keep it conversational.
- Clearly indicate collaboration interest.
- Do not sound like spam.

Return ONLY valid JSON:

{{
    "email": "...",
    "instagram_dm": "..."
}}
"""

    response = llm.invoke(
        prompt
    )

    result = response.content.strip()

    try:

        data = json.loads(
            result
        )

    except json.JSONDecodeError:

        result = result.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        data = json.loads(
            result
        )

    return data


# ==========================================
# Personalize all influencers
# ==========================================

def personalize_influencers(df):

    qualified_df = df[
        df["status"] == "Qualified"
    ].copy()

    print(
        f"Qualified influencers: "
        f"{len(qualified_df)}"
    )

    results = []

    total = len(
        qualified_df
    )

    for index, (_, influencer) in enumerate(
        qualified_df.iterrows(),
        start=1
    ):

        print(
            f"Generating messages "
            f"{index}/{total}: "
            f"{influencer['name']}"
        )

        try:

            messages = generate_messages(
                influencer
            )

            influencer[
                "email_pitch"
            ] = messages.get(
                "email",
                ""
            )

            influencer[
                "instagram_dm"
            ] = messages.get(
                "instagram_dm",
                ""
            )

            influencer[
                "message_generated"
            ] = "Yes"

        except Exception as e:

            print(
                f"Failed for "
                f"{influencer['name']}: {e}"
            )

            influencer[
                "email_pitch"
            ] = "Not Generated"

            influencer[
                "instagram_dm"
            ] = "Not Generated"

            influencer[
                "message_generated"
            ] = "No"

        # Sending status
        influencer[
            "sent"
        ] = "No"

        influencer[
            "send_date"
        ] = ""

        influencer[
            "outreach_status"
        ] = "Not Sent"

        results.append(
            influencer
        )

    return pd.DataFrame(
        results
    )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    input_file = (
        "data/enriched_influencers.csv"
    )

    output_file = (
        "data/outreach.csv"
    )

    if not os.path.exists(
        input_file
    ):

        raise FileNotFoundError(
            f"{input_file} not found. "
            "Run enrichment first."
        )

    # --------------------------------------
    # Load enriched data
    # --------------------------------------

    df = pd.read_csv(
        input_file
    )

    print(
        f"Loaded {len(df)} influencers."
    )

    # --------------------------------------
    # Generate messages
    # --------------------------------------

    outreach_df = (
        personalize_influencers(
            df
        )
    )

    # --------------------------------------
    # Save
    # --------------------------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    outreach_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nOutreach dataset saved to:"
        f"\n{output_file}"
    )

    # --------------------------------------
    # Display samples
    # --------------------------------------

    print(
        "\n=============================="
    )

    print(
        "PERSONALIZATION COMPLETE"
    )

    print(
        "=============================="
    )

    for _, row in outreach_df.head(3).iterrows():

        print(
            f"\nCreator: {row['name']}"
        )

        print(
            "\nEMAIL:"
        )

        print(
            row["email_pitch"]
        )

        print(
            "\nINSTAGRAM DM:"
        )

        print(
            row["instagram_dm"]
        )

        print(
            "\n------------------------------"
        )