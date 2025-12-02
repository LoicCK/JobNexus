import requests
from typing import List, Optional, Dict, Any
from models.job import Job


class LaBonneAlternanceService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://labonnealternance.apprentissage.beta.gouv.fr/api/v1/jobs"

    def search_jobs(self, longitude: float, latitude: float, radius: int, insee: str, romes: str) -> List[Job]:

        params = {
            "longitude": longitude,
            "latitude": latitude,
            "insee":insee,
            "radius": radius,
            "romes": romes,
            "caller": "jobnexus",
            "sources": "offres,matcha,lba"
        }

        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.get(self.url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Erreur LBA: {e}")
            return []

        results = []

        pe_raw = data.get("peJobs", {}).get("results", [])
        for item in pe_raw:
            if job := self._parse_pe_job(item):
                results.append(job)

        matcha_raw = data.get("matchas", {}).get("results", [])
        for item in matcha_raw:
            if job := self._parse_matcha_job(item):
                results.append(job)

        return results

    def _parse_pe_job(self, item: Dict[str, Any]) -> Optional[Job]:
        try:
            company = item.get("company") or {}
            place = company.get("place") or {}

            return Job(
                title=item.get("title", "Titre Inconnu"),
                company=company.get("name", "Entreprise confidentielle"),
                city=place.get("city") or place.get("fullAddress"),
                url=item.get("url", "#"),
                contract_type="Alternance",
                target_diploma_level=item.get("target_diploma_level") or  "Niveau d'études non précisé",
                source="LBA"
            )
        except Exception as e:
            print(f"Skipping PE job: {e}")
            return None

    def _parse_matcha_job(self, item: Dict[str, Any]) -> Optional[Job]:
        try:
            company = item.get("company") or {}
            place = item.get("place") or {}
            job_details = item.get("job") or {}

            job_id = item.get("id")

            url = item.get("url")

            if not url and job_id:
                base_lba = "https://labonnealternance.apprentissage.beta.gouv.fr/recherche-apprentissage"
                url = f"{base_lba}?type=matcha&itemId={job_id}"

            if not url:
                url = "https://labonnealternance.apprentissage.beta.gouv.fr"

            return Job(
                title=item.get("title", "Titre Inconnu"),
                company=company.get("name", "Entreprise confidentielle"),
                city=place.get("city") or place.get("fullAddress"),
                url=url,
                contract_type=job_details.get("contractType", "Apprentissage"),
                target_diploma_level=item.get("target_diploma_level"),
                source="LBA"
            )
        except Exception as e:
            print(f"Skipping Matcha job: {e}")
            return None