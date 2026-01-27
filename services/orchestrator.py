import logging
from typing import List

from fastapi import BackgroundTasks

from models.job import Job
from services.apec import ApecService
from services.cache import CacheService
from services.data import DataService
from services.labonnealternance import LaBonneAlternanceService
from services.rome import RomeService
from services.wttj import WelcomeService


class OrchestratorService:
    def __init__(
        self,
        lba_service: LaBonneAlternanceService,
        rome_service: RomeService,
        wttj_service: WelcomeService,
        cache_service: CacheService,
        apec_service: ApecService,
        data_service: DataService,
    ):
        self.lba_service = lba_service
        self.rome_service = rome_service
        self.wttj_service = wttj_service
        self.cache_service = cache_service
        self.apec_service = apec_service
        self.data_service = data_service
        self.logger = logging.getLogger(__name__)

    def find_jobs_by_query(
        self,
        query: str,
        longitude: float,
        latitude: float,
        radius: int,
        insee: str,
        background_tasks: BackgroundTasks,
    ) -> List[Job]:
        cached_jobs = self.cache_service.get_jobs(query, latitude, longitude, radius)
        if cached_jobs is not None:
            return cached_jobs
        romes = self.rome_service.search_rome(query)
        if not romes:
            return self.wttj_service.search_jobs(query, longitude, latitude, radius)
        codes = [rome.code for rome in romes]
        codes = ",".join(codes)
        jobs = []
        try:
            jobs.extend(
                self.lba_service.search_jobs(latitude, longitude, radius, insee, codes)
            )
        except Exception:
            self.logger.error("Failed to get jobs on LBA", exc_info=True)
        try:
            jobs.extend(
                self.wttj_service.search_jobs(query, latitude, longitude, radius)
            )
        except Exception:
            self.logger.error("Failed to get jobs on WTTJ", exc_info=True)
        try:
            jobs.extend(self.apec_service.search_jobs(query, insee))
        except Exception:
            self.logger.error("Failed to get jobs on APEC", exc_info=True)
        try:
            self.cache_service.save_jobs(query, latitude, longitude, radius, jobs)
        except Exception:
            self.logger.error("Failed cache jobs to FireStore", exc_info=True)
        try:
            background_tasks.add_task(self.data_service.save_jobs_data, jobs)
        except Exception:
            self.logger.error("Failed to save jobs to BigQuery", exc_info=True)
        return jobs
