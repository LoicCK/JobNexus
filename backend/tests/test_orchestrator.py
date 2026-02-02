from unittest.mock import MagicMock

import pytest

from models.job import Job


@pytest.mark.asyncio
async def test_find_jobs_aggregation(orchestrator, mock_dependencies):
    # mock cache as if the search is not cached, to fetch new data
    mock_dependencies["cache_service"].get_jobs.return_value = None

    # mock a ROME code, to avoid Orchestrator from skipping LBA
    mock_rome = MagicMock()
    mock_rome.code = "M1805"
    mock_dependencies["rome_service"].search_rome.return_value = [mock_rome]

    # mock APEC
    job_apec = Job(
        title="Dev Apec",
        company="Apec Corp",
        city="Paris",
        url="http://apec",
        target_diploma_level="Master",
        source="APEC",
    )
    mock_dependencies["apec_service"].search_jobs.return_value = [job_apec]

    # mock WTTJ
    job_wttj = Job(
        title="Dev WTTJ",
        company="Jungle Corp",
        city="Paris",
        url="http://wttj",
        target_diploma_level="Bachelor",
        source="WTTJ",
    )
    mock_dependencies["wttj_service"].search_jobs.return_value = [job_wttj]

    # mock LBA
    job_lba = Job(
        title="Dev LBA",
        company="Gov Corp",
        city="Paris",
        url="http://lba",
        target_diploma_level="CAP",
        source="LBA",
    )
    mock_dependencies["lba_service"].search_jobs.return_value = [job_lba]

    # mock background tasks
    mock_background_tasks = MagicMock()

    # run the orchestrator logic
    results = await orchestrator.find_jobs_by_query(
        query="Developer",
        longitude=2.35,
        latitude=48.85,
        radius=10,
        insee="75056",
        background_tasks=mock_background_tasks,
    )

    # we expect 3 jobs total (1 from each provider)
    assert len(results) == 3

    # verify aggregation
    titles = [job.title for job in results]
    assert "Dev Apec" in titles
    assert "Dev WTTJ" in titles
    assert "Dev LBA" in titles

    # verify logic
    assert results[0].search_query == "Developer"

    # verify if the orchestrator tried to save cache and data
    assert mock_background_tasks.add_task.call_count == 2
