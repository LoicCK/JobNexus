from services.labonnealternance import LaBonneAlternanceService
from services.rome import RomeService
from models.job import Job
from typing import List

class OrchestratorService:
    def __init__(self, lba_service: LaBonneAlternanceService, rome_service: RomeService):
        self.lba_service = lba_service
        self.rome_service = rome_service

    def find_jobs_by_query(self, query: str) -> List[Job]:
        romes = self.rome_service.search_rome(query)
        codes = [rome.code for rome in romes]
        codes = ",".join(codes)
        jobs = self.lba_service.search_jobs(romes=codes)
        return jobs