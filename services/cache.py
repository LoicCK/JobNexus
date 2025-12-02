from typing import List
from google.cloud import firestore
import hashlib
from models.job import Job
from datetime import datetime, timezone


class CacheService:
    def __init__(self):
        self.db = firestore.Client()
        self.collection_name = "job_searches"

    def _generate_cache_key(self, query: str, lat: float, lon: float, radius: int) -> str:
        raw = f"{query}_{lat:.4f}_{lon:.4f}_{radius}"
        return hashlib.md5(raw.encode('utf-8')).hexdigest()

    def save_jobs(self, query: str, lat: float, lon: float, radius: int, jobs: List[Job]):
        research_date = datetime.now(timezone.utc)
        cache_key = self._generate_cache_key(query, lat, lon, radius)
        jobs_data = [job.model_dump() for job in jobs]
        document_content = {
            "date":research_date,
            "params":{
                "query":query,
                "lat":lat,
                "lon":lon,
                "radius":radius
            },
            "jobs":jobs_data
        }
        self.db.collection(self.collection_name).document(cache_key).set(document_content)

    def get_jobs(self, query: str, lat: float, lon: float, radius: int) -> List[Job] | None:
        cache_key = self._generate_cache_key(query, lat, lon, radius)
        doc_ref = self.db.collection(self.collection_name).document(cache_key)
        doc_snapshot = doc_ref.get()
        if not doc_snapshot.exists:
            return None
        data = doc_snapshot.to_dict()
        current_date = datetime.now(timezone.utc)
        cached_date = data["date"]
        age = current_date - cached_date
        if age.total_seconds() > 86400:
            print("Expired cache")
            return None
        jobs_dicts = data.get("jobs", [])
        return [Job.model_validate(j) for j in jobs_dicts]