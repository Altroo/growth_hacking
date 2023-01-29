from sys import stdout
from django.core.management import BaseCommand
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import requests
from io import BytesIO
from PIL import Image, ImageOps, ImageEnhance
from pytesseract import image_to_string
from avito.models import Boutique, Produit
from django.db import IntegrityError
from growth_hacking.settings import MEDIA_ROOT
from datetime import date, timedelta
from re import search
import subprocess
import pyautogui as pg


class WhatsAppMessageSender:

    def __init__(self, number, msg_type):
        self.url = 'https://web.whatsapp.com/send?phone={}'
        self.name = None
        self.browser = None
        self.number = number
        self.msg_type = msg_type

    def setup(self):
        options = Options()
        options.add_argument("user-data-dir=/Users/youness/Library/Application Support/Google/Chrome/Default/")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.browser = Chrome(executable_path='/Users/youness/Documents/webdrivers/chromedriver',
                              options=options)

    def run(self):
        self.setup()
        url = self.url.format(self.number)
        self.pre_setup()
        if self.msg_type == 'msg':
            # sleep(5)
            self.send_whatsapp_message(url)
        else:
            # sleep(5)
            self.send_whatsapp_image(url)

    def pre_setup(self):
        self.browser.execute_script(
            """
            if (window.trustedTypes && window.trustedTypes.createPolicy) {
              window.trustedTypes.createPolicy('default', {
                createHTML: (string, sink) => string
              });
            }
            """
        )

    def send_whatsapp_message(self, url):
        try:
            # message_box = WebDriverWait(self.browser, 20).until(
            #    ec.presence_of_element_located(
            #        (By.XPATH, "//div[@class='_13NKt copyable-text selectable-text'][1]")
            #    )
            # )
            # message_box = self.browser.find_element(By.TAG_NAME, 'body')
            # message_box.send_keys("Hello from whatsapp web!")
            url += '&text=HelloFromComputer'
            self.browser.get(url)
            # message_box = self.browser.find_element(By.TAG_NAME, 'body')
            # message_box.submit()
            # message_box.send_keys(Keys.ENTER)
            sleep(5)
            # Send message action
            self.browser.execute_script("document.querySelector('button._4sWnG').click()")
            sleep(100)
        except WebDriverException as err:
            print(err)

    def send_whatsapp_image(self, url):
        url += '&text=HelloFromComputerWithImage'
        self.browser.get(url)
        self.browser.maximize_window()
        sleep(10)

        # self.browser.execute_script("document.querySelector('div._1UWac._1LbR4').click()")
        self.browser.execute_script(
            "document.querySelector('div._1UWac._1LbR4').classList.add('focused')"
        )
        subprocess.run(["osascript", "-e", 'set the clipboard to (read (POSIX file "/Users/youness/Desktop/Guepard-300x266.jpg") as JPEG picture)'])
        width, height = pg.size()
        pg.click(width / 2, height / 2)
        sleep(20)
        # pg.hotkey("command", "v")
        pg.hotkey("command", "v", interval=0.25)
        sleep(10)
        pg.press('enter')
        # pg.hotkey("command", "r", interval=0.25)  # to refresh page
        # pg.hotkey("command", "t", interval=0.25)
        # self.browser.execute_script("document.querySelector('button._4sWnG').click()")
        sleep(100)


class Command(BaseCommand):
    """
    Scrapping Avito Boutique data
    """

    help = 'Sending WhatsApp messages'

    def handle(self, *args, **options):
        stdout.write(f'Start processing WhatsApp messages.\n')
        self.whatsapp_message_sending()
        stdout.write('\n')

    @staticmethod
    def whatsapp_message_sending():
        """
        whatsapp_message_sending
        """
        # msg_type = 'msg'
        msg_type = 'img'
        number = '+212662190660'
        # https://web.whatsapp.com/send?phone=+212662190660&text=HelloTesting
        whatsapp_sender = WhatsAppMessageSender(number, msg_type)
        whatsapp_sender.run()
        # print(MEDIA_ROOT)
