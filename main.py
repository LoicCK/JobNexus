from fastapi import FastAPI
import os

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
def get_jobs():
    return [{"titre":"Boulanger","entreprise":"Boulangerie truc"},
            {"titre":"Conducteur PL H/F", "entreprise":"JP"}]
