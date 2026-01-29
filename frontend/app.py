import os
from datetime import date

import pandas as pd
import requests
import streamlit as st

PAGE_TITLE = "JobNexus"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

JOB_CATEGORIES = [
    "DevOps",
    "DevSecOps",
    "SRE",
    "Ingenieur-Cloud",
    "Ingenieur-Systeme",
    "Ingenieur-Reseaux",
    "Cybersecurity",
    "Cloud-Computing",
]

st.set_page_config(page_title=PAGE_TITLE, layout="wide")


@st.cache_data(ttl=3600)
def load_data(category: str) -> pd.DataFrame:
    try:
        response = requests.get(
            f"{BACKEND_URL}/opportunities", params={"q": category, "limit": 1000}
        )
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data.get("results", []))

        if not df.empty:
            df["scraped_at"] = pd.to_datetime(df["scraped_at"]).dt.date
            return df

        return _get_empty_df()

    except Exception as e:
        st.error(f"API Error: {e}")
        return _get_empty_df()


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


def render_metrics(df: pd.DataFrame):
    visible_companies = df[
        ~df["company"].isin(["Entreprise confidentielle", "Confidentiel"])
    ]

    top_recruiter = (
        visible_companies["company"].mode()[0] if not visible_companies.empty else "N/A"
    )
    top_city = df["city"].mode()[0] if not df["city"].empty else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Jobs (30d)", len(df))
    c2.metric("Top Recruiter", top_recruiter)
    c3.metric("Top City", top_city)
    c4.metric("Sources", df["source"].nunique())


def render_daily_offers(df: pd.DataFrame):
    today = date.today()
    todays_offers = df[df["scraped_at"] == today]

    if not todays_offers.empty:
        st.subheader(f"🔥 Daily New Offers ({len(todays_offers)})")
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
    daily_counts = df["scraped_at"].value_counts().sort_index()
    st.bar_chart(daily_counts, color="#8b5cf6")
    st.divider()


def render_full_table(df: pd.DataFrame):
    st.subheader(f"All Opportunities ({len(df)})")
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


def main():
    st.title("JobNexus Market")
    st.caption("Explore Cloud & DevOps opportunities in real-time")

    selected_category = st.selectbox("Select Job Category", JOB_CATEGORIES)

    df = load_data(selected_category)

    if df.empty:
        st.info(
            "No data available. Please check your connection or project configuration."
        )
        return

    render_metrics(df)
    st.divider()
    render_daily_offers(df)
    render_charts(df)
    render_full_table(df)


if __name__ == "__main__":
    main()
