from typing import Dict, Any, List

from algoliasearch.configs import SearchConfig
from algoliasearch.search_client import SearchClient
from models.job import Job

class WelcomeService:
    def __init__(self, wttj_app_id: str, wttj_api_key: str):
        self.app_id = wttj_app_id
        self.api_key = wttj_api_key
        self.index = "wttj_jobs_production_fr"

        config = SearchConfig(wttj_app_id, wttj_api_key)
        config.headers['Referer'] = 'https://www.welcometothejungle.com/'
        self.client = SearchClient.create_with_config(config)
        self.index = self.client.init_index(self.index)

    def search_jobs(self, query: str, latitude: float, longitude: float, radius: int) -> List[Job]:
        search_params = {
            'filters': 'contract_type:apprenticeship',
            'hitsPerPage': 50,
            'attributesToRetrieve': ['name', 'organization', 'offices', 'contract_type', 'slug'],
            'aroundLatLng':f"{latitude},{longitude}",
            'aroundRadius': radius * 1000
        }

        try:
            hits = self.index.search(query, search_params)['hits']
            results = [self._parse_algolia_hit(hit) for hit in hits]
            return results
        except Exception as e:
            print(f"Erreur WTTJ: {e}")
            return []

    def _parse_algolia_hit(self, hit: Dict[str, Any]) -> Job:
        offre_slug = hit.get("slug")
        organization = hit.get("organization",{})
        organization_slug = organization.get("slug")
        offices = hit.get('offices', [])
        city = "Ville non spécifiée"

        if offices and isinstance(offices, list) and len(offices) > 0:
            first_office = offices[0]
            raw_city = first_office.get('city')
            if isinstance(raw_city, dict):
                city = raw_city.get('value', city)
            elif isinstance(raw_city, str):
                city = raw_city

        return Job(
            title=hit.get("name"),
            company=organization.get("name"),
            city=city,
            url=f"https://www.welcometothejungle.com/fr/companies/{organization_slug}/jobs/{offre_slug}",
            target_diploma_level="Inconnu",
            source="WTTJ"
        )