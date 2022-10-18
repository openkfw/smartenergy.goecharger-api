import os

from goecharger.goecharger import GoeChargerApi
from dotenv import load_dotenv

load_dotenv()

charger = GoeChargerApi(os.getenv("GOE_API_URL"), os.getenv("GOE_API_TOKEN"), wait=True)

print(charger.request_status())
# print(charger.set_max_current(13))
