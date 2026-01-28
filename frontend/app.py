import streamlit as st
import pandas as pd
import os
from google.cloud import bigquery as bq
from datetime import date

# Thanks, Gemini, for the comments

# --- Configuration Constants ---
PAGE_TITLE = "JobNexus"
DATASET_ID = "jobnexus_job_data"
TABLE_ID = "jobnexus_job_table"
DAYS_LOOKBACK = 30  # Time window for data retrieval

# Configure the browser tab title and layout width
st.set_page_config(page_title=PAGE_TITLE, layout="wide")


# --- Data Loading Section ---
# @st.cache_data keeps the data in memory for 3600s (1 hour) to prevent
# re-querying BigQuery on every user interaction (saves cost/improves speed).
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    # Retrieve Google Cloud Project ID from environment variables
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        st.warning("GOOGLE_CLOUD_PROJECT environment variable not set.")
        return _get_empty_df()

    # Initialize BigQuery client
    client = bq.Client(project=project_id)
    table_ref = f"{project_id}.{DATASET_ID}.{TABLE_ID}"

    # SQL Query: Selects specific columns and filters by 'scraped_at' timestamp
    query = f"""
        SELECT
            title, company, city, url, contract_type,
            target_diploma_level, source, scraped_at
        FROM `{table_ref}`
        WHERE scraped_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {DAYS_LOOKBACK} DAY)
        ORDER BY scraped_at DESC
    """

    try:
        # Execute query and convert directly to Pandas DataFrame
        df = client.query(query).to_dataframe()

        if not df.empty:
            # specific conversion to ensure date compatibility with Streamlit charts
            df["scraped_at"] = pd.to_datetime(df["scraped_at"]).dt.date
            return df

        return _get_empty_df()

    except Exception as e:
        # Display error on UI if connection fails
        st.error(f"BigQuery Error: {e}")
        return _get_empty_df()


# Helper function to return a structured empty DataFrame (prevents crashes if query fails)
def _get_empty_df() -> pd.DataFrame:
    columns = [
        "title",
        "company",
        "city",
        "url",
        "contract_type",
        "target_diploma_level",
        "source",
        "scraped_at",
    ]
    return pd.DataFrame(columns=columns)


# --- UI Rendering Functions ---


def render_metrics(df: pd.DataFrame):
    # Filter out generic/hidden company names for the 'Top Recruiter' stat
    visible_companies = df[
        ~df["company"].isin(["Entreprise confidentielle", "Confidentiel"])
    ]

    # Calculate mode (most frequent value) for company and city
    top_recruiter = (
        visible_companies["company"].mode()[0] if not visible_companies.empty else "N/A"
    )
    top_city = df["city"].mode()[0] if not df["city"].empty else "N/A"

    # Display 4 key metrics in a row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Jobs (30d)", len(df))
    c2.metric("Top Recruiter", top_recruiter)
    c3.metric("Top City", top_city)
    c4.metric("Sources", df["source"].nunique())


def render_daily_offers(df: pd.DataFrame):
    today = date.today()
    # Filter data for rows where 'scraped_at' matches today
    todays_offers = df[df["scraped_at"] == today]

    if not todays_offers.empty:
        st.subheader(f"🔥 Daily New Offers ({len(todays_offers)})")
        # specific dataframe config to turn the URL string into a clickable "Apply" button
        st.dataframe(
            todays_offers[["title", "company", "city", "url"]],
            width="stretch",
            hide_index=True,
            column_config={
                "url": st.column_config.LinkColumn("Apply", display_text="Apply ➜"),
                "title": "Job Title",
                "company": "Company",
                "city": "Location",
            },
        )
        st.divider()


def render_charts(df: pd.DataFrame):
    st.subheader("New Offers per Day")
    # Group by date to count offers, sorting by index ensures chronological order
    daily_counts = df["scraped_at"].value_counts().sort_index()
    st.bar_chart(daily_counts, color="#8b5cf6")  # Render bar chart with purple theme
    st.divider()


def render_full_table(df: pd.DataFrame):
    st.subheader(f"All Opportunities ({len(df)})")
    # Display the full dataset with formatted columns
    st.dataframe(
        df[
            ["title", "company", "city", "contract_type", "target_diploma_level", "url"]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "url": st.column_config.LinkColumn("Apply", display_text="Apply ➜"),
            "title": "Job Title",
            "company": "Company",
            "city": "Location",
            "contract_type": "Contract",
            "target_diploma_level": "Education",
        },
    )


# --- Main Application Logic ---
def main():
    st.title("JobNexus Market")
    st.caption("Explore Cloud & DevOps opportunities in real-time")

    # Load data
    df = load_data()

    # Stop execution if data is empty to prevent UI errors
    if df.empty:
        st.info(
            "No data available. Please check your connection or project configuration."
        )
        return

    # Render components sequentially
    render_metrics(df)
    st.divider()
    render_daily_offers(df)
    render_charts(df)
    render_full_table(df)


if __name__ == "__main__":
    main()
