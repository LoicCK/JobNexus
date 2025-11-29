import requests
from time import time
from models.rome_code import RomeCode
from typing import List

class RomeService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.credential_url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
        self.url = "https://api.francetravail.io/partenaire/rome-metiers/v1/metiers/appellation/requete"
        self.token = None
        self.expiration_time = -1

    def search_rome(self, query: str) -> List[RomeCode]:
        if time() >= self.expiration_time:
            oauth_payload = {
                "grant_type":"client_credentials",
                "client_id":self.client_id,
                "client_secret":self.client_secret,
                "scope":"api_rome-metiersv1 nomenclatureRome"
            }

            oauth_headers = {"Content-Type":"application/x-www-form-urlencoded"}

            try:
                response = requests.post(self.credential_url, data=oauth_payload, headers=oauth_headers)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"Erreur OAuth ROME: {e}")
                return []

            self.token = data["access_token"]
            self.expiration_time = time() + data["expires_in"] - 60

        params = {"q":query}
        headers={"Authorization":f"Bearer {self.token}"}

        try:
            response = requests.get(self.url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Erreur API ROME: {e}")
            return []

        if data["totalResultats"] == 0:
            return []

        resultats = data["resultats"]

        rome_codes = []

        for res in resultats:
            print(res)
            code = RomeCode(
                libelle=res.get("libelle","Libellé non défini"),
                code=f"M{res.get('code', '0')}"
            )
            rome_codes.append(code)

        return rome_codes