import os

from fastapi import BackgroundTasks, FastAPI

from services.apec import ApecService
from services.cache import CacheService
from services.data import DataService
from services.labonnealternance import LaBonneAlternanceService
from services.orchestrator import OrchestratorService
from services.rome import RomeService
from services.wttj import WelcomeService

ft_id = os.environ.get("FT_CLIENT_ID")
ft_secret = os.environ.get("FT_CLIENT_SECRET")
lba_key = os.environ.get("LBA_API_KEY")
wttj_app_id = os.environ.get("WTTJ_APP_ID")
wttj_api_key = os.environ.get("WTTJ_API_KEY")

rome_service = RomeService(ft_id, ft_secret)
lba_service = LaBonneAlternanceService(lba_key)
wttj_service = WelcomeService(wttj_app_id, wttj_api_key)
cache_service = CacheService()
apec_service = ApecService()
data_service = DataService()

orchestrator_service = OrchestratorService(
    lba_service, rome_service, wttj_service, cache_service, apec_service, data_service
)

app = FastAPI(title="JobNexus")


@app.get("/")
def read_root():
    return {"Hello": "Welcome to JobNexus"}


@app.get("/health")
def read_health():
    return {"status": "healthy"}


@app.get("/lba")
async def get_jobs_by_lba(
    longitude: float,
    latitude: float,
    radius: int,
    insee: str,
    romes: str,
):
    jobs = await lba_service.search_jobs(longitude, latitude, radius, insee, romes)

    return {"count": len(jobs), "results": jobs}


@app.get("/rome")
async def get_rome_codes(q: str):
    codes = await rome_service.search_rome(q)

    return {"count": len(codes), "results": codes}


@app.get("/search")
async def get_jobs_by_query(
    background_tasks: BackgroundTasks,
    q: str,
    longitude: float,
    latitude: float,
    radius: int,
    insee: str,
):
    jobs = await orchestrator_service.find_jobs_by_query(
        q, longitude, latitude, radius, insee, background_tasks
    )

    return {"count": len(jobs), "results": jobs}


@app.get("/wttj")
async def get_jobs_by_wttj(q: str, latitude: float, longitude: float, radius: int):
    wttj_jobs = await wttj_service.search_jobs(q, latitude, longitude, radius)

    return {"count": len(wttj_jobs), "results": wttj_jobs}


@app.get("/apec")
async def get_jobs_by_apec(q: str, insee: str):
    apec_jobs = await apec_service.search_jobs(q, insee)

    return {"count": len(apec_jobs), "results": apec_jobs}
