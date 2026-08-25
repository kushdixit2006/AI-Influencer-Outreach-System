import os
from datetime import datetime
import pandas as pd


def is_valid_email(email):
    """
    Check whether an email is available.
    """

    if pd.isna(email):
        return False

    email = str(email).strip()

    if not email:
        return False

    if email.lower() == "not found":
        return False

    return "@" in email and "." in email


def send_email_simulated(
    influencer
):
    """
    Simulate sending an email.

    No real email is sent.
    """

    print(
        f"\n[SIMULATED EMAIL]"
    )

    print(
        f"To: {influencer['contact_email']}"
    )

    print(
        f"Creator: {influencer['name']}"
    )

    print(
        f"Subject: Collaboration Opportunity"
    )

    print(
        f"\n{influencer['email_pitch']}"
    )

    return True


def process_outreach(df):
    """
    Process personalized outreach.

    Rules:
    - Only Qualified influencers
    - Must have a valid email
    - Prevent duplicate outreach
    - Instagram DM remains manual
    """

    results = []

    for _, influencer in df.iterrows():

        influencer = influencer.copy()

        # --------------------------------
        # Check qualification
        # --------------------------------

        if influencer.get(
            "status"
        ) != "Qualified":

            influencer[
                "sent"
            ] = "No"

            influencer[
                "outreach_status"
            ] = "Not Qualified"

            influencer[
                "send_date"
            ] = ""

            results.append(
                influencer
            )

            continue

        # --------------------------------
        # Check email
        # --------------------------------

        email = influencer.get(
            "contact_email",
            "Not Found"
        )

        if not is_valid_email(email):

            influencer[
                "sent"
            ] = "No"

            influencer[
                "outreach_status"
            ] = "No Email"

            influencer[
                "send_date"
            ] = ""

            results.append(
                influencer
            )

            continue

        # --------------------------------
        # Duplicate protection
        # --------------------------------

        already_sent = str(
            influencer.get(
                "sent",
                "No"
            )
        ).lower()

        if already_sent == "yes":

            influencer[
                "outreach_status"
            ] = "Already Sent"

            results.append(
                influencer
            )

            continue

        # --------------------------------
        # Simulate email
        # --------------------------------

        success = send_email_simulated(
            influencer
        )

        if success:

            influencer[
                "sent"
            ] = "Yes"

            influencer[
                "send_date"
            ] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            influencer[
                "outreach_status"
            ] = "Sent (Simulated)"

        else:

            influencer[
                "sent"
            ] = "No"

            influencer[
                "send_date"
            ] = ""

            influencer[
                "outreach_status"
            ] = "Failed"

        # --------------------------------
        # Instagram DM
        # --------------------------------

        influencer[
            "instagram_dm_status"
        ] = "Manual / Simulated"

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
        "data/outreach.csv"
    )

    output_file = (
        "data/outreach_tracker.csv"
    )

    # --------------------------------------
    # Load personalized outreach
    # --------------------------------------

    if not os.path.exists(
        input_file
    ):

        raise FileNotFoundError(
            f"{input_file} not found. "
            "Run personalization.py first."
        )

    df = pd.read_csv(
        input_file
    )

    print(
        f"Loaded {len(df)} "
        f"outreach records."
    )

    # --------------------------------------
    # Process outreach
    # --------------------------------------

    tracker_df = process_outreach(
        df
    )

    # --------------------------------------
    # Save tracker
    # --------------------------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    tracker_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nOutreach tracker saved to:"
        f"\n{output_file}"
    )

    # --------------------------------------
    # Statistics
    # --------------------------------------

    sent = len(
        tracker_df[
            tracker_df["sent"] == "Yes"
        ]
    )

    no_email = len(
        tracker_df[
            tracker_df[
                "outreach_status"
            ] == "No Email"
        ]
    )

    print(
        "\n=============================="
    )

    print(
        "OUTREACH RESULTS"
    )

    print(
        "=============================="
    )

    print(
        f"Total records : "
        f"{len(tracker_df)}"
    )

    print(
        f"Simulated sent: "
        f"{sent}"
    )

    print(
        f"No email      : "
        f"{no_email}"
    )

    print(
        "\nInstagram DMs:"
    )

    print(
        "Manual / Simulated"
    )