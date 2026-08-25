import os
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup


EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"


def extract_emails_from_text(text):
    """
    Extract email addresses from publicly available text.
    """

    if not text:
        return []

    return list(
        dict.fromkeys(
            re.findall(
                EMAIL_PATTERN,
                text
            )
        )
    )


def get_public_page_text(url):
    """
    Fetch publicly accessible webpage text.
    """

    try:

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; "
                    "InfluencerResearchBot/1.0)"
                )
            }
        )

        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove scripts/styles
        for tag in soup(
            ["script", "style"]
        ):
            tag.decompose()

        return soup.get_text(
            " ",
            strip=True
        )

    except Exception as e:

        print(
            f"Could not fetch {url}: {e}"
        )

        return ""


def find_contact_email(influencer):
    """
    Find publicly available contact email.

    Currently checks text already available
    in the influencer record.

    Never generates or guesses an email.
    """

    # --------------------------------
    # Check existing text fields
    # --------------------------------

    text_fields = [
        influencer.get(
            "description",
            ""
        ),
        influencer.get(
            "recent_video_descriptions",
            ""
        )
    ]

    for text in text_fields:

        emails = extract_emails_from_text(
            str(text)
        )

        if emails:

            return emails[0]

    # --------------------------------
    # Check website if available
    # --------------------------------

    website = influencer.get(
        "website",
        ""
    )

    if website and website != "Not Found":

        page_text = get_public_page_text(
            website
        )

        emails = extract_emails_from_text(
            page_text
        )

        if emails:

            return emails[0]

    # --------------------------------
    # Nothing found
    # --------------------------------

    return "Not Found"


def enrich_emails(df):

    results = []

    total = len(df)

    for index, (_, influencer) in enumerate(
        df.iterrows(),
        start=1
    ):

        print(
            f"Checking email "
            f"{index}/{total}: "
            f"{influencer['name']}"
        )

        try:

            email = find_contact_email(
                influencer
            )

        except Exception as e:

            print(
                f"Email lookup failed: {e}"
            )

            email = "Not Found"

        influencer["contact_email"] = email

        results.append(
            influencer
        )

    return pd.DataFrame(results)


if __name__ == "__main__":

    input_file = (
        "data/enriched_influencers.csv"
    )

    output_file = (
        "data/enriched_influencers.csv"
    )

    if not os.path.exists(
        input_file
    ):

        raise FileNotFoundError(
            f"{input_file} not found. "
            "Run enrichment.py first."
        )

    df = pd.read_csv(
        input_file
    )

    print(
        f"Loaded {len(df)} influencers."
    )

    enriched_df = enrich_emails(
        df
    )

    enriched_df.to_csv(
        output_file,
        index=False
    )

    print(
        "\nEmail enrichment complete."
    )

    print(
        f"Saved to {output_file}"
    )

    print(
        "\nEmail results:"
    )

    print(
        enriched_df[
            [
                "name",
                "contact_email"
            ]
        ].to_string(
            index=False
        )
    )