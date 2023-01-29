from sys import stdout
from django.core.management import BaseCommand
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from time import sleep
from avito.models import Particulier, ParticulierProduit
from django.db import IntegrityError
from datetime import date
from re import search
from threading import Thread


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


class AvitoScrapper(Thread):

    def __init__(self, color):
        super().__init__()
        self.url = None
        self.color = color
        self.browser = None
        self.start_page = None
        self.end_page = None

    def setup(self):
        options = Options()
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.browser = Chrome(executable_path='/Users/youness/Documents/webdrivers/chromedriver',
                              options=options)
        self.browser.set_window_size(1000, 1400)
        # change this for every thread move the x by 500px (x, y) and leave the y at 0
        # self.url limit each thread by 30 pages
        if self.color == 0:
            x = 0
            self.url = 'https://www.avito.ma/fr/maroc/%C3%A0_vendre?o='
            self.start_page = 1
            self.end_page = 30
        elif self.color == 1:
            x = 500
            self.url = 'https://www.avito.ma/fr/maroc/%C3%A0_vendre?o='
            self.start_page = 31
            self.end_page = 60
        elif self.color == 2:
            x = 1000
            self.url = 'https://www.avito.ma/fr/maroc/%C3%A0_vendre?o='
            self.start_page = 61
            self.end_page = 90
        elif self.color == 3:
            x = 1500
            self.url = 'https://www.avito.ma/fr/maroc/%C3%A0_vendre?o='
            self.start_page = 91
            self.end_page = 120
        else:
            x = 2000
            self.url = 'https://www.avito.ma/fr/maroc/%C3%A0_vendre?o='
            self.start_page = 121
            self.end_page = 150
        self.browser.set_window_position(x, 0)

    def run(self):
        self.setup()
        self.pre_setup()
        self.get_avito_boutique_data()

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

    def get_avito_boutique_data(self):
        # Increment page number by 1 each time
        for i in range(self.start_page, self.end_page):
            url = self.url + str(i)
            self.browser.get(url)
            nbr_elements = self.browser.execute_script(
                "return document.querySelector('div.sc-1nre5ec-0.gYGzXe.listing')"
                ".querySelectorAll('div.oan6tk-0').length"
            )
            # Check if element is a store
            for element in range(nbr_elements):
                check_store = self.browser.execute_script(
                    "return document.querySelector('div.sc-1nre5ec-0.gYGzXe.listing')"
                    ".querySelectorAll('div.oan6tk-0')[" + str(element) + "].querySelector('div.sc-1xuksbu-0.jIQSll')"
                )
                # Skip stores
                if check_store is not None:
                    continue
                else:
                    particulier_output_dict = {
                        'name': None,
                        'phone': None,
                        'city': None,
                    }
                    particulier_product_output_dict = {
                        'id_particulier': None,
                        'url': None,
                        'title': None,
                        'category': None,
                        'price': 0,
                        'image_1': None,
                        'image_2': None,
                        'image_3': None,
                        'description': None,
                        'date_published': None,
                    }
                    # Navigate action (access store)
                    store_link = self.browser.execute_script(
                        "return document.querySelector('div.sc-1nre5ec-0.gYGzXe.listing')"
                        ".querySelectorAll('div.oan6tk-0')[" + str(
                            element) + "].querySelector('a.oan6tk-1.jkKPKg').href"
                    )
                    # Access details product
                    self.browser.get(store_link)
                    # URL
                    particulier_product_output_dict['url'] = self.browser.current_url
                    # Nom utilisateur
                    try:
                        name = self.browser.execute_script(
                            "return document.querySelector('span.sc-1x0vz2r-0.gcrouT.sc-1xrx1m6-8.gIZsec').textContent"
                        )
                        particulier_output_dict['name'] = name
                    except WebDriverException:
                        print('code#')
                        print(self.browser.current_url)
                        exit()
                    # City
                    city = self.browser.execute_script(
                        "return document.querySelector('span.sc-1x0vz2r-0.eOIPVs').textContent"
                    )
                    particulier_output_dict['city'] = city
                    # Title
                    title = self.browser.execute_script(
                        "return document.querySelector('h1.sc-1x0vz2r-0.cqjVAe').textContent"
                    )
                    particulier_product_output_dict['title'] = title
                    # Category
                    category = self.browser.execute_script(
                        "return document.querySelector('span.sc-1x0vz2r-0.dVPTCB').textContent"
                    )
                    particulier_product_output_dict['category'] = category
                    # Price
                    try:
                        price_content = self.browser.execute_script(
                            "return document.querySelector('p.sc-1x0vz2r-0.dUNDMm').textContent"
                        )
                        price = int(''.join(filter(str.isdigit, price_content)))
                        particulier_product_output_dict['price'] = price
                    except WebDriverException:
                        particulier_product_output_dict['price'] = 0
                    # Extract images
                    # Check numbers of available images
                    images = []
                    try:
                        available_images = self.browser.execute_script(
                            "return document.querySelectorAll('ul.slick-dots.slick-thumb')"
                            "[1].querySelectorAll('li').length"
                        )
                    except WebDriverException:
                        available_images = 0
                    if available_images == 0:
                        try:
                            images.append(self.browser.execute_script(
                                "return document.querySelector('img.sc-1gjavk-0.dcOYyv').src"
                            ))
                        except WebDriverException:
                            images.append(None)
                    else:
                        for image in range(available_images):
                            images.append(str(self.browser.execute_script(
                                "return document.querySelectorAll('ul.slick-dots.slick-thumb')[1]"
                                ".querySelectorAll('li')[" + str(image) + "].querySelector('img').src"
                            )).replace('thumbs', 'images'))
                            if len(images) == 3:
                                break
                    try:
                        particulier_product_output_dict['image_1'] = images[0]
                    except IndexError:
                        particulier_product_output_dict['image_1'] = None
                    try:
                        particulier_product_output_dict['image_2'] = images[1]
                    except IndexError:
                        particulier_product_output_dict['image_2'] = None
                    try:
                        particulier_product_output_dict['image_3'] = images[2]
                    except IndexError:
                        particulier_product_output_dict['image_3'] = None
                    # Click load more if exist (description)
                    try:
                        self.browser.execute_script(
                            "document.querySelector('button.sc-ij98yj-1.biVnBx').click()"
                        )
                    except WebDriverException:
                        pass
                    # Description
                    description = self.browser.execute_script(
                        "return document.querySelector('p.sc-ij98yj-0.ekgmnS').textContent"
                    )
                    particulier_product_output_dict['description'] = description
                    # Date_published
                    date_str = self.browser.execute_script(
                        "return document.querySelectorAll('span.sc-1x0vz2r-0.eOIPVs')[1].textContent"
                    )
                    if len(date_str) == 5:
                        date_value = date.today().strftime('%Y-%m-%d')
                    else:
                        date_value = self.date_parser(date_str)
                    particulier_product_output_dict['date_published'] = date_value
                    # Click show phone
                    try:
                        self.browser.execute_script(
                            "document.querySelector('button.uoqswv-0.uoqswv-1.uoqswv-2.jdNwiD.eGkOjT').click()"
                        )
                        sleep(1)
                        phone = self.browser.execute_script(
                            "return document.querySelector('span.sc-h6iqfz-3.fQNvjM span').textContent"
                        )
                        particulier_output_dict['phone'] = phone
                    except WebDriverException:
                        pass
                id_particulier = self.insert_particulier_output(particulier_output_dict)
                # ID particulier
                particulier_product_output_dict['id_particulier'] = id_particulier
                self.insert_particulier_products_output(particulier_product_output_dict)
                print(Styles.colors[self.color] + '=' * 87, '\033[0m')
                print(Styles.colors[self.color] + ' ' + str(particulier_output_dict) + ' ', '\033[0m')
                print(Styles.colors[self.color] + ' ' + str(particulier_product_output_dict) + ' ', '\033[0m')
                print(Styles.colors[self.color] + '=' * 87, '\033[0m')
                # Return to list
                self.browser.back()
                sleep(1)
        self.close_browser()

    @staticmethod
    def insert_particulier_output(particulier_output_dict):
        try:
            particulier = Particulier.objects.create(
                name=particulier_output_dict['name'],
                phone=particulier_output_dict['phone'],
                city=particulier_output_dict['city'],
            )
        except IntegrityError as ex:
            print(ex)
            particulier = Particulier.objects.get(phone=particulier_output_dict['phone'])
        return particulier.id

    @staticmethod
    def insert_particulier_products_output(particulier_produits_output_dict):
        try:
            ParticulierProduit.objects.create(
                particulier_id=particulier_produits_output_dict['id_particulier'],
                url=particulier_produits_output_dict['url'],
                title=particulier_produits_output_dict['title'],
                category=particulier_produits_output_dict['category'],
                price=particulier_produits_output_dict['price'],
                image_1=particulier_produits_output_dict['image_1'],
                image_2=particulier_produits_output_dict['image_2'],
                image_3=particulier_produits_output_dict['image_3'],
                description=particulier_produits_output_dict['description'],
                date_published=particulier_produits_output_dict['date_published'],
            )
        except IntegrityError as ex:
            print(ex)

    @staticmethod
    def month_str_to_date(month_str):
        return {
            'Janvier': '01',
            'Février': '02',
            'Mars': '03',
            'Avril': '04',
            'Mai': '05',
            'Juin': '06',
            'Juillet': '07',
            'Août': '08',
            'Septembre': '09',
            'Octobre': '10',
            'Novembre': '11',
            'Décembre': '12',
        }.get(month_str, '01')

    def date_parser(self, date_value):
        days = date_value[0:2]
        month_str = search(r"Janvier|Février|Mars|Avril|Mai|Juin|Juillet|Août|Septembre|Octobre|Novembre|Décembre",
                           date_value.strip()).group(0)
        month = self.month_str_to_date(month_str)
        return "{}-{}-{}".format(date.today().year, month, days)

    def close_browser(self):
        try:
            self.browser.close()
        except WebDriverException as e:
            print('Cannot close browser : {} '.format(e.msg))


class Command(BaseCommand):
    """
    Scrapping Avito data
    """

    help = 'Scrapping Avito data'

    def handle(self, *args, **options):
        stdout.write(f'Start processing Avito.\n')
        self.avito_scrapping()
        stdout.write('\n')

    @staticmethod
    def avito_scrapping():
        """
        avito_scrapping
        """
        bots = [AvitoScrapper(x) for x in range(0, 5)]
        for bot in bots:
            bot.start()
