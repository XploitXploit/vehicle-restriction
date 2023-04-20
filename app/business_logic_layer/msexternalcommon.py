import requests
from app.settings import settings


class Bll_MsExternaCommon:
    def __init__(self):
        pass

    def get_api_vehicles(self):
        vehicles_response = requests.get(
            settings.GOWGO_API_URL + "msexternalcommon/macktest/all-vehicle-list",
            auth=(settings.GOWGO_USER, settings.GOWGO_PASSWORD),
        )
        return vehicles_response
