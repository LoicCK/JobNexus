from typing import List

from google.cloud import firestore
import hashlib

from models.job import Job


class CacheService:
    def __init__(self):
        self.db = firestore.Client()
        self.collection_name = "job_searches"

    def _generate_cache_key(self, query: str, lat: float, lon: float, radius: int) -> str:
        raw = f"{query}_{lat:.4f}_{lon:.4f}_{radius}"
        return hashlib.md5(raw.encode('utf-8')).hexdigest()

    def save_jobs(self, query: str, lat: float, lon: float, radius: int, jobs: List[Job]):
        search_id = self._generate_cache_key(query, lat, lon, radius)

        # Sérialisation Pydantic (Job -> dict)
        jobs_data = [job.model_dump() for job in jobs]

        doc_ref = self.db.collection(self.collection_name).document(search_id)
        doc_ref.set({
            "query": query,
            "jobs": jobs_data,
            "created_at": datetime.now(timezone.utc)
        })
        print(f"Cache sauvegardé pour {query}")