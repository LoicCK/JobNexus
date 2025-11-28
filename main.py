from fastapi import FastAPI
import os
from services.labonnealternance import LaBonneAlternanceService

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
    api_key = os.environ.get("LBA_API_KEY", "")

    service = LaBonneAlternanceService(api_key)

    jobs = service.search_jobs(romes=rome)

    return {
        "count": len(jobs),
        "results": jobs
    }
