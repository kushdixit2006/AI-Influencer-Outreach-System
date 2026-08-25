import os
import pandas as pd
import streamlit as st

from llm_keyword import generate_keywords
from filtering import filter_influencers
from enrichment import enrich_influencers
from email_enrichment import enrich_emails
from personalization import personalize_influencers
from sending import process_outreach


# ==========================================
# Streamlit Configuration
# ==========================================

st.set_page_config(
    page_title="AI Influencer Outreach System",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 AI Influencer Outreach System")

st.write(
    "Discover, qualify, enrich and personalize "
    "micro-influencer outreach using AI."
)


# ==========================================
# Load Demo Dataset
# ==========================================

def load_demo_influencers():
    """
    Load previously discovered real influencers.

    This dataset is used for the public demo so
    the application can continue working when
    the YouTube API quota is unavailable.
    """

    demo_file = (
        "data/discovered_influencers.csv"
    )

    if not os.path.exists(demo_file):
        return None

    try:

        return pd.read_csv(
            demo_file
        )

    except Exception as e:

        st.error(
            f"Could not load influencer dataset: {e}"
        )

        return None


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
# AI Keyword Generation + Discovery
# ==========================================

st.header("1️⃣ Influencer Discovery & Filtering")

if st.button(
    "🔎 Find Influencers",
    type="primary"
):

    if not niche.strip():

        st.warning(
            "Please enter a niche first."
        )

        st.stop()

    st.session_state.niche = (
        niche.strip()
    )

    # --------------------------------------
    # Generate niche keywords using Groq
    # --------------------------------------

    with st.spinner(
        "Understanding the niche with AI..."
    ):

        try:

            niche_data = generate_keywords(
                niche.strip()
            )

        except Exception as e:

            st.error(
                f"AI keyword generation failed: {e}"
            )

            st.stop()

    st.session_state.niche_data = (
        niche_data
    )

    # --------------------------------------
    # Display generated keywords
    # --------------------------------------

    keywords = niche_data.get(
        "keywords",
        []
    )

    topics = niche_data.get(
        "topics",
        []
    )

    with st.expander(
        "View AI-generated niche information"
    ):

        st.write(
            "**Keywords:**"
        )

        st.write(
            ", ".join(
                keywords
            )
        )

        st.write(
            "**Topics:**"
        )

        st.write(
            ", ".join(
                topics
            )
        )

    # --------------------------------------
    # Load real discovered creators
    # --------------------------------------

    with st.spinner(
        "Loading discovered influencers..."
    ):

        influencers_df = (
            load_demo_influencers()
        )

    if influencers_df is None:

        st.error(
            "The discovered influencer dataset "
            "could not be found."
        )

        st.stop()

    # --------------------------------------
    # Update niche
    # --------------------------------------

    influencers_df["niche"] = (
        niche.strip()
    )

    # --------------------------------------
    # Store discovered data
    # --------------------------------------

    st.session_state.influencers_df = (
        influencers_df
    )

    # --------------------------------------
    # Filtering
    # --------------------------------------

    with st.spinner(
        "Filtering creators according to "
        "the selected niche..."
    ):

        try:

            filtered_df = filter_influencers(
                influencers_df,
                niche.strip(),
                niche_data
            )

        except Exception as e:

            st.error(
                f"Filtering failed: {e}"
            )

            st.stop()

    st.session_state.filtered_df = (
        filtered_df
    )

    # --------------------------------------
    # Save filtering results
    # --------------------------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    filtered_df.to_csv(
        "data/filtered_influencers.csv",
        index=False
    )

    st.success(
        f"Discovery and filtering complete! "
        f"{len(influencers_df)} creators processed."
    )


# ==========================================
# Display Discovery Results
# ==========================================

if (
    st.session_state.influencers_df
    is not None
    and st.session_state.filtered_df
    is not None
):

    discovered_df = (
        st.session_state.influencers_df
    )

    filtered_df = (
        st.session_state.filtered_df
    )

    qualified_count = len(
        filtered_df[
            filtered_df["status"]
            == "Qualified"
        ]
    )

    rejected_count = len(
        filtered_df[
            filtered_df["status"]
            == "Rejected"
        ]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Creators Available",
        len(discovered_df)
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
        "🔎 View Filtering Results"
    ):

        display_columns = [
            "name",
            "followers",
            "platform",
            "status",
            "filter_reason",
            "profile_url"
        ]

        available_columns = [
            column
            for column in display_columns
            if column in filtered_df.columns
        ]

        st.dataframe(
            filtered_df[
                available_columns
            ],
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# STEP 2
# Profile Enrichment
# ==========================================

st.header("2️⃣ Profile Enrichment")

if (
    st.session_state.filtered_df
    is not None
):

    if st.button(
        "✨ Enrich Qualified Influencers"
    ):

        with st.spinner(
            "Collecting profile metrics "
            "and recent content..."
        ):

            try:

                enriched_df = (
                    enrich_influencers(
                        st.session_state.filtered_df
                    )
                )

            except Exception as e:

                st.error(
                    f"Profile enrichment failed: {e}"
                )

                st.stop()

        # ----------------------------------
        # Email enrichment
        # ----------------------------------

        with st.spinner(
            "Checking publicly available "
            "contact information..."
        ):

            try:

                enriched_df = enrich_emails(
                    enriched_df
                )

            except Exception as e:

                st.warning(
                    f"Email enrichment encountered "
                    f"an issue: {e}"
                )

                enriched_df[
                    "contact_email"
                ] = "Not Found"

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
        "📊 View Enriched Influencers"
    ):

        display_columns = [
            "name",
            "followers",
            "average_views",
            "engagement_rate",
            "content_themes",
            "contact_email"
        ]

        available_columns = [
            column
            for column in display_columns
            if column in enriched_df.columns
        ]

        st.dataframe(
            enriched_df[
                available_columns
            ],
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# STEP 3
# AI Personalization
# ==========================================

st.header("3️⃣ AI Personalization")

if (
    st.session_state.enriched_df
    is not None
):

    if st.button(
        "💬 Generate Personalized Outreach"
    ):

        with st.spinner(
            "Generating personalized "
            "emails and Instagram DMs..."
        ):

            try:

                outreach_df = (
                    personalize_influencers(
                        st.session_state.enriched_df
                    )
                )

            except Exception as e:

                st.error(
                    f"Personalization failed: {e}"
                )

                st.stop()

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
        "✍️ Personalized Outreach"
    )

    for _, row in outreach_df.iterrows():

        creator_name = row.get(
            "name",
            "Creator"
        )

        with st.expander(
            f"📩 {creator_name}"
        ):

            email = row.get(
                "contact_email",
                "Not Found"
            )

            st.write(
                f"**Email:** {email}"
            )

            st.write(
                "**Email Pitch**"
            )

            st.info(
                row.get(
                    "email_pitch",
                    "Not Generated"
                )
            )

            st.write(
                "**Instagram DM**"
            )

            st.info(
                row.get(
                    "instagram_dm",
                    "Not Generated"
                )
            )


# ==========================================
# STEP 4
# Sending Simulation
# ==========================================

st.header(
    "4️⃣ Sending & Outreach Tracking"
)

if (
    st.session_state.outreach_df
    is not None
):

    st.warning(
        "Demo Mode: Email sending is simulated. "
        "No real emails will be sent."
    )

    if st.button(
        "📧 Simulate Outreach"
    ):

        with st.spinner(
            "Processing outreach..."
        ):

            try:

                tracker_df = (
                    process_outreach(
                        st.session_state.outreach_df
                    )
                )

            except Exception as e:

                st.error(
                    f"Outreach processing failed: {e}"
                )

                st.stop()

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

    sent_count = len(
        tracker_df[
            tracker_df["sent"]
            == "Yes"
        ]
    )

    no_email_count = len(
        tracker_df[
            tracker_df[
                "outreach_status"
            ]
            == "No Email"
        ]
    )

    total_count = len(
        tracker_df
    )

    col1, col2, col3 = st.columns(3)

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
        total_count
    )

    display_columns = [
        "name",
        "contact_email",
        "message_generated",
        "sent",
        "send_date",
        "outreach_status"
    ]

    available_columns = [
        column
        for column in display_columns
        if column in tracker_df.columns
    ]

    st.dataframe(
        tracker_df[
            available_columns
        ],
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
    "AI Influencer Outreach System • "
    "Groq + LangChain + YouTube Data + Streamlit"
)