from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from twilio.rest import Client

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
from datetime import date
import logging
import os
import boto3
import json
import time
import random
import datetime
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(process)d --- %(name)s %(funcName)20s() : %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

logger = logging.getLogger('AppointmentChecker')

client = Client(os.environ['TWILIO_ACCOUNT_SID'],
                os.environ['TWILIO_AUTH_TOKEN'])

text_body = f"""
swedish appointment might be available! \n

https://www.migrationsverket.se/ansokanbokning/omboka?enhet=UM&sprak=en&callback=http://www.swedenabroad.com/ \n
SHRB-1409 \n
srsani@gmail.com
"""


def __get_default_chrome_options():
    chrome_options = webdriver.ChromeOptions()
    lambda_options = [
        '--autoplay-policy=user-gesture-required',
        '--disable-background-networking',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-breakpad',
        '--disable-client-side-phishing-detection',
        '--disable-component-update',
        '--disable-default-apps',
        '--disable-dev-shm-usage',
        '--disable-domain-reliability',
        '--disable-extensions',
        '--disable-features=AudioServiceOutOfProcess',
        '--disable-hang-monitor',
        '--disable-ipc-flooding-protection',
        '--disable-notifications',
        '--disable-offer-store-unmasked-wallet-cards',
        '--disable-popup-blocking',
        '--disable-print-preview',
        '--disable-prompt-on-repost',
        '--disable-renderer-backgrounding',
        '--disable-setuid-sandbox',
        '--disable-speech-api',
        '--disable-sync',
        '--disk-cache-size=33554432',
        '--hide-scrollbars',
        '--ignore-gpu-blacklist',
        '--ignore-certificate-errors',
        '--metrics-recording-only',
        '--mute-audio',
        '--no-default-browser-check',
        '--no-first-run',
        '--no-pings',
        '--no-sandbox',
        '--no-zygote',
        '--password-store=basic',
        '--use-gl=swiftshader',
        '--use-mock-keychain',
        '--single-process',
        '--headless']

    # chrome_options.add_argument('--disable-gpu')
    for argument in lambda_options:
        chrome_options.add_argument(argument)
    return chrome_options


def send_message(text_body, cell_nums):

    for cell_num in cell_nums:
        _ = client.messages.create(
            body=text_body,
            from_='+447897037940',
            to=cell_num
        )
    return True


def main():
    driver = webdriver.Chrome(ChromeDriverManager(
    ).install(), options=__get_default_chrome_options())
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    driver.get("https://www.migrationsverket.se/ansokanbokning/omboka?enhet=UM&sprak=en&callback=http://www.swedenabroad.com/")

    # add input to the form
    input_field_1 = driver.find_element(By.ID, "bokningsnummer")
    input_field_1.send_keys('SHRB-1409')

    input_field_2 = driver.find_element(By.ID, "epost")
    input_field_2.send_keys('srsani@gmail.com')

    # click the next button
    next_button = driver.find_element_by_xpath('//input[@value="Next"]')
    next_button.click()

    # Locate the li element by class name
    feedback_elements = driver.find_elements_by_class_name(
        'feedbackPanelERROR')

    # Check if the expected message exists
    for element in feedback_elements:
        if "At the moment, there are no available time slots." in element.text:
            logger.info("no available time slots!")
            break
    else:
        logger.info("Feedback message not found.")

        _ = send_message(text_body=text_body,
                         cell_nums=[
                             '+447852255962'])


while True:
    try:
        now = datetime.datetime.now()

        # # Check if the current day is a weekday (0=Monday, 6=Sunday)
        # if 0 <= now.weekday() <= 4:
        # Check if the current time is between 8am to 8pm
        if 6 <= now.hour < 20:

            # Generate a random interval between 10 to 15 minutes (600 to 900 seconds)
            interval = random.randint(600, 900)
            logger.info(f"{now} - {interval}")
            # Wait for the interval
            time.sleep(interval)

            # Run the function
            # 26754
            main()

        else:
            # If it's past 8pm, sleep until 8am the next day
            # Calculate seconds until 8am the next day
            tomorrow = now + datetime.timedelta(days=1)
            eight_am_tomorrow = tomorrow.replace(
                hour=8, minute=0, second=0, microsecond=0)
            sleep_seconds = (eight_am_tomorrow - now).seconds
            time.sleep(sleep_seconds)

    except Exception as e:
        logger.info(f"An error occurred: {e}. Retrying...")
        time.sleep(random.randint(200, 400))
