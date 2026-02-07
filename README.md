# JobNexus

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.122-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.53-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![GCP](https://img.shields.io/badge/Google_Cloud-Deployed-4285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **Streamline your apprenticeship search by aggregating France's top job boards into one powerful interface.**

JobNexus is an apprenticeship job aggregation platform designed to consolidate listings from multiple French job boards into a single, unified interface. By integrating data from **APEC**, **La Bonne Alternance**, and **Welcome to the Jungle**, it provides a centralized search engine for job seekers.

The system utilizes [**ROME codes**](https://www.francetravail.fr/employeur/vos-recrutements/le-rome-et-les-fiches-metiers.html) (Répertoire Opérationnel des Métiers et des Emplois) to standardize job categories across different providers and implements a caching layer to optimize performance and reduce external API calls.

## Architecture

JobNexus operates on a microservices architecture hosted on **Google Cloud Platform**.

<p align="center">
  <img src="docs/architecture.svg" alt="JobNexus Architecture" width="800">
</p>

The system consists of three main components:
1.  **Frontend (Streamlit):** Provides the user interface for searching and visualizing job data.
2.  **Backend (FastAPI):** Acts as an orchestrator that fetches, normalizes, and caches data from external providers.
3.  **Infrastructure (Terraform):** Manages the deployment of resources on Google Cloud Run and API Gateway.

## Tech Stack

This project utilizes a modern Python stack and cloud-native technologies.

### Core
* **Language:** Python 3.14
* **Package Manager:** Poetry

### Backend
* **Framework:** FastAPI
* **Server:** Uvicorn
* **Data Storage:** Google Cloud Firestore, BigQuery
* **Testing:** Pytest (Asyncio)

### Frontend
* **Framework:** Streamlit
* **Visualization:** Plotly, Pandas
* **Authentication:** Google Auth

### DevOps & Infrastructure
* **IaC:** Terraform
* **Containerization:** Docker
* **CI/CD:** Google Cloud Build

## Features

* **Aggregated Search:** Query multiple job boards simultaneously with a single request.
* **Orchestration Engine:** Parallel data fetching from APEC, LBA, and WTTJ to minimize latency.
* **Geo-Spatial Filtering:** Search capabilities based on longitude, latitude, and radius.
* **Analytics Dashboard:** Visual metrics regarding active jobs, top recruiters, and daily offer volume.
* **Asynchronous Processing:** Background tasks for data caching and archival.

## Extending JobNexus

JobNexus is designed to be easily extensible. To add a new job board provider (e.g., Indeed, LinkedIn), follow these steps:

1.  **Create a Service:** Add a new file in `backend/services/` (e.g., `new_provider.py`). Your class must implement a `search_jobs` method that returns a list of `Job` models.

    ```python
    # backend/services/new_provider.py
    class NewProviderService:
        async def search_jobs(self, query: str, ...) -> List[Job]:
            # Implement API call or scraping logic here
            return [Job(...)]
    ```

2.  **Register Dependency:** Initialize your service in `backend/dependencies.py`.

3.  **Update Orchestrator:** Inject the new service into `backend/services/orchestrator.py` and add it to the aggregation logic.

    ```python
    # backend/services/orchestrator.py
    # ... inside find_jobs_by_query method
    searches = [
        self.wttj_service.search_jobs(...),
        self.apec_service.search_jobs(...),
        self.new_provider_service.search_jobs(...) # Add your new service here
    ]
    ```

## API Reference

The backend exposes a RESTful API. Documentation is available at `/docs` when the server is running.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/search` | Main orchestrator endpoint. Searches all providers by query and location. |
| `GET` | `/opportunities` | Retrieves aggregated opportunities stored in the database. |
| `GET` | `/lba` | Fetches jobs specifically from *La Bonne Alternance*. |
| `GET` | `/wttj` | Fetches jobs specifically from *Welcome to the Jungle*. |
| `GET` | `/apec` | Fetches jobs specifically from *APEC*. |
| `GET` | `/rome` | Resolves job titles to standardized ROME codes. |

## Getting Started

### Prerequisites

* **Docker**
* **Poetry** (Python dependency manager)
* **Google Cloud SDK** (Optional, for deployment)

### 1. Backend Setup

The backend handles all data logic and API exposure.

```bash
cd backend

# Install dependencies
poetry install

# Configure Environment
cp .env.example .env
# Edit .env with your API keys (APEC, France Travail, etc.)

# Start the server
poetry run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### 2. Frontend Setup

The frontend provides the dashboard interface.

```bash
cd frontend

# Install dependencies
poetry install

# Configure Environment
cp .env.example .env
# Ensure BACKEND_URL is pointing to your backend

# Launch the Dashboard
poetry run streamlit run app.py
```

The UI will be accessible at `http://localhost:8501`.

## Docker Support

The project includes Dockerfiles for containerized execution.

**Backend**
```bash
docker build -t jobnexus-backend ./backend
docker run -p 8000:8080 --env-file ./backend/.env jobnexus-backend
```

**Frontend**
```bash
docker build -t jobnexus-frontend ./frontend
docker run -p 8080:8080 --env-file ./frontend/.env jobnexus-frontend
```

## Infrastructure

Infrastructure is managed as code using **Terraform**.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## How to Contribute

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  **Fork the Project**
2.  **Create your Feature Branch**
3.  **Commit your Changes**
4.  **Push to the Branch**
5.  **Open a Pull Request**

### Development Guidelines
* Ensure you have **pre-commit** installed to maintain code quality.
* Write tests for new features in the `backend/tests` directory.
* Follow the existing code style (Black, Isort).

## License

Distributed under the MIT License. See `LICENSE` for more information.
