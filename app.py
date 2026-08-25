import os
import pandas as pd
import streamlit as st

from llm_keyword import generate_keywords
from filtering import filter_influencers
from enrichment import enrich_influencers
from email_enrichment import enrich_emails
from personalization import personalize_influencers
from sending import process_outreach


# =========================================================
# STREAMLIT CONFIGURATION
# =========================================================

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


# =========================================================
# CONFIGURATION
# =========================================================

# The saved dataset contains Technology influencers.
# It is used when live YouTube discovery is unavailable.
DEFAULT_DEMO_NICHE = "Technology"

DEMO_DATASET = "data/discovered_influencers.csv"


# =========================================================
# LOAD SAVED INFLUENCERS
# =========================================================

def load_demo_influencers():
    """
    Load previously discovered real influencers.

    The dataset is used as a fallback because the
    current YouTube API quota is unavailable.
    """

    if not os.path.exists(DEMO_DATASET):
        return None

    try:
        df = pd.read_csv(DEMO_DATASET)

        return df

    except Exception as e:

        st.error(
            f"Could not load the influencer dataset: {e}"
        )

        return None


# =========================================================
# SESSION STATE
# =========================================================

if "niche" not in st.session_state:
    st.session_state.niche = ""

if "effective_niche" not in st.session_state:
    st.session_state.effective_niche = ""

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


# =========================================================
# NICHE INPUT
# =========================================================

user_niche = st.text_input(
    "Enter influencer niche",
    value=st.session_state.niche,
    placeholder="Technology, Education, Fitness, Beauty..."
)


# =========================================================
# DETERMINE EFFECTIVE NICHE
# =========================================================

effective_niche = user_niche.strip()


if effective_niche:

    # -----------------------------------------------------
    # Current demo is using the saved Technology dataset.
    # -----------------------------------------------------

    if effective_niche.lower() != DEFAULT_DEMO_NICHE.lower():

        st.warning(
            f"⚠️ **YouTube API quota limit has been exceeded.**\n\n"
            f"Live influencer discovery is temporarily "
            f"unavailable.\n\n"
            f"You entered **{effective_niche}**, but the "
            f"available fallback dataset contains "
            f"**{DEFAULT_DEMO_NICHE}** influencers.\n\n"
            f"The system will therefore continue using "
            f"**{DEFAULT_DEMO_NICHE}** as the effective niche."
        )

        effective_niche = DEFAULT_DEMO_NICHE

    else:

        st.info(
            "ℹ️ YouTube API quota limit has been exceeded. "
            "The system will continue using the available "
            "**Technology** influencer dataset."
        )


# Store the effective niche
if effective_niche:
    st.session_state.effective_niche = effective_niche


# =========================================================
# STEP 1
# DISCOVERY + FILTERING
# =========================================================

st.header("1️⃣ Influencer Discovery & Filtering")


if st.button(
    "🔎 Find Influencers",
    type="primary"
):

    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if not user_niche.strip():

        st.warning(
            "Please enter an influencer niche first."
        )

        st.stop()


    # -----------------------------------------------------
    # Store original user input
    # -----------------------------------------------------

    st.session_state.niche = user_niche.strip()


    # -----------------------------------------------------
    # Get effective niche
    # -----------------------------------------------------

    effective_niche = (
        st.session_state.effective_niche
    )

    if not effective_niche:

        effective_niche = DEFAULT_DEMO_NICHE

        st.session_state.effective_niche = (
            effective_niche
        )


    # -----------------------------------------------------
    # Show effective niche
    # -----------------------------------------------------

    st.write(
        f"**User niche:** {user_niche.strip()}"
    )

    st.write(
        f"**Processing niche:** {effective_niche}"
    )


    # =====================================================
    # AI KEYWORD GENERATION
    # =====================================================

    with st.spinner(
        f"Generating AI keywords for {effective_niche}..."
    ):

        try:

            niche_data = generate_keywords(
                effective_niche
            )

        except Exception as e:

            st.error(
                f"AI keyword generation failed: {e}"
            )

            st.stop()


    st.session_state.niche_data = niche_data


    # =====================================================
    # DISPLAY GENERATED KEYWORDS
    # =====================================================

    keywords = niche_data.get(
        "keywords",
        []
    )

    topics = niche_data.get(
        "topics",
        []
    )


    with st.expander(
        "🤖 View AI-generated niche information"
    ):

        st.write("### Keywords")

        if keywords:

            st.write(
                ", ".join(keywords)
            )

        else:

            st.write(
                "No keywords generated."
            )


        st.write("### Topics")

        if topics:

            st.write(
                ", ".join(topics)
            )

        else:

            st.write(
                "No topics generated."
            )


    # =====================================================
    # LOAD SAVED DATASET
    # =====================================================

    with st.spinner(
        "Loading previously discovered influencers..."
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


    # =====================================================
    # CHECK DATASET
    # =====================================================

    required_columns = [
        "channel_id",
        "name",
        "description",
        "profile_url",
        "followers",
        "platform"
    ]


    missing_columns = [
        column
        for column in required_columns
        if column not in influencers_df.columns
    ]


    if missing_columns:

        st.error(
            "The influencer dataset is missing "
            f"required columns: {missing_columns}"
        )

        st.stop()


    # =====================================================
    # USE EFFECTIVE NICHE
    # =====================================================

    influencers_df["niche"] = (
        effective_niche
    )


    # Store discovered influencers
    st.session_state.influencers_df = (
        influencers_df
    )


    # =====================================================
    # FILTERING
    # =====================================================

    with st.spinner(
        f"Filtering influencers for {effective_niche}..."
    ):

        try:

            filtered_df = filter_influencers(
                influencers_df,
                effective_niche,
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


    # =====================================================
    # SAVE FILTERED DATA
    # =====================================================

    os.makedirs(
        "data",
        exist_ok=True
    )


    filtered_df.to_csv(
        "data/filtered_influencers.csv",
        index=False
    )


    # =====================================================
    # SUCCESS MESSAGE
    # =====================================================

    st.success(
        f"Discovery and filtering complete! "
        f"{len(influencers_df)} creators processed."
    )


# =========================================================
# DISPLAY FILTERING RESULTS
# =========================================================

if (
    st.session_state.influencers_df is not None
    and
    st.session_state.filtered_df is not None
):

    discovered_df = (
        st.session_state.influencers_df
    )

    filtered_df = (
        st.session_state.filtered_df
    )


    # -----------------------------------------------------
    # Calculate qualified/rejected
    # -----------------------------------------------------

    if "status" in filtered_df.columns:

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

    else:

        qualified_count = 0
        rejected_count = 0


    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Display filtering results
    # -----------------------------------------------------

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


# =========================================================
# STEP 2
# PROFILE ENRICHMENT
# =========================================================

st.header("2️⃣ Profile Enrichment")


if (
    st.session_state.filtered_df is not None
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


        # =================================================
        # EMAIL ENRICHMENT
        # =================================================

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


        # Store
        st.session_state.enriched_df = (
            enriched_df
        )


        # Save
        enriched_df.to_csv(
            "data/enriched_influencers.csv",
            index=False
        )


        st.success(
            "Profile enrichment complete!"
        )


# =========================================================
# DISPLAY ENRICHMENT
# =========================================================

if (
    st.session_state.enriched_df is not None
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


# =========================================================
# STEP 3
# AI PERSONALIZATION
# =========================================================

st.header("3️⃣ AI Personalization")


if (
    st.session_state.enriched_df is not None
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


# =========================================================
# DISPLAY PERSONALIZED OUTREACH
# =========================================================

if (
    st.session_state.outreach_df is not None
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


# =========================================================
# STEP 4
# SENDING SIMULATION
# =========================================================

st.header(
    "4️⃣ Sending & Outreach Tracking"
)


if (
    st.session_state.outreach_df is not None
):

    st.warning(
        "🧪 Demo Mode: Email sending is simulated. "
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


# =========================================================
# OUTREACH TRACKER
# =========================================================

if (
    st.session_state.tracker_df is not None
):

    tracker_df = (
        st.session_state.tracker_df
    )


    st.subheader(
        "📊 Outreach Tracker"
    )


    # -----------------------------------------------------
    # Sent count
    # -----------------------------------------------------

    if "sent" in tracker_df.columns:

        sent_count = len(
            tracker_df[
                tracker_df["sent"]
                == "Yes"
            ]
        )

    else:

        sent_count = 0


    # -----------------------------------------------------
    # No email count
    # -----------------------------------------------------

    if "outreach_status" in tracker_df.columns:

        no_email_count = len(
            tracker_df[
                tracker_df[
                    "outreach_status"
                ]
                == "No Email"
            ]
        )

    else:

        no_email_count = 0


    total_count = len(
        tracker_df
    )


    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Tracker table
    # -----------------------------------------------------

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


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Influencer Outreach System • "
    "Groq + LangChain + YouTube Data API + Streamlit"
)