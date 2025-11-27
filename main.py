from fastapi import FastAPI

app = FastAPI(title="JobNexus")

@app.get("/")
def read_root():
    return {"Hello":"Welcome to JobNexus"}

@app.get("/health")
def read_health():
    return {"status":"healthy"}

@app.get("/jobs")
def get_jobs():
    return [{"titre":"Boulanger","entreprise":"Boulangerie truc"},
            {"titre":"Conducteur PL H/F", "entreprise":"JP"}]