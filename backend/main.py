import logging
import sys
import traceback

import google.cloud.logging
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException

import dependencies as dp
from services.apec import ApecService
from services.data import DataService
from services.labonnealternance import LaBonneAlternanceService
from services.orchestrator import OrchestratorService
from services.rome import RomeService
from services.wttj import WelcomeService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

try:
    client = google.cloud.logging.Client()
    client.setup_logging()
except Exception as e:
    logging.warning(f"Failed to activate Cloud Logging: {str(e)}")

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
    lba_service: LaBonneAlternanceService = Depends(dp.get_lba_service),
):
    jobs = await lba_service.search_jobs(longitude, latitude, radius, insee, romes)

    return {"count": len(jobs), "results": jobs}


@app.get("/rome")
async def get_rome_codes(
    q: str, rome_service: RomeService = Depends(dp.get_rome_service)
):
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
    orchestrator_service: OrchestratorService = Depends(dp.get_orchestrator_service),
):
    try:
        jobs = await orchestrator_service.find_jobs_by_query(
            q, longitude, latitude, radius, insee, background_tasks
        )

        return {"count": len(jobs), "results": jobs}
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/wttj")
async def get_jobs_by_wttj(
    q: str,
    latitude: float,
    longitude: float,
    radius: int,
    wttj_service: WelcomeService = Depends(dp.get_wttj_service),
):
    wttj_jobs = await wttj_service.search_jobs(q, latitude, longitude, radius)

    return {"count": len(wttj_jobs), "results": wttj_jobs}


@app.get("/apec")
async def get_jobs_by_apec(
    q: str, insee: str, apec_service: ApecService = Depends(dp.get_apec_service)
):
    apec_jobs = await apec_service.search_jobs(q, insee)

    return {"count": len(apec_jobs), "results": apec_jobs}


@app.get("/opportunities")
def get_opportunities(
    q: str,
    limit: int = 50,
    skip: int = 0,
    data_service: DataService = Depends(dp.get_data_service),
):
    jobs = data_service.get_opportunities(search_query=q, limit=limit, offset=skip)
    return {"count": len(jobs), "results": jobs}
