"""Go-eCharger API examples"""
import os

from dotenv import load_dotenv
from src.goechargerv2.goecharger import GoeChargerApi

load_dotenv()

charger = GoeChargerApi(os.getenv("GOE_API_URL"), os.getenv("GOE_API_TOKEN"), wait=True)

print(charger.request_status())
# print(charger.set_max_current(13))
