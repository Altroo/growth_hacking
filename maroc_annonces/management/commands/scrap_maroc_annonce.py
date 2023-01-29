from sys import stdout
from django.core.management import BaseCommand
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from time import sleep
from maroc_annonces.models import MarocAnnonce, MarocAnnonceProduit
from django.db import IntegrityError
from threading import Thread
from re import findall
from math import ceil
from io import BytesIO
import requests
from PIL import Image, ImageEnhance
from growth_hacking.settings import MEDIA_ROOT
from pytesseract import image_to_string


class Styles:
    colors = [
        '\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m',
        '\033[1;35m', '\033[1;36m', '\033[1;37m', '\033[90m', '\033[92m',
        '\033[1;41m', '\033[1;42m', '\033[1;43m', '\033[1;44m', '\033[1;45m',
        '\033[1;46m', '\033[1;47m', '\033[0;30;47m', '\033[0;31;47m', '\033[0;32;47m',
        '\033[0;33;47m', '\033[0;34;47m', '\033[0;35;47m', '\033[0;36;47m',
        # WHITE
        '\033[1;30m',
    ]


class MarocAnnoncesScrapper(Thread):

    def __init__(self, color):
        super().__init__()
        self.url = None
        self.browser = Chrome()
        self.category = None
        self.color = color

    def setup(self):
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.browser = Chrome(options=options)
        # change this for every thread move the x by 500px (x, y) and leave the y at 0
        # self.url limit each thread by 30 pages
        if self.color == 0:
            x = 0
            self.url = 'https://www.marocannonces.com/categorie/15/Auto-Moto{}'
            self.category = 'Auto - Moto'
        elif self.color == 1:
            x = 200
            self.url = 'https://www.marocannonces.com/categorie/16/Vente-immobilier{}'
            self.category = 'Vente immobilier'
        elif self.color == 2:
            x = 400
            self.url = 'https://www.marocannonces.com/categorie/305/Location-immobilier{}'
            self.category = 'Location immobilier'
        elif self.color == 3:
            x = 600
            self.url = 'https://www.marocannonces.com/categorie/307/Multi-Services{}'
            self.category = 'Multi services'
        elif self.color == 4:
            x = 800
            self.url = 'https://www.marocannonces.com/categorie/308/Ventes-diverses{}'
            self.category = 'Ventes diverses'
        elif self.color == 5:
            x = 1000
            self.url = 'https://www.marocannonces.com/categorie/306/Multim%C3%A9dia{}'
            self.category = 'Informatique & Multimédia'
        # Thread 7
        else:
            x = 1200
            self.url = 'https://www.marocannonces.com/categorie/362/Ventes-diverses/Animaux{}'
            self.category = 'Animaux'
        self.browser.set_window_position(x, 0)

    def run(self):
        self.setup()
        self.pre_setup()
        self.get_maroc_annonces_data()

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

    def get_maroc_annonces_data(self):
        self.browser.get(self.url.format('/1.html'))
        WebDriverWait(self.browser, 20).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'ul.cars-list'))
        )
        if self.color in [0, 1, 2, 3, 4, 5, 6]:
            number_of_ads = int(str(self.browser.execute_script(
                "return document.querySelector('div.results strong').textContent"
            )).replace(' ', ''))
        else:
            number_of_ads = int(str(self.browser.execute_script(
                "return document.querySelectorAll('div.results strong')[1].textContent"
            )).replace(' ', ''))
        nbr_pages = ceil(number_of_ads / 20)

        for i in range(nbr_pages):
            nbr_elements = self.browser.execute_script(
                "return document.querySelector('ul.cars-list').querySelectorAll('li:not(.adslistingpos)').length"
            )
            for element in range(nbr_elements):
                maroc_annonces_output_dict = {
                    'name': None,
                    'city': None,
                    'phone': None,
                }
                maroc_annonces_product_output_dict = {
                    'id_particulier': None,
                    'url': None,
                    'title': None,
                    'category': self.category,
                    'price': 0.0,
                    'image_1': None,
                    'image_2': None,
                    'image_3': None,
                    'description': None,
                }
                # - URL
                print(Styles.colors[self.color] + '=' * 87, '\033[0m')
                print(Styles.colors[self.color] + ' ' + str(element) + ' ', '\033[0m')
                print(Styles.colors[self.color] + '=' * 87, '\033[0m')
                url = str(self.browser.execute_script(
                    "return document.querySelector('ul.cars-list').querySelectorAll('li:not(.adslistingpos')["
                    + str(element) + "].querySelector('a').href"
                ))
                maroc_annonces_product_output_dict['url'] = url
                # Price
                try:
                    price_str = str(self.browser.execute_script(
                        "return document.querySelector('ul.cars-list').querySelectorAll"
                        "('li:not(.adslistingpos)')[" + str(element) + "].querySelector('strong.price')"
                                                                       ".textContent.trimStart().trimEnd()"
                    )).replace(' ', '')
                except WebDriverException:
                    price_str = "0.0"
                price_re = findall(r'\d+', price_str)
                maroc_annonces_product_output_dict['price'] = float(price_re[0])
                # City
                city = str(self.browser.execute_script(
                    "return document.querySelector('ul.cars-list').querySelectorAll('li:not(.adslistingpos)')[" + str(
                        element) + "].querySelector('span.location').textContent.trimStart().trimEnd()"
                ))
                maroc_annonces_output_dict['city'] = city
                # Title
                title = self.browser.execute_script(
                    "return document.querySelector('ul.cars-list').querySelectorAll('li:not(.adslistingpos)')[" + str(
                        element) + "].querySelector('h3').textContent.trimStart().trimEnd()"
                )
                maroc_annonces_product_output_dict['title'] = title
                # Access ad details (new tab)
                # Save current tab
                current_window = self.browser.current_window_handle
                sleep(2)
                # Open ad details in new tab
                self.browser.execute_script("window.open('{}')".format(str(url)))
                # Get new window/tab ID
                new_window = [window for window in self.browser.window_handles if window != current_window][0]
                # Switch to ad details new window/tab
                self.browser.switch_to.window(new_window)
                # Waiting new page to load
                WebDriverWait(self.browser, 20).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, 'ul.breadcrumbs'))
                )
                # Phone
                # - Click show phone number | Exception
                try:
                    phone_src = self.browser.execute_script(
                        "return document.querySelector('div#phone_number img').src"
                    )
                    response = requests.get(phone_src)
                    phone_img = Image.open(BytesIO(response.content))
                    self.process_image(phone_img)
                    phone_number = image_to_string(Image.open(MEDIA_ROOT + '/maroc_annonce/temp/tel0.jpg'),
                                                   config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789/',
                                                   lang='eng')
                    phone_number = phone_number.lstrip().rstrip()
                    maroc_annonces_output_dict['phone'] = phone_number
                except WebDriverException:
                    # close tab
                    self.browser.close()
                    # Switch to initial window/tab
                    self.browser.switch_to.window(current_window)
                    continue
                # Name
                name = self.browser.execute_script(
                    "return document.querySelector('div.infoannonce dl dd').textContent.trimStart().trimEnd()"
                )
                maroc_annonces_output_dict['name'] = name
                # Description
                description = str(self.browser.execute_script(
                    "return document.querySelector('div.parameter div.block').textContent.trimStart().trimEnd()"
                )).replace('Detail de l\'annonce : ', '')
                maroc_annonces_product_output_dict['description'] = description
                # Nbr_images
                try:
                    available_images = str(self.browser.execute_script(
                        "return document.querySelector('div.ad-controls p.ad-info').textContent.trimStart().trimEnd()"
                    ))
                    # "1 / 6"
                    available_images = int(available_images[-1])
                except WebDriverException:
                    available_images = 0
                # Extract Images
                # Check number of available images
                images = []
                if available_images == 0:
                    images.append(None)
                else:
                    for image in range(available_images):
                        images.append(self.browser.execute_script(
                            "return document.querySelector('div.ad-thumbs ul.ad-thumb-list').querySelectorAll('li')"
                            "[" + str(image) + "].querySelector('a').href"
                        ))
                        if len(images) == 3:
                            break
                try:
                    maroc_annonces_product_output_dict['image_1'] = images[0]
                except IndexError:
                    maroc_annonces_product_output_dict['image_1'] = None
                try:
                    maroc_annonces_product_output_dict['image_2'] = images[1]
                except IndexError:
                    maroc_annonces_product_output_dict['image_2'] = None
                try:
                    maroc_annonces_product_output_dict['image_3'] = images[2]
                except IndexError:
                    maroc_annonces_product_output_dict['image_3'] = None
                maroc_annonces_id = self.insert_maroc_annonce_output(maroc_annonces_output_dict)
                maroc_annonces_product_output_dict['id_particulier'] = maroc_annonces_id
                self.insert_maroc_annonces_products_output(maroc_annonces_product_output_dict)
                print(Styles.colors[self.color] + '=' * 87, '\033[0m')
                print(Styles.colors[self.color] + ' ' + str(maroc_annonces_output_dict) + ' ', '\033[0m')
                print(Styles.colors[self.color] + ' ' + str(maroc_annonces_product_output_dict) + ' ', '\033[0m')
                print(Styles.colors[self.color] + '=' * 87, '\033[0m')
                # close tab
                self.browser.close()
                # Switch to initial window/tab
                self.browser.switch_to.window(current_window)
                # Remove element from list
                # self.browser.execute_script(
                #    "document.querySelector('ul.cars-list')"
                #    ".querySelectorAll('li:not(.adslistingpos)')[0].outerHTML = ''"
                # )
                sleep(1)
            self.browser.get(self.url.format('/{}.html'.format(i + 2)))
        self.close_browser()

    @staticmethod
    def process_image(im):
        im.save(MEDIA_ROOT + '/maroc_annonce/temp/tel0.jpg')
        image = Image.open(MEDIA_ROOT + '/maroc_annonce/temp/tel0.jpg')
        image_enhanced = ImageEnhance.Sharpness(image).enhance(3)
        image_enhanced.save(MEDIA_ROOT + '/maroc_annonce/temp/tel0.jpg')

    @staticmethod
    def insert_maroc_annonce_output(mubawab_output_dict):
        try:
            boutique = MarocAnnonce.objects.create(
                name=mubawab_output_dict['name'],
                city=mubawab_output_dict['city'],
                phone=mubawab_output_dict['phone'],
            )
        except IntegrityError as ex:
            print(ex)
            boutique = MarocAnnonce.objects.get(phone=mubawab_output_dict['phone'])
        return boutique.id

    @staticmethod
    def insert_maroc_annonces_products_output(mubawab_produits_output_dict):
        try:
            MarocAnnonceProduit.objects.create(
                particulier_id=mubawab_produits_output_dict['id_particulier'],
                url=mubawab_produits_output_dict['url'],
                title=mubawab_produits_output_dict['title'],
                category=mubawab_produits_output_dict['category'],
                price=mubawab_produits_output_dict['price'],
                image_1=mubawab_produits_output_dict['image_1'],
                image_2=mubawab_produits_output_dict['image_2'],
                image_3=mubawab_produits_output_dict['image_3'],
                description=mubawab_produits_output_dict['description'],
            )
        except IntegrityError as ex:
            print(ex)

    def close_browser(self):
        try:
            self.browser.close()
        except WebDriverException as e:
            print('Cannot close browser : {} '.format(e.msg))


# 7 threads


class Command(BaseCommand):
    """
    Scrapping Maroc Annonces data
    """

    help = 'Scrapping Maroc Annonces data'

    def handle(self, *args, **options):
        stdout.write(f'Start processing Maroc Annonces.\n')
        self.maroc_annonces_scrapping()
        stdout.write('\n')

    @staticmethod
    def maroc_annonces_scrapping():
        """
        MarocAnnoncesScrapper
        """
        # 7 Threads
        bots = [MarocAnnoncesScrapper(x) for x in range(0, 7)]
        for bot in bots:
            bot.start()
