# JobNexus

JobNexus is a powerful aggregator for work-study (alternance) job listings. It consolidates job opportunities from multiple major French platforms into a single, unified API.

## Features

*   **Multi-Source Aggregation**: Retrieves job listings from:
    *   **La Bonne Alternance (LBA)** (France Travail)
    *   **Welcome to the Jungle (WTTJ)**
    *   **APEC**
*   **Smart Search**: Uses ROME codes (Répertoire Opérationnel des Métiers et des Emplois) for standardized job matching.
*   **Caching System**: Implements caching with **Google Cloud Firestore** to optimize performance and reduce API calls.
*   **Unified API**: Provides a centralized endpoint to query all sources simultaneously.
*   **FastAPI Powered**: Built with high-performance Python framework.

## Prerequisites

*   Python >= 3.14
*   [Poetry](https://python-poetry.org/) for dependency management
*   Google Cloud Platform project with Firestore enabled

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/jobnexus.git
    cd jobnexus
    ```

2.  **Install dependencies:**
    ```bash
    poetry install
    ```

## Configuration

Set the following environment variables:

| Variable | Description |
| :--- | :--- |
| `FT_CLIENT_ID` | France Travail Client ID (for ROME service) |
| `FT_CLIENT_SECRET` | France Travail Client Secret (for ROME service) |
| `LBA_API_KEY` | API Key for La Bonne Alternance |
| `WTTJ_APP_ID` | App ID for Welcome to the Jungle |
| `WTTJ_API_KEY` | API Key for Welcome to the Jungle |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to your Google Cloud Service Account JSON key (required for Firestore) |

## Usage

Start the development server:

```bash
poetry run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Core
*   `GET /`: Welcome message and environment check.
*   `GET /health`: Health check status.

### Search
*   `GET /search`: **Main aggregator endpoint.** Searches all configured sources.
    *   `q`: Search query (e.g., "ingénieur cloud")
    *   `longitude`, `latitude`: Location coordinates
    *   `radius`: Search radius in km
    *   `insee`: INSEE code for location

### Individual Sources
*   `GET /lba`: Search La Bonne Alternance directly.
*   `GET /wttj`: Search Welcome to the Jungle directly.
*   `GET /apec`: Search APEC directly.

### Utilities
*   `GET /rome`: Look up ROME codes for a job title.

## License

[MIT](LICENSE)
