from sys import stdout
from django.core.management import BaseCommand
from selenium.webdriver import Chrome, ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from time import sleep
from mubawab.models import Mubawab, MubawabProduit
from django.db import IntegrityError
from threading import Thread
from lxml.html import fromstring
from re import findall


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


class MubawabScrapper(Thread):

    def __init__(self, color):
        super().__init__()
        self.url = None
        self.browser = Chrome()
        self.type_annonce = None
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
            self.url = 'https://www.mubawab.ma/fr/sc/appartements-a-vendre:o:n'
            self.type_annonce = 'Vente'
        elif self.color == 1:
            x = 500
            self.url = 'https://www.mubawab.ma/fr/cc/immobilier-a-louer-all:o:n'
            self.type_annonce = 'Location'
        elif self.color == 2:
            x = 1000
            self.url = 'https://www.mubawab.ma/fr/cc/immobilier-vacational:o:n'
            self.type_annonce = 'Location vacances'
        # Thread 4
        else:
            x = 1500
            self.url = 'https://www.mubawab.ma/fr/listing-promotion'
            self.type_annonce = 'Immobilier neuf'
        self.browser.set_window_position(x, 0)

    def run(self):
        self.setup()
        self.pre_setup()
        self.get_mubawab_data()

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

    def get_mubawab_data(self):
        self.browser.get(self.url)
        WebDriverWait(self.browser, 20).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'li.listingBox'))
        )
        nbr_pages_str = str(self.browser.execute_script(
            "return document.querySelector('p.fSize11').textContent.trimStart().trimEnd()"
        )).replace('\n', '').replace('\t', '')
        nbr_pages = int(nbr_pages_str.split('| ')[1].split('-')[1].replace(' pages', ''))
        for i in range(nbr_pages):
            # Remove map if "Immobilier neuf"
            if self.color == 3:
                self.browser.execute_script(
                    "document.querySelector('iframe#mapFrame').outerHTML = ''"
                )
            # body = WebDriverWait(self.browser, 20).until(
            #     ec.presence_of_element_located((By.TAG_NAME, 'body'))
            # )
            # body = self.browser.find_element(By.CSS_SELECTOR, 'div#listingCol')
            nbr_elements = self.browser.execute_script(
                "return document.querySelectorAll('li.listingBox').length"
            )
            none_clean_root = self.get_none_clean_html()

            for element in range(nbr_elements):
                mubawab_output_dict = {
                    'name': None,
                    'city': None,
                    'phone': None,
                }
                mubawab_product_output_dict = {
                    'id_particulier': None,
                    'url': None,
                    'title': None,
                    'type_annonce': self.type_annonce,
                    'category': None,
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
                # if self.color in [0, 1, 2]:
                # body.send_keys(Keys.PAGE_DOWN)
                #    url = self.browser.execute_script(
                #        "return document.querySelectorAll('li.listingBox')[" + str(
                #            element) + "].querySelector('h2 a').href"
                #    )
                # else:
                url = str(none_clean_root.xpath('//li[contains(@class,"listingBox")]/@linkref')[int(element)])
                mubawab_product_output_dict['url'] = url
                # Price
                if self.color in [0, 1, 2]:
                    # price_str = str(self.browser.execute_script(
                    #     "return document.querySelectorAll('li.listingBox')[" + str(
                    #         element) + "].querySelector('span.priceTag').textContent.trimStart().trimEnd()"
                    # ))
                    # if price_str == 'Prix à consulter':
                    #     price = 0.0
                    # else:
                    #     price = price_str.replace('DH', '')\
                    #         .replace('par jour', '')\
                    #         .replace('À partir de', '')\
                    #         .replace('\xa0', '')\
                    #         .replace('\n', '')\
                    #         .replace('\t', '')\
                    #         .replace(' ', '')
                    price_str = str(none_clean_root.xpath(
                        "//li[contains(@class, 'listingBox')][" + str(
                            int(element+1)) + "]//span[contains(@class, 'priceTag')]/text()"
                    )).replace(' ', '')
                else:
                    price_str = str(none_clean_root.xpath(
                        "//li[contains(@class, 'listingBox')][" + str(
                            int(element+1)) + "]//div[contains(@class, 'contentBox')]"
                        "/span[contains(@class, 'priceTag')]/text()")).replace(' ', '')
                price_re = findall(r'\d+', price_str)
                if len(price_re) == 0:
                    price = 0.0
                else:
                    price = price_re[0]
                mubawab_product_output_dict['price'] = price
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
                if self.color in [0, 1, 2]:
                    WebDriverWait(self.browser, 20).until(
                        ec.presence_of_element_located((By.CSS_SELECTOR, 'div.breadBlock.greyBlock'))
                    )
                else:
                    WebDriverWait(self.browser, 20).until(
                        ec.presence_of_element_located((By.CSS_SELECTOR, 'div.breadcrumb'))
                    )
                # Category
                if self.color in [0, 1, 2]:
                    category = str(self.browser.execute_script(
                        "return document.querySelector('div.breadBlock.greyBlock')"
                        ".querySelectorAll('a')[0].textContent.trimStart().trimEnd()"
                    )).replace(' Maroc', '')
                else:
                    category = str(self.browser.execute_script(
                        "return document.querySelector('div.breadcrumb')"
                        ".querySelectorAll('a')[0].textContent.trimStart().trimEnd()"
                    )).replace(' Maroc', '').rstrip()
                mubawab_product_output_dict['category'] = category
                # City
                if self.color in [0, 1, 2]:
                    city_str = str(self.browser.execute_script(
                        "return document.querySelector('div.breadBlock.greyBlock')"
                        ".querySelectorAll('a')[1].textContent.trimStart().trimEnd()"
                    )).replace('Immobilier ', '')
                else:
                    city_str = str(self.browser.execute_script(
                        "return document.querySelector('div.breadcrumb')"
                        ".querySelectorAll('a')[2].textContent.trimStart().trimEnd()"
                    )).replace('Immobilier neuf', '').lstrip().rstrip()
                mubawab_output_dict['city'] = city_str
                # Title
                title = self.browser.execute_script(
                    "return document.querySelector('h1').textContent.trimStart().trimEnd()"
                )
                mubawab_product_output_dict['title'] = title
                # Name
                if self.color in [0, 1, 2]:
                    try:
                        name = self.browser.execute_script(
                            "return document.querySelector('div.agency-info a').textContent.trimStart().trimEnd()"
                        )
                    except WebDriverException:
                        name = None
                else:
                    try:
                        name = self.browser.execute_script(
                            "return document.querySelector('div.agency-info img').alt.trimStart().trimEnd()"
                        )
                    except WebDriverException:
                        name = None
                mubawab_output_dict['name'] = name
                # Description
                if self.color in [0, 1, 2]:
                    description = self.browser.execute_script(
                        "return document.querySelector('div.blockProp p').textContent.trimStart().trimEnd()"
                    )
                else:
                    description = self.browser.execute_script(
                        "return document.querySelector('p.changeDescrip').textContent.trimStart().trimEnd()"
                    )
                mubawab_product_output_dict['description'] = description
                # Nbr_images
                try:
                    available_images = self.browser.execute_script(
                        "return document.querySelector('p.numSldr span').nextSibling.textContent.trimStart().trimEnd()"
                    )
                    available_images = int(str(available_images.replace('de ', '')))
                except WebDriverException:
                    available_images = 0
                # Extract Images
                # Check number of available images
                images = []
                if available_images == 0:
                    images.append(None)
                else:
                    self.browser.execute_script(
                        "document.querySelector('div#fullPicturesPopup').style.display = ''"
                    )
                    for image in range(available_images):
                        images.append(self.browser.execute_script(
                            "return document.querySelectorAll('div.item')"
                            "[" + str(int(image+1)) + "].querySelector('img').src"
                        ))
                        self.browser.execute_script(
                            "document.querySelector('div.thumbArrows.rightArrow').click()"
                        )
                        if len(images) == 3:
                            break
                    # Close images slider
                    self.browser.execute_script(
                        "document.querySelector('div.fancybox-close').click()"
                    )
                try:
                    mubawab_product_output_dict['image_1'] = images[0]
                except IndexError:
                    mubawab_product_output_dict['image_1'] = None
                try:
                    mubawab_product_output_dict['image_2'] = images[1]
                except IndexError:
                    mubawab_product_output_dict['image_2'] = None
                try:
                    mubawab_product_output_dict['image_3'] = images[2]
                except IndexError:
                    mubawab_product_output_dict['image_3'] = None
                # - Click show phone number | Exception
                try:
                    self.browser.execute_script(
                        "document.querySelector('div.hide-phone-number-box').click()"
                    )
                    phone = self.browser.execute_script(
                        "return document.querySelector('span#phoneBtnOpened')"
                        ".querySelector('p').textContent.trimStart().trimEnd()"
                    )
                except WebDriverException:
                    phone = None
                mubawab_output_dict['phone'] = str(phone).replace(' ', '')
                mubawab_id = self.insert_mubawab_output(mubawab_output_dict)
                mubawab_product_output_dict['id_particulier'] = mubawab_id
                self.insert_mubawab_products_output(mubawab_product_output_dict)
                print(Styles.colors[self.color] + '=' * 87, '\033[0m')
                print(Styles.colors[self.color] + ' ' + str(mubawab_output_dict) + ' ', '\033[0m')
                print(Styles.colors[self.color] + ' ' + str(mubawab_product_output_dict) + ' ', '\033[0m')
                print(Styles.colors[self.color] + '=' * 87, '\033[0m')
                # close tab
                self.browser.close()
                # Switch to initial window/tab
                self.browser.switch_to.window(current_window)
                # Remove element from list
                self.browser.execute_script(
                    "document.querySelectorAll('li.listingBox')[0].outerHTML = ''"
                )
                sleep(1)
            self.browser.get(self.url + ':p:{}'.format(int(i+2)))
        self.close_browser()

    def get_none_clean_html(self):
        root = self.browser.execute_script("return document.querySelector('body').innerHTML")
        none_clean_root = fromstring(str(root))
        return none_clean_root

    @staticmethod
    def insert_mubawab_output(mubawab_output_dict):
        try:
            boutique = Mubawab.objects.create(
                name=mubawab_output_dict['name'],
                city=mubawab_output_dict['city'],
                phone=mubawab_output_dict['phone'],
            )
        except IntegrityError as ex:
            print(ex)
            boutique = Mubawab.objects.get(phone=mubawab_output_dict['phone'])
        return boutique.id

    @staticmethod
    def insert_mubawab_products_output(mubawab_produits_output_dict):
        try:
            MubawabProduit.objects.create(
                particulier_id=mubawab_produits_output_dict['id_particulier'],
                url=mubawab_produits_output_dict['url'],
                title=mubawab_produits_output_dict['title'],
                type_annonce=mubawab_produits_output_dict['type_annonce'],
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

# 4 threads


class Command(BaseCommand):
    """
    Scrapping Mubawab data
    """

    help = 'Scrapping Mubawab data'

    def handle(self, *args, **options):
        stdout.write(f'Start processing Mubawab.\n')
        self.mubawab_scrapping()
        stdout.write('\n')

    @staticmethod
    def mubawab_scrapping():
        """
        MubawabScrapper
        """
        # 4 Threads
        bots = [MubawabScrapper(x) for x in range(0, 4)]
        for bot in bots:
            bot.start()
