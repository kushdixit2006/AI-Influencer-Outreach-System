import os
import pandas as pd
import streamlit as st

from llm_keyword import generate_keywords
from discovery import discover_influencers
from filtering import filter_influencers
from enrichment import enrich_influencers
from email_enrichment import enrich_emails
from personalization import personalize_influencers
from sending import process_outreach


# ==========================================
# Streamlit Configuration
# ==========================================

st.set_page_config(
    page_title="AI Influencer Outreach",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 AI Influencer Outreach System")

st.write(
    "Discover, qualify, enrich and personalize "
    "micro-influencer outreach."
)


# ==========================================
# Session State
# ==========================================

if "niche" not in st.session_state:
    st.session_state.niche = ""

if "niche_data" not in st.session_state:
    st.session_state.niche_data = None

if "influencers_df" not in st.session_state:
    st.session_state.influencers_df = None

if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None

if "enriched_df" not in st.session_state:
    st.session_state.enriched_df = None

if "outreach_df" not in st.session_state:
    st.session_state.outreach_df = None

if "tracker_df" not in st.session_state:
    st.session_state.tracker_df = None


# ==========================================
# Niche Input
# ==========================================

niche = st.text_input(
    "Enter influencer niche",
    value=st.session_state.niche,
    placeholder="Technology, Fitness, Beauty..."
)


# ==========================================
# STEP 1
# Discovery + Filtering
# ==========================================

st.header("1️⃣ Discovery & Filtering")

if st.button(
    "🔎 Find Influencers",
    type="primary"
):

    if not niche.strip():

        st.warning(
            "Please enter a niche first."
        )

        st.stop()

    st.session_state.niche = niche.strip()

    # --------------------------------------
    # Generate keywords
    # --------------------------------------

    with st.spinner(
        "Understanding the niche with AI..."
    ):

        niche_data = generate_keywords(
            niche.strip()
        )

    st.session_state.niche_data = niche_data

    # --------------------------------------
    # Search queries
    # --------------------------------------

    search_queries = (
        niche_data["keywords"]
        + niche_data["topics"]
    )

    search_queries = list(
        dict.fromkeys(
            search_queries
        )
    )

    # --------------------------------------
    # Discovery
    # --------------------------------------

    with st.spinner(
        "Discovering YouTube creators..."
    ):

        influencers = discover_influencers(
            niche=niche.strip(),
            search_queries=search_queries
        )

    if not influencers:

        st.error(
            "No micro-influencers found."
        )

        st.stop()

    influencers_df = pd.DataFrame(
        influencers
    )

    st.session_state.influencers_df = (
        influencers_df
    )

    # --------------------------------------
    # Save discovery data
    # --------------------------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    influencers_df.to_csv(
        "data/influencers.csv",
        index=False
    )

    # --------------------------------------
    # Filtering
    # --------------------------------------

    with st.spinner(
        "Filtering creators..."
    ):

        filtered_df = filter_influencers(
            influencers_df,
            niche.strip(),
            niche_data
        )

    st.session_state.filtered_df = (
        filtered_df
    )

    st.success(
        "Discovery and filtering complete!"
    )


# ==========================================
# Display Discovery Results
# ==========================================

if (
    st.session_state.influencers_df
    is not None
):

    df = st.session_state.influencers_df

    qualified_df = (
        st.session_state.filtered_df
    )

    qualified_count = len(
        qualified_df[
            qualified_df["status"]
            == "Qualified"
        ]
    )

    rejected_count = len(
        qualified_df[
            qualified_df["status"]
            == "Rejected"
        ]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Discovered",
        len(df)
    )

    col2.metric(
        "Qualified",
        qualified_count
    )

    col3.metric(
        "Rejected",
        rejected_count
    )

    with st.expander(
        "View Filtering Results"
    ):

        st.dataframe(
            qualified_df[
                [
                    "name",
                    "followers",
                    "platform",
                    "status",
                    "filter_reason",
                    "profile_url"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# STEP 2
# Profile Enrichment
# ==========================================

st.header("2️⃣ Profile Enrichment")

if st.session_state.filtered_df is not None:

    if st.button(
        "✨ Enrich Qualified Influencers"
    ):

        with st.spinner(
            "Collecting profile metrics "
            "and recent content..."
        ):

            enriched_df = enrich_influencers(
                st.session_state.filtered_df
            )

        st.session_state.enriched_df = (
            enriched_df
        )

        # ----------------------------------
        # Email enrichment
        # ----------------------------------

        with st.spinner(
            "Checking publicly available "
            "contact information..."
        ):

            enriched_df = enrich_emails(
                enriched_df
            )

        st.session_state.enriched_df = (
            enriched_df
        )

        enriched_df.to_csv(
            "data/enriched_influencers.csv",
            index=False
        )

        st.success(
            "Profile enrichment complete!"
        )


# ==========================================
# Display Enrichment
# ==========================================

if (
    st.session_state.enriched_df
    is not None
):

    enriched_df = (
        st.session_state.enriched_df
    )

    with st.expander(
        "View Enriched Influencers"
    ):

        st.dataframe(
            enriched_df[
                [
                    "name",
                    "followers",
                    "engagement_rate",
                    "content_themes",
                    "contact_email"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# STEP 3
# AI Personalization
# ==========================================

st.header("3️⃣ AI Personalization")

if st.session_state.enriched_df is not None:

    if st.button(
        "💬 Generate Personalized Outreach"
    ):

        with st.spinner(
            "Generating personalized "
            "emails and Instagram DMs..."
        ):

            outreach_df = (
                personalize_influencers(
                    st.session_state.enriched_df
                )
            )

        st.session_state.outreach_df = (
            outreach_df
        )

        outreach_df.to_csv(
            "data/outreach.csv",
            index=False
        )

        st.success(
            "Personalized messages generated!"
        )


# ==========================================
# Display Personalized Messages
# ==========================================

if (
    st.session_state.outreach_df
    is not None
):

    outreach_df = (
        st.session_state.outreach_df
    )

    st.subheader(
        "Personalized Outreach"
    )

    for _, row in outreach_df.iterrows():

        with st.expander(
            f"📩 {row['name']}"
        ):

            st.write(
                f"**Email:** "
                f"{row['contact_email']}"
            )

            st.write(
                "**Email Pitch**"
            )

            st.info(
                row["email_pitch"]
            )

            st.write(
                "**Instagram DM**"
            )

            st.info(
                row["instagram_dm"]
            )


# ==========================================
# STEP 4
# Sending Simulation
# ==========================================

st.header("4️⃣ Sending & Outreach Tracking")

if st.session_state.outreach_df is not None:

    st.warning(
        "Email sending is currently "
        "SIMULATED. No real emails will be sent."
    )

    if st.button(
        "📧 Simulate Outreach"
    ):

        with st.spinner(
            "Processing outreach..."
        ):

            tracker_df = process_outreach(
                st.session_state.outreach_df
            )

        st.session_state.tracker_df = (
            tracker_df
        )

        tracker_df.to_csv(
            "data/outreach_tracker.csv",
            index=False
        )

        st.success(
            "Outreach simulation completed!"
        )


# ==========================================
# Outreach Tracker
# ==========================================

if (
    st.session_state.tracker_df
    is not None
):

    tracker_df = (
        st.session_state.tracker_df
    )

    st.subheader(
        "📊 Outreach Tracker"
    )

    col1, col2, col3 = st.columns(3)

    sent_count = len(
        tracker_df[
            tracker_df["sent"] == "Yes"
        ]
    )

    no_email_count = len(
        tracker_df[
            tracker_df[
                "outreach_status"
            ] == "No Email"
        ]
    )

    col1.metric(
        "Sent (Simulated)",
        sent_count
    )

    col2.metric(
        "No Email",
        no_email_count
    )

    col3.metric(
        "Total",
        len(tracker_df)
    )

    st.dataframe(
        tracker_df[
            [
                "name",
                "contact_email",
                "message_generated",
                "sent",
                "send_date",
                "outreach_status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )