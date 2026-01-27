from typing import List

import requests

from models.job import Job


class ApecService:
    def __init__(self):
        self.session = requests.session()
        headers = {
            "Host": "www.apec.fr",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) "
            "Gecko/20100101 Firefox/145.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/json",
            "Origin": "https://www.apec.fr",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        self.session.headers.update(headers)
        self.session.get("https://www.apec.fr/")
        self.url = "https://www.apec.fr/cms/webservices/rechercheOffre"
        self.payload = {
            "lieux": [],
            "fonctions": [],
            "statutPoste": [],
            "typesContrat": ["20053"],
            "typesConvention": ["143684", "143685", "143686", "143687"],
            "niveauxExperience": [],
            "idsEtablissement": [],
            "secteursActivite": [],
            "typesTeletravail": [],
            "idNomZonesDeplacement": [],
            "positionNumbersExcluded": [],
            "typeClient": "CADRE",
            "sorts": [{"type": "SCORE", "direction": "DESCENDING"}],
            "pagination": {"range": 50, "startIndex": 0},
            "activeFiltre": True,
            "pointGeolocDeReference": {"distance": 0},
            "motsCles": "",
        }

    def search_jobs(self, query: str, insee: str) -> List[Job]:
        code_dep = insee[:2]
        search_headers = {
            "Referer": f"https://www.apec.fr/candidat/recherche-emploi.html/emploi?typesContrat=20053&motsCles={query}&lieux={code_dep}"
        }
        self.payload["lieux"] = [code_dep]
        self.payload["motsCles"] = query
        try:
            response = self.session.post(
                self.url, json=self.payload, headers=search_headers
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Erreur: {e}")
            return []
        resultats = data["resultats"]
        jobs = []
        for result in resultats:
            job = Job(
                title=result["intitule"],
                company=result["nomCommercial"],
                city=result["lieuTexte"],
                url=f"https://www.apec.fr/candidat/recherche-emploi.html/emploi/detail-offre/{result['numeroOffre']}",
                target_diploma_level="Inconnu",
                source="APEC",
            )
            jobs.append(job)
        return jobs
