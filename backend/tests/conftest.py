from unittest.mock import AsyncMock, MagicMock

import pytest

from services.orchestrator import OrchestratorService


@pytest.fixture
def mock_dependencies():
    return {
        "lba_service": AsyncMock(),
        "rome_service": AsyncMock(),
        "wttj_service": AsyncMock(),
        "cache_service": AsyncMock(),
        "apec_service": AsyncMock(),
        "data_service": MagicMock(),
    }


@pytest.fixture
def orchestrator(mock_dependencies):
    return OrchestratorService(
        lba_service=mock_dependencies["lba_service"],
        rome_service=mock_dependencies["rome_service"],
        wttj_service=mock_dependencies["wttj_service"],
        cache_service=mock_dependencies["cache_service"],
        apec_service=mock_dependencies["apec_service"],
        data_service=mock_dependencies["data_service"],
    )
