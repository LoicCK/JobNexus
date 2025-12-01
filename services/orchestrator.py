from services.labonnealternance import LaBonneAlternanceService
from services.rome import RomeService
from services.wttj import WelcomeService
from models.job import Job
from typing import List

class OrchestratorService:
    def __init__(self, lba_service: LaBonneAlternanceService, rome_service: RomeService, wttj_service: WelcomeService):
        self.lba_service = lba_service
        self.rome_service = rome_service
        self.wttj_service = wttj_service

    def find_jobs_by_query(self, query: str,  longitude: float, latitude: float, radius: int, insee: str) -> List[Job]:
        romes = self.rome_service.search_rome(query)
        if not romes:
            print("Aucun ROME trouvé")
            return self.wttj_service.search_jobs(query, longitude, latitude, radius)
        codes = [rome.code for rome in romes]
        codes = ",".join(codes)
        jobs = self.lba_service.search_jobs(longitude, latitude, radius, insee, codes)
        jobs.extend(self.wttj_service.search_jobs(query, latitude, longitude, radius))
        return jobs