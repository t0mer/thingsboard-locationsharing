import os
import json
import time
import yaml
import shutil
import requests
import schedule
from os import path
from device import Device
from loguru import logger
from locationsharinglib import Service
from cookieshandler import CookiesHandler
from locationsharinglib.locationsharinglibexceptions import InvalidCookies



cookies_file = "./cookies/" + os.getenv("COOKIES_FILE_NAME")
google_email = os.getenv("EMAIL_ADDRESS")
update_interval = os.getenv("UPDATE_INTERVAL")
DEVICES = []
CONFIG_PATH = 'config/devices.yaml'
TB_SERVER_ADDRESS= os.getenv("TB_SERVER_ADDRESS")
cookieshandler = CookiesHandler()

def load_devices():
    try:
        logger.info("Loading devices list")
        if not path.exists(CONFIG_PATH):
            shutil.copy('devices.yaml', CONFIG_PATH)
        with open("config/devices.yaml",'r',encoding='utf-8') as stream:
            try:
                for _device in yaml.safe_load(stream)["devices"]:
                    DEVICES.append(Device(name=_device["name"],id=_device["id"],access_token=_device["access_token"]))
            except yaml.YAMLError as exc:
                logger.error(exc)
    except Exception as e:
        logger.error(str(e))


try:
    service = Service(cookies_file=cookies_file, authenticating_account=google_email)
except InvalidCookies:
    logger.error(
                "The cookie file provided does not provide a valid session. Please"
                " create another one and try again"
            )


def send_telemetry(access_token,payload):
    headers = {"Content-Type": "application/json"}
    report_url = f"{TB_SERVER_ADDRESS}/api/v1/{access_token}/telemetry" 
    
    try:
        response = requests.post(report_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (non-2xx responses)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data: {e}")
    except Exception as e:
        logger.error(f"Failed to send data: {e}")

def run():
    persons = service.get_all_people()
    for person in persons:
        # print(f"Person name: {person.nickname}, Person id: {person.id}")
        _device = [device for device in DEVICES if device.id == person.id ]
        if _device:
            matched_device = _device[0]
            payload = {"latitude": getattr(person, "latitude"), "longitude": getattr(person, "longitude"), "gps_accuracy": getattr(person, "accuracy"), "battery_level": getattr(person, "battery_level")}
            logger.info(f"Sending telemetry for: {person.nickname}")
            send_telemetry(access_token=matched_device.access_token,payload=payload)
    
def refresh_coockies():
    cookieshandler.refresh()
    

if __name__ == "__main__":
    load_devices()
    schedule.every(int(update_interval)).minutes.do(run)
    # schedule.every(15).minutes.do(refresh_coockies)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
