# JobNexus

JobNexus is a work-study job aggregator built with Python and FastAPI. It consolidates job listings from multiple platforms into a single, unified API.

## Features

- **Multi-source Aggregation**: Aggregates job offers from:
  - **La Bonne Alternance**
  - **Welcome to the Jungle**
  - **APEC**
  - **France Travail** (via ROME service for categorization)
- **Unified Search**: Provides a single endpoint to search across all supported platforms.
- **Caching**: Utilizes Google Cloud Firestore to cache results and improve performance.
- **REST API**: Built with FastAPI, offering automatic interactive documentation.

## Prerequisites

- **Python** >= 3.14
- **Poetry**: For dependency management.
- **Google Cloud Credentials**: Access to a Google Cloud project with Firestore enabled.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LoicCK/JobNexus
   cd jobnexus
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

## Configuration

The application relies on several environment variables for authentication with external services. Ensure these are set in your environment before running the application.

| Variable | Description |
|----------|-------------|
| `FT_CLIENT_ID` | France Travail Client ID |
| `FT_CLIENT_SECRET` | France Travail Client Secret |
| `LBA_API_KEY` | La Bonne Alternance API Key |
| `WTTJ_APP_ID` | Welcome to the Jungle App ID |
| `WTTJ_API_KEY` | Welcome to the Jungle API Key |

## Usage

Start the development server using Uvicorn:

```bash
poetry run uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can access it at:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoints

- **GET /**: Welcome message and environment status check.
- **GET /health**: Health check.
- **GET /search**: **Main endpoint**. Searches for jobs across all configured services.
  - Query parameters: `q`, `longitude`, `latitude`, `radius`, `insee`.
- **GET /lba**: Search La Bonne Alternance directly.
- **GET /wttj**: Search Welcome to the Jungle directly.
- **GET /apec**: Search APEC directly.
- **GET /rome**: Search for ROME codes (used for categorization).

## Development

This project uses `black` for code formatting and `ruff` for linting.

```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
