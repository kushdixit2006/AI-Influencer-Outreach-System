import os
import pandas as pd

from dotenv import load_dotenv
from googleapiclient.discovery import build

from llm_enrichment import analyze_creator


# ==========================================
# Configuration
# ==========================================

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


# ==========================================
# Get Recent Videos
# ==========================================

def get_recent_videos(
    channel_id,
    max_results=10
):
    """
    Fetch recent videos from a YouTube channel.
    """

    response = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        type="video",
        order="date",
        maxResults=max_results
    ).execute()

    videos = []

    for item in response.get(
        "items",
        []
    ):

        video_id = item["id"]["videoId"]

        snippet = item.get(
            "snippet",
            {}
        )

        videos.append({
            "video_id": video_id,
            "title": snippet.get(
                "title",
                ""
            ),
            "description": snippet.get(
                "description",
                ""
            ),
            "published_at": snippet.get(
                "publishedAt",
                ""
            )
        })

    return videos


# ==========================================
# Get Video Statistics
# ==========================================

def get_video_statistics(
    video_ids
):
    """
    Fetch views, likes and comments
    for recent videos.
    """

    if not video_ids:
        return []

    statistics = []

    # YouTube API allows max 50 IDs
    # per request.
    for i in range(
        0,
        len(video_ids),
        50
    ):

        batch = video_ids[
            i:i + 50
        ]

        response = youtube.videos().list(
            part="statistics",
            id=",".join(batch)
        ).execute()

        for video in response.get(
            "items",
            []
        ):

            stats = video.get(
                "statistics",
                {}
            )

            views = int(
                stats.get(
                    "viewCount",
                    0
                )
            )

            likes = int(
                stats.get(
                    "likeCount",
                    0
                )
            )

            comments = int(
                stats.get(
                    "commentCount",
                    0
                )
            )

            statistics.append({
                "video_id": video["id"],
                "views": views,
                "likes": likes,
                "comments": comments
            })

    return statistics


# ==========================================
# Calculate Engagement
# ==========================================

def calculate_engagement(
    video_statistics
):
    """
    Calculate average engagement rate.

    Per-video engagement rate:

        (likes + comments) / views * 100

    Final engagement rate is the average
    across the analyzed videos.
    """

    if not video_statistics:

        return {
            "average_views": 0,
            "average_likes": 0,
            "average_comments": 0,
            "engagement_rate": 0
        }

    total_views = 0
    total_likes = 0
    total_comments = 0

    engagement_rates = []

    for video in video_statistics:

        views = video["views"]
        likes = video["likes"]
        comments = video["comments"]

        total_views += views
        total_likes += likes
        total_comments += comments

        if views > 0:

            rate = (
                (likes + comments)
                / views
            ) * 100

            engagement_rates.append(
                rate
            )

    count = len(
        video_statistics
    )

    average_views = (
        total_views / count
    )

    average_likes = (
        total_likes / count
    )

    average_comments = (
        total_comments / count
    )

    if engagement_rates:

        engagement_rate = (
            sum(engagement_rates)
            / len(engagement_rates)
        )

    else:

        engagement_rate = 0

    return {
        "average_views": round(
            average_views,
            2
        ),

        "average_likes": round(
            average_likes,
            2
        ),

        "average_comments": round(
            average_comments,
            2
        ),

        "engagement_rate": round(
            engagement_rate,
            2
        )
    }


# ==========================================
# Enrich One Influencer
# ==========================================

def enrich_influencer(
    influencer
):
    """
    Enrich one qualified influencer.
    """

    channel_id = influencer[
        "channel_id"
    ]

    niche = influencer.get(
        "niche",
        ""
    )

    # --------------------------------------
    # 1. Get recent videos
    # --------------------------------------

    videos = get_recent_videos(
        channel_id,
        max_results=10
    )

    # --------------------------------------
    # 2. Get video IDs
    # --------------------------------------

    video_ids = [
        video["video_id"]
        for video in videos
    ]

    # --------------------------------------
    # 3. Get statistics
    # --------------------------------------

    statistics = get_video_statistics(
        video_ids
    )

    # --------------------------------------
    # 4. Calculate engagement
    # --------------------------------------

    metrics = calculate_engagement(
        statistics
    )

    influencer[
        "average_views"
    ] = metrics[
        "average_views"
    ]

    influencer[
        "average_likes"
    ] = metrics[
        "average_likes"
    ]

    influencer[
        "average_comments"
    ] = metrics[
        "average_comments"
    ]

    influencer[
        "engagement_rate"
    ] = metrics[
        "engagement_rate"
    ]

    # --------------------------------------
    # 5. Store recent content
    # --------------------------------------

    recent_titles = [
        video["title"]
        for video in videos
    ]

    recent_descriptions = [
        video["description"]
        for video in videos
    ]

    influencer[
        "recent_video_titles"
    ] = " | ".join(
        recent_titles
    )

    influencer[
        "recent_video_descriptions"
    ] = " | ".join(
        recent_descriptions
    )

    # --------------------------------------
    # 6. AI Content Analysis
    # --------------------------------------

    try:

        ai_analysis = analyze_creator(
            influencer,
            niche
        )

        content_themes = (
            ai_analysis.get(
                "content_themes",
                []
            )
        )

        creator_brief = (
            ai_analysis.get(
                "creator_brief",
                ""
            )
        )

        influencer[
            "content_themes"
        ] = ", ".join(
            content_themes
        )

        influencer[
            "creator_brief"
        ] = creator_brief

    except Exception as e:

        print(
            f"AI analysis failed for "
            f"{influencer['name']}: {e}"
        )

        influencer[
            "content_themes"
        ] = "Not Available"

        influencer[
            "creator_brief"
        ] = "Not Available"

    # --------------------------------------
    # 7. Contact Email
    # --------------------------------------

    # We will implement public email
    # extraction separately.
    # Never guess an email.

    influencer[
        "contact_email"
    ] = "Not Found"

    return influencer


# ==========================================
# Enrich All Qualified Influencers
# ==========================================

def enrich_influencers(
    df
):
    """
    Enrich all qualified influencers.
    """

    qualified_df = df[
        df["status"] == "Qualified"
    ].copy()

    print(
        f"Qualified influencers: "
        f"{len(qualified_df)}"
    )

    enriched = []

    total = len(
        qualified_df
    )

    for index, (
        _,
        influencer
    ) in enumerate(
        qualified_df.iterrows(),
        start=1
    ):

        print(
            f"\nEnriching "
            f"{index}/{total}: "
            f"{influencer['name']}"
        )

        try:

            enriched_influencer = (
                enrich_influencer(
                    influencer
                )
            )

            enriched.append(
                enriched_influencer
            )

        except Exception as e:

            print(
                f"Error enriching "
                f"{influencer['name']}: {e}"
            )

            # Preserve the influencer even
            # if enrichment fails.

            influencer[
                "average_views"
            ] = 0

            influencer[
                "average_likes"
            ] = 0

            influencer[
                "average_comments"
            ] = 0

            influencer[
                "engagement_rate"
            ] = 0

            influencer[
                "recent_video_titles"
            ] = ""

            influencer[
                "recent_video_descriptions"
            ] = ""

            influencer[
                "content_themes"
            ] = "Not Available"

            influencer[
                "creator_brief"
            ] = "Not Available"

            influencer[
                "contact_email"
            ] = "Not Found"

            enriched.append(
                influencer
            )

    return pd.DataFrame(
        enriched
    )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    input_file = (
        "data/filtered_influencers.csv"
    )

    output_file = (
        "data/enriched_influencers.csv"
    )

    # --------------------------------------
    # Load filtered influencers
    # --------------------------------------

    if not os.path.exists(
        input_file
    ):

        raise FileNotFoundError(
            f"{input_file} not found. "
            "Run the filtering step first."
        )

    df = pd.read_csv(
        input_file
    )

    print(
        f"Loaded {len(df)} filtered "
        f"influencers."
    )

    # --------------------------------------
    # Check qualified creators
    # --------------------------------------

    qualified_count = len(
        df[
            df["status"] == "Qualified"
        ]
    )

    print(
        f"Qualified creators to enrich: "
        f"{qualified_count}"
    )

    if qualified_count == 0:

        print(
            "No qualified influencers "
            "available for enrichment."
        )

        exit()

    # --------------------------------------
    # Enrichment
    # --------------------------------------

    enriched_df = enrich_influencers(
        df
    )

    # --------------------------------------
    # Save
    # --------------------------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    enriched_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nEnriched dataset saved to:"
        f"\n{output_file}"
    )

    # --------------------------------------
    # Display results
    # --------------------------------------

    print(
        "\n=============================="
    )

    print(
        "ENRICHMENT RESULTS"
    )

    print(
        "=============================="
    )

    if not enriched_df.empty:

        columns = [
            "name",
            "followers",
            "average_views",
            "average_likes",
            "average_comments",
            "engagement_rate",
            "content_themes",
            "contact_email"
        ]

        print(
            enriched_df[
                columns
            ].to_string(
                index=False
            )
        )