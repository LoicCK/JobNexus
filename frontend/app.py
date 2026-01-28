import streamlit as st
from google.cloud import bigquery as bq
import os


@st.cache_data(ttl=3600)
def load_data():
    client = bq.Client()
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        st.error("Impossible to get the projet ID")
        st.stop()

    sql_query = (
        f"SELECT * FROM `{project_id}.jobnexus_job_data.jobnexus_job_table` LIMIT 1000"
    )
    query_job = client.query(sql_query)
    return query_job.to_dataframe()


st.set_page_config(page_title="JobNexus", layout="wide")

col1, col2, col3 = st.columns(3)

df = load_data()

st.write("Aperçu des données :")
st.dataframe(df)
