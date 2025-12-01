from fastapi import FastAPI
import os
from services.labonnealternance import LaBonneAlternanceService
from services.orchestrator import OrchestratorService
from services.rome import RomeService

ft_id = os.environ.get("FT_CLIENT_ID")
ft_secret = os.environ.get("FT_CLIENT_SECRET")
lba_key = os.environ.get("LBA_API_KEY")
wttj_app_id = os.environ.get("WTTJ_APP_ID")
wttj_api_key = os.environ.get("WTTJ_API_KEY")

rome_service = RomeService(ft_id, ft_secret)
lba_service = LaBonneAlternanceService(lba_key)

orchestrator_service = OrchestratorService(lba_service, rome_service)

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


@app.get("/jobs")
def get_jobs(rome: str = "M1805"):
    jobs = lba_service.search_jobs(romes=rome)

    return {
        "count": len(jobs),
        "results": jobs
    }

@app.get("/rome")
def get_rome_codes(q: str = "boulanger"):
    codes = rome_service.search_rome(q)

    return {
        "count":len(codes),
        "results":codes
    }

@app.get("/search")
def get_jobs_by_query(q: str = "boulanger"):
    jobs = orchestrator_service.find_jobs_by_query(q)

    return {
        "count":len(jobs),
        "results":jobs
    }