from fastapi import FastAPI
import os
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

orchestrator_service = OrchestratorService(lba_service, rome_service, wttj_service)

app = FastAPI(title="JobNexus")

@app.get("/")
def read_root():
    client_id = os.environ.get("FT_CLIENT_ID", "Non défini")
    masked_id = client_id[:4] + "*" * 10 if client_id != "Non défini" else "Non défini"
    return {
        "Hello": "Welcome to JobNexus",
        "Environment": "Production" if client_id != "Non défini" else "Local",
        "Client_ID_Check": masked_id
    }

@app.get("/health")
def read_health():
    return {"status":"healthy"}


@app.get("/lba")
def get_jobs_by_lba(longitude: float = 2.3522,
             latitude: float = 48.8566,
             radius: int = 30,
             insee: str = "75056",
             romes: str = "M1805"):
    jobs = lba_service.search_jobs(longitude, latitude, radius, insee, romes)

    return {
        "count": len(jobs),
        "results": jobs
    }

@app.get("/rome")
def get_rome_codes(q: str = "ingénieur cloud"):
    codes = rome_service.search_rome(q)

    return {
        "count":len(codes),
        "results":codes
    }

@app.get("/search")
def get_jobs_by_query(q: str = "ingénieur cloud",
                      longitude: float = 2.3522,
                      latitude: float = 48.8566,
                      radius: int = 30,
                      insee: str = "75056",
                      romes: str = "M1805"):
    jobs = orchestrator_service.find_jobs_by_query(q, longitude, latitude, radius, insee, romes)

    return {
        "count":len(jobs),
        "results":jobs
    }

@app.get("/wttj")
def get_jobs_by_wttj(q: str,
                     latitude: float = 48.85341,
                     longitude: float = 2.3488,
                     radius: int = 20):
    wttj_jobs = wttj_service.search_jobs(q, latitude, longitude, radius)

    return {
        "count":len(wttj_jobs),
        "results":wttj_jobs
    }