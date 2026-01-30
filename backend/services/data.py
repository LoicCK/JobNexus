import hashlib
import json
import os
from datetime import datetime, timezone
from typing import List
from urllib.parse import urlparse, urlunparse

from google.cloud import bigquery

from models.job import Job


class DataService:
    def __init__(self):
        self.client = bigquery.Client()
        self.table_id = os.getenv("BIGQUERY_TABLE_ID")
        if not self.table_id:
            raise ValueError("Environment variable BIGQUERY_TABLE_ID is not set")

    def generate_job_hash(self, job: Job) -> str:
        parsed = urlparse(job.url)
        clean_url = urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, parsed.params, "", "")
        )
        raw_string = f"{job.title}{job.company}{clean_url}".lower()
        return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()

    def get_job_dict(self, job: Job) -> dict:
        job_dict = job.model_dump() if hasattr(job, "model_dump") else job.dict()
        job_dict["scraped_at"] = datetime.now(timezone.utc).isoformat()
        job_dict["job_hash"] = self.generate_job_hash(job)
        return job_dict

    def save_jobs_data(self, jobs: List[Job]):
        """
        Reference:
        - MERGE Syntax: https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax#merge_statement
        - Query Parameters: https://cloud.google.com/bigquery/docs/parameterized-queries#array_parameters
        - JSON Functions: https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/json_functions
        - Working With Arrays: https://docs.cloud.google.com/bigquery/docs/arrays

        """
        if not jobs:
            return

        rows_to_insert = [self.get_job_dict(job) for job in jobs]
        jobs_json_string = json.dumps(rows_to_insert, default=str)

        query = f"""
        MERGE `{self.table_id}` T
        USING (
          SELECT
            JSON_VALUE(item, '$.search_query') as search_query,
            JSON_VALUE(item, '$.job_hash') as job_hash,
            JSON_VALUE(item, '$.title') as title,
            JSON_VALUE(item, '$.company') as company,
            JSON_VALUE(item, '$.city') as city,
            JSON_VALUE(item, '$.url') as url,
            JSON_VALUE(item, '$.contract_type') as contract_type,
            JSON_VALUE(item, '$.target_diploma_level') as target_diploma_level,
            JSON_VALUE(item, '$.source') as source,
            TIMESTAMP(JSON_VALUE(item, '$.scraped_at')) as scraped_at
          FROM UNNEST(JSON_EXTRACT_ARRAY(@json_data)) AS item
        ) S
        ON T.job_hash = S.job_hash
        WHEN NOT MATCHED THEN
          INSERT (
              search_query, job_hash, title, company, city, url,
              contract_type, target_diploma_level, source, scraped_at
          )
          VALUES (
              S.search_query, S.job_hash, S.title, S.company, S.city, S.url,
              S.contract_type, S.target_diploma_level, S.source, S.scraped_at
          )
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("json_data", "STRING", jobs_json_string)
            ]
        )

        query_job = self.client.query(query, job_config=job_config)
        query_job.result()

    def get_opportunities(
        self, search_query: str, limit: int = 50, offset: int = 0
    ) -> List[dict]:
        query = f"""
            SELECT
                title, company, city, url, contract_type,
                target_diploma_level, source, scraped_at
            FROM `{self.table_id}`
            WHERE scraped_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 120 DAY)
            AND search_query = @search_query
            ORDER BY scraped_at DESC
            LIMIT @limit OFFSET @offset
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("search_query", "STRING", search_query),
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
                bigquery.ScalarQueryParameter("offset", "INT64", offset),
            ]
        )

        query_job = self.client.query(query, job_config=job_config)

        results = []
        for row in query_job:
            results.append(
                {
                    "title": row.title,
                    "company": row.company,
                    "city": row.city,
                    "url": row.url,
                    "contract_type": row.contract_type,
                    "target_diploma_level": row.target_diploma_level,
                    "source": row.source,
                    "scraped_at": row.scraped_at,
                }
            )

        return results
