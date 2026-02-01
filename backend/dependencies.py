import os
from functools import lru_cache

from fastapi import Depends

from services.apec import ApecService
from services.cache import CacheService
from services.data import DataService
from services.labonnealternance import LaBonneAlternanceService
from services.orchestrator import OrchestratorService
from services.rome import RomeService
from services.wttj import WelcomeService


@lru_cache()
def get_rome_service():
    ft_id = os.environ.get("FT_CLIENT_ID")
    ft_secret = os.environ.get("FT_CLIENT_SECRET")

    return RomeService(ft_id, ft_secret)


@lru_cache()
def get_lba_service():
    lba_key = os.environ.get("LBA_API_KEY")

    return LaBonneAlternanceService(lba_key)


@lru_cache()
def get_wttj_service():
    wttj_app_id = os.environ.get("WTTJ_APP_ID")
    wttj_api_key = os.environ.get("WTTJ_API_KEY")

    return WelcomeService(wttj_app_id, wttj_api_key)


@lru_cache()
def get_cache_service():
    return CacheService()


@lru_cache()
def get_apec_service():
    return ApecService()


@lru_cache()
def get_data_service():
    return DataService()


def get_orchestrator_service(
    lba_service: LaBonneAlternanceService = Depends(get_lba_service),
    rome_service: RomeService = Depends(get_rome_service),
    wttj_service: WelcomeService = Depends(get_wttj_service),
    cache_service: CacheService = Depends(get_cache_service),
    apec_service: ApecService = Depends(get_apec_service),
    data_service: DataService = Depends(get_data_service),
):
    return OrchestratorService(
        lba_service,
        rome_service,
        wttj_service,
        cache_service,
        apec_service,
        data_service,
    )
