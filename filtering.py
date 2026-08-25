import os
import pandas as pd


def filter_influencers(
    df,
    niche,
    niche_data
):
    """
    Filter discovered influencers and save
    the filtering results to CSV.
    """

    # -----------------------------
    # Get LLM-generated terms
    # -----------------------------

    keywords = niche_data.get(
        "keywords",
        []
    )

    topics = niche_data.get(
        "topics",
        []
    )

    relevance_terms = [
        str(term).lower().strip()
        for term in keywords + topics
        if str(term).strip()
    ]

    # -----------------------------
    # Organization indicators
    # -----------------------------

    organization_keywords = [
        "university",
        "college",
        "institute",
        "corporation",
        "organization",
        "company",
        "school"
    ]

    results = []

    # -----------------------------
    # Filter each influencer
    # -----------------------------

    for _, influencer in df.iterrows():

        name = str(
            influencer.get(
                "name",
                ""
            )
        ).lower()

        description = str(
            influencer.get(
                "description",
                ""
            )
        ).lower()

        text = f"{name} {description}"

        followers = int(
            influencer.get(
                "followers",
                0
            )
        )

        # -------------------------
        # 1. Follower check
        # -------------------------

        if not 5000 <= followers <= 100000:

            status = "Rejected"

            reason = (
                "Follower count outside "
                "the 5K–100K range."
            )

        # -------------------------
        # 2. Organization check
        # -------------------------

        elif any(
            word in text
            for word in organization_keywords
        ):

            status = "Rejected"

            reason = (
                "Organization or institution "
                "rather than an individual creator."
            )

        # -------------------------
        # 3. Niche relevance
        # -------------------------

        else:

            matched_terms = [
                term
                for term in relevance_terms
                if term in text
            ]

            if matched_terms:

                status = "Qualified"

                reason = (
                    f"Content is relevant "
                    f"to the {niche} niche."
                )

            else:

                status = "Rejected"

                reason = (
                    f"Content is not sufficiently "
                    f"relevant to the {niche} niche."
                )

        # Add filtering information

        influencer["status"] = status

        influencer["filter_reason"] = reason

        results.append(
            influencer
        )

    # -----------------------------
    # Create final DataFrame
    # -----------------------------

    filtered_df = pd.DataFrame(
        results
    )

    # -----------------------------
    # Save filtered dataset
    # -----------------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    output_path = (
        "data/filtered_influencers.csv"
    )

    filtered_df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nFiltered dataset saved to: "
        f"{output_path}"
    )

    return filtered_df