from sys import stdout
from django.core.management import BaseCommand
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from time import sleep
from opensooq.models import OpenSooqParticulier, OpenSooqParticulierProduit
from django.db import IntegrityError
from datetime import date, timedelta


class OpenSooqScrapper:

    def __init__(self, country):
        self.url = None
        self.browser = None
        self.start_page = None
        self.end_page = None
        self.country = country[0]

    def setup(self):
        options = Options()
        options.add_argument("--disable-infobars")
        mobile_emulation = {"deviceName": "iPad Pro"}
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        self.browser = Chrome(executable_path='/Users/youness/Documents/webdrivers/chromedriver',
                              options=options)
        self.browser.set_window_size(1100, 1400)

    def run(self):
        self.setup()
        self.pre_setup()
        self.get_opensooq_particulier_data()

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

    def get_country_prefix_url(self):
        return {
            'saudi arabia': 'sa',
            'UAE': 'ae',
            'egypt': 'eg',
            'bahrain': 'bh',
            'qatar': 'qa',
            'koweit': 'kw',
            'jordan': 'jo',
            'oman': 'om',
        }.get(self.country, 'jo')

    def get_opensooq_particulier_data(self):
        country_prefix_url = self.get_country_prefix_url()
        shops_url = "https://{}.opensooq.com/en/find?have_images=&allposts=&onlyPremiumAds=&onlyDonation=&" \
                    "onlyPrice=&onlyUrgent=&onlyShops=&onlyMemberships=&onlyBuynow=&memberId=&" \
                    "sort=record_posted_date.desc&term=&cat_id=&scid=&city=".format(country_prefix_url)
        self.browser.get(shops_url)
        # Remove top bar
        self.clean_top_bar()
        # Pagination max page
        nbr_page_str = self.browser.execute_script(
            "return document.querySelector('span.block.mt8').textContent"
        )
        nbr_page = self.get_nbr_page(nbr_page_str)
        # For each page in particulier pages
        for page in range(nbr_page):
            # Nomber of elements by page
            nbr_elements = self.browser.execute_script(
                "return document.querySelector('div.items').querySelectorAll('div.postListItem').length"
            )
            # For each ad in one particulier page
            for element in range(nbr_elements):
                particulier_output_dict = {
                    'country': str(self.country).title(),
                    'name': None,
                    'phone': None,
                    'city': None,
                }
                particulier_product_output_dict = {
                    'id_particulier': None,
                    'url': None,
                    'title': None,
                    'category': None,
                    'price': 0.0,
                    'image_1': None,
                    'image_2': None,
                    'image_3': None,
                    'description': None,
                    'date_published': None,
                }
                # Remove top bar
                self.clean_top_bar()
                # Waiting for page to load
                self.check_maintenance()
                self.check_forbidden()
                WebDriverWait(self.browser, 20).until(
                    ec.presence_of_element_located((By.ID, 'mainContent'))
                )
                check_if_store = self.browser.execute_script(
                    "return document.querySelector('div.items').querySelectorAll('div.postListItem')[" + str(
                        element) + "].querySelector('svg[data-name=IconShop]')"
                )
                if check_if_store:
                    continue
                # Category
                city_and_category_str = self.browser.execute_script(
                    "return document.querySelectorAll('div.cpValues.overflowHidden')[" + str(
                        element) + "].textContent.trimStart().trimEnd()"
                )
                city, category = self.get_city_and_category(city_and_category_str)
                particulier_output_dict['city'] = city
                particulier_product_output_dict['category'] = category
                # Number of images
                available_images_str = self.browser.execute_script(
                    "return document.querySelectorAll('div.postListItem.relative.osWhiteBg.p8')[" + str(
                        element) + "].querySelector('span.numOfCont').textContent")
                available_images = self.get_available_imgs(available_images_str)
                # Date_published
                try:
                    date_published_str = self.browser.execute_script(
                        "return document.querySelectorAll('div.customCont')[" + str(
                            element) + "].querySelector('span[data-ghost=SERP-Date]').textContent"
                    )
                except WebDriverException:
                    date_published_str = "ago"
                if "ago" in date_published_str:
                    date_value = date.today().strftime('%Y-%m-%d')
                elif "yesterday" in date_published_str:
                    date_value = date.today() - timedelta(days=1)
                else:
                    date_formated = date_published_str.split('-')
                    date_value = '{}-{}-{}'.format(date_formated[2], date_formated[1], date_formated[0])
                particulier_product_output_dict['date_published'] = date_value
                # Phone
                # Click show phone
                self.browser.execute_script(
                    "document.querySelectorAll('div.postListItem.relative')[" + str(
                        element) + "].querySelector('a.callButton').click()"
                )
                sleep(2)
                phone = self.browser.execute_script(
                    "return document.querySelectorAll('div.postListItem.relative')[" + str(
                        element) + "].querySelector('a.callButton').textContent.trimStart().trimEnd()"
                )
                particulier_output_dict['phone'] = phone
                # Access ad details page
                ad_link = self.browser.execute_script(
                    "return document.querySelector('div.items').querySelectorAll('div.postListItem')[" + str(
                        element) + "].querySelector('a').href"
                )
                # Access store details
                self.browser.get(ad_link)
                sleep(2)
                # Remove top bar
                self.check_maintenance()
                self.check_forbidden()
                self.clean_top_bar()
                # Name
                user_name = self.browser.execute_script(
                    "return document.querySelector('a.userCardDet').textContent.trimStart().trimEnd()"
                )
                particulier_output_dict['name'] = user_name
                id_particulier = self.insert_particulier_output(particulier_output_dict)
                particulier_product_output_dict['id_particulier'] = id_particulier
                # URL
                particulier_product_output_dict['url'] = self.browser.current_url
                # Title
                title = self.browser.execute_script(
                    "return document.querySelector('h1').textContent"
                )
                particulier_product_output_dict['title'] = title
                # Price
                currency = False
                try:
                    currency = self.browser.execute_script(
                        "return document.querySelector('div.postViewPrice').firstElementChild"
                        ".textContent.trimStart().trimEnd()"
                    )
                except WebDriverException:
                    particulier_product_output_dict['price'] = 0.0
                if currency:
                    price_value = self.browser.execute_script(
                        "return document.querySelector('div.postViewPrice').textContent.trimStart().trimEnd()"
                    )
                    price = float(str(price_value).replace(str(currency), '').replace(' ', '').replace(',', '.'))
                    particulier_product_output_dict['price'] = price
                # Click load more (description)
                try:
                    self.browser.execute_script(
                        "document.querySelector('a.showMore').click()"
                    )
                except WebDriverException:
                    pass
                # Description
                try:
                    description = self.browser.execute_script(
                        "return document.querySelector('div.descCont.clear').textContent.trimStart().trimEnd()"
                    )
                    particulier_product_output_dict['description'] = description
                except WebDriverException:
                    particulier_product_output_dict['description'] = None
                # Extract Images
                # Check number of available images
                images = []
                if available_images == 0:
                    images.append(None)
                else:
                    # Access images page
                    self.browser.execute_script(
                        "document.querySelector('a.allImages').click()"
                    )
                    # Waiting page to load
                    self.check_maintenance()
                    self.check_forbidden()
                    WebDriverWait(self.browser, 20).until(
                        ec.presence_of_element_located((By.TAG_NAME, 'main'))
                    )
                    for image in range(available_images):
                        images.append(self.browser.execute_script(
                            "return document.querySelectorAll('img.imageGallery')[" + str(image) + "].src"
                        ))
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

                print('*' * 20)
                print(particulier_product_output_dict)
                print('*' * 20)
                self.insert_particulier_products_output(particulier_product_output_dict)
                # Back is performed x2 (gallery page or no gallery)
                self.browser.back()
                sleep(2)
                self.browser.back()
                # sleep(2)
                # self.browser.back()
                # sleep(2)
            # Check if next page button exist
            next_page = self.browser.execute_script(
                "return document.querySelector('a.nextPager:not(.hide)')"
            )
            if next_page:
                # Access next page
                self.browser.execute_script(
                    "document.querySelector('a.nextPager').click()"
                )
            else:
                break
            # Access stores link
            page_url = '?page=' + str(page + 1)
            shops_url = shops_url + page_url
            sleep(2)
            self.browser.get(shops_url)
        self.close_browser()

    def clean_top_bar(self):
        try:
            self.browser.execute_script(
                "document.querySelector('section#splash').outerHTML = ''"
            )
        except WebDriverException:
            pass
        try:
            self.browser.execute_script(
                "document.querySelector('span.block.p15.osWhite.font12').click()"
            )
        except WebDriverException:
            pass

    def check_maintenance(self):
        while True:
            maintenance = self.browser.execute_script(
                "return document.querySelector('img.maintenanceImg')"
            )
            if maintenance:
                sleep(2)
                self.browser.refresh()
            else:
                break

    def check_forbidden(self):
        while True:
            try:
                forbidden = self.browser.execute_script(
                    "return document.querySelector('center h1').textContent"
                )
                if forbidden == '403 Forbidden':
                    sleep(2)
                    self.browser.refresh()
                else:
                    break
            except WebDriverException:
                break

    @staticmethod
    def get_city_and_category(city_and_category_str):
        city_and_category_str = str(city_and_category_str).split('|')
        city = str(city_and_category_str[0]).lstrip().rstrip()
        category = str(city_and_category_str[1]).lstrip().rstrip()
        return city, category

    @staticmethod
    def get_available_imgs(available_images_str):
        return int(available_images_str.replace(' ', ''))

    @staticmethod
    def get_nbr_page(nbr_page_str):
        return int(nbr_page_str.replace(' ', '').replace(' ', '').split('of')[1])

    @staticmethod
    def insert_particulier_output(particulier_output_dict):
        try:
            boutique = OpenSooqParticulier.objects.create(
                country=particulier_output_dict['country'],
                name=particulier_output_dict['name'],
                phone=particulier_output_dict['phone'],
                city=particulier_output_dict['city'],
            )
        except IntegrityError as ex:
            print(ex)
            boutique = OpenSooqParticulier.objects.get(phone=particulier_output_dict['phone'])
        return boutique.id

    @staticmethod
    def insert_particulier_products_output(particulier_produits_output_dict):
        try:
            OpenSooqParticulierProduit.objects.create(
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

    def close_browser(self):
        try:
            self.browser.close()
        except WebDriverException as e:
            print('Cannot close browser : {} '.format(e.msg))


class Command(BaseCommand):
    """
    Scrapping OpenSooq data
    """

    help = 'Scrapping OpenSooq data'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('country', nargs='+', type=str)

        # Named (optional) arguments
        parser.add_argument(
            '--country',
            action='store_true',
            help='Add which country to scrap',
        )

    def handle(self, *args, **options):
        country = options['country']
        stdout.write('Start processing OpenSooq {}.\n'.format(str(country[0]).title()))
        self.opensooq_scrapping(country)
        stdout.write('\n')

    @staticmethod
    def opensooq_scrapping(country):
        """
        opensooq_scrapping
        """
        bots = OpenSooqScrapper(country)
        bots.run()
