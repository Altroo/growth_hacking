from sys import stdout
from django.core.management import BaseCommand
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from time import sleep
from opensooq.models import OpenSooqBoutique, OpenSooqBoutiqueProduit
from django.db import IntegrityError
from datetime import date, timedelta


class OpenSooqShopScrapper:

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
        self.get_opensooq_shop_jordan_data()

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
            'jordan': 'jo',
            'oman': 'om',
        }.get(self.country, 'jo')

    def get_opensooq_shop_jordan_data(self):
        country_prefix_url = self.get_country_prefix_url()
        shops_url = "https://{}.opensooq.com/en/shops".format(country_prefix_url)
        self.browser.get(shops_url)
        # Remove top bar
        self.clean_top_bar()
        # Pagination max page
        nbr_page_str = self.browser.execute_script(
            "return document.querySelector('span.block.mt8').textContent"
        )
        nbr_page = self.get_nbr_page(nbr_page_str)
        # For each page in store pages
        for page in range(nbr_page):
            # Nomber of elements by page
            nbr_elements = self.browser.execute_script(
                "return document.querySelectorAll('a.p15.relative.borderBottom.block').length"
            )
            # For each store in one store page
            for element in range(nbr_elements):
                boutique_output_dict = {
                    'country': str(self.country).title(),
                    'url': None,
                    'name': None,
                    'category': None,
                    'city': None,
                    'picture': None,
                    'address': None,
                    'phone': None,
                    'description': None,
                }
                # Remove top bar
                self.clean_top_bar()
                # Waiting for page to load
                self.check_maintenance()
                self.check_forbidden()
                WebDriverWait(self.browser, 20).until(
                    ec.presence_of_element_located((By.ID, 'mainContent'))
                )
                # Name
                name = self.browser.execute_script(
                    "return document.querySelectorAll('a.p15.relative.borderBottom.block')[" + str(
                        element) + "].querySelector('h2').textContent"
                )
                boutique_output_dict['name'] = name
                # Category
                category = self.browser.execute_script(
                    "return document.querySelectorAll('a.p15.relative.borderBottom.block')[" + str(
                        element) + "].querySelector('img.vMiddle.inline.vMiddle.ml8').alt"
                )
                boutique_output_dict['category'] = category
                # City
                city = self.browser.execute_script(
                    "return document.querySelectorAll('a.p15.relative.borderBottom.block')[" + str(
                        element) + "].querySelector('span.inline.shopCity.osGray').textContent"
                )
                boutique_output_dict['city'] = city
                # Picture
                picture = self.browser.execute_script(
                    "return document.querySelectorAll('a.p15.relative.borderBottom.block')[" + str(
                        element) + "].querySelector('div.shopProfilePic.absolute.p5.osLightGrayBg img').src"
                )
                boutique_output_dict['picture'] = picture
                # Navigate action (access store)
                store_link = self.browser.execute_script(
                    "return document.querySelectorAll('a.p15.relative.borderBottom.block')[" + str(
                        element) + "].href"
                )
                sleep(2)
                # Access store details
                self.browser.get(store_link)
                # Remove top bar
                self.clean_top_bar()
                # URL
                boutique_output_dict['url'] = self.browser.current_url
                # Phone
                phone_str = self.browser.execute_script(
                    "return document.querySelector('a.block.blueBtn.p12').href"
                )
                phone = self.get_phone_number(phone_str)
                boutique_output_dict['phone'] = phone
                # Access Info tab
                self.browser.execute_script(
                    "document.querySelectorAll('div.p15.ripple')[3].click()"
                )
                # Waiting for page to load
                self.check_maintenance()
                self.check_forbidden()
                WebDriverWait(self.browser, 20).until(
                    ec.presence_of_element_located((By.TAG_NAME, 'address'))
                )
                # Remove top bar
                self.clean_top_bar()
                # Address
                address = self.browser.execute_script(
                    "return document.querySelector('address').textContent"
                )
                boutique_output_dict['address'] = address
                # Click load more (description)
                try:
                    self.browser.execute_script(
                        "document.querySelector('div.osBlue.mt8.font11').click()"
                    )
                except WebDriverException:
                    pass
                # Description
                try:
                    description = self.browser.execute_script(
                        "return document.querySelector('p.aboutShop').textContent"
                    )
                    boutique_output_dict['description'] = description
                except WebDriverException:
                    boutique_output_dict['description'] = None
                # Access Ads tab
                self.browser.execute_script(
                    "document.querySelectorAll('div.p15.ripple')[0].click()"
                )
                # Waiting for page to load
                self.check_maintenance()
                self.check_forbidden()
                WebDriverWait(self.browser, 20).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, 'span.block.mt8'))
                )
                # Remove top bar
                self.clean_top_bar()
                # Nomber of pages per store
                nbr_page_produit_str = self.browser.execute_script(
                    "return document.querySelector('span.block.mt8').textContent"
                )
                nbr_page_produit = self.get_nbr_page(nbr_page_produit_str)
                # Nomber of ads by page
                nbr_ads = self.browser.execute_script(
                    "return document.querySelectorAll('div.postListItem.relative.osWhiteBg.p8').length"
                )
                print('*' * 20)
                print(boutique_output_dict)
                print('*' * 20)
                id_boutique = self.insert_boutique_output(boutique_output_dict)
                # For each products page in the store
                for i in range(nbr_page_produit):
                    # For each ad in the store ads
                    for ad in range(nbr_ads):
                        # with id boutique
                        product_output_dict = {
                            'id_boutique': id_boutique,
                            'url': None,
                            'title': None,
                            'product_category': None,
                            'price': 0.0,
                            'image_1': None,
                            'image_2': None,
                            'image_3': None,
                            'product_description': None,
                            'date_published': None,
                        }
                        # Waiting page to load
                        self.check_maintenance()
                        self.check_forbidden()
                        WebDriverWait(self.browser, 20).until(
                            ec.presence_of_element_located((By.TAG_NAME, 'main'))
                        )
                        # Remove top bar
                        self.clean_top_bar()
                        # Ad URL
                        try:
                            url = self.browser.execute_script(
                                "return document.querySelectorAll('div.postListItem.relative.osWhiteBg.p8')[" + str(
                                    ad) + "].querySelector('a.flex.flexNoWrap.ripple.osBlack').href"
                            )
                            product_output_dict['url'] = url
                        except WebDriverException:
                            break
                        # Title
                        title = self.browser.execute_script(
                            "return document.querySelectorAll('div.postListItem.relative.osWhiteBg.p8')[" + str(
                                ad) + "].querySelector('h2').textContent"
                        )
                        product_output_dict['title'] = title
                        # Price
                        check_price_balise = self.browser.execute_script(
                            "return document.querySelectorAll('div.postListItem.relative.osWhiteBg.p8')[" + str(
                                ad) + "].querySelectorAll('span.bold').length"
                        )

                        if check_price_balise == 1:
                            price = str(self.browser.execute_script(
                                "return document.querySelectorAll('div.postListItem.relative.osWhiteBg.p8')[" + str(
                                    ad) + "].querySelector('span.bold').textContent"
                            )).replace(' ', '').replace(',', '')
                        else:
                            try:
                                price = str(self.browser.execute_script(
                                    "return document.querySelectorAll('div.postListItem.relative.osWhiteBg.p8')[" + str(
                                        ad) + "].querySelectorAll('span.bold')[1].textContent"
                                )).replace(' ', '').replace(',', '')
                            except WebDriverException:
                                price = 'Callforprice'
                        if price == 'Callforprice' or price == 'verified':
                            product_output_dict['price'] = 0.0
                        else:
                            product_output_dict['price'] = float(price)
                        # Number of images
                        available_images_str = self.browser.execute_script(
                            "return document.querySelectorAll('div.postListItem.relative.osWhiteBg.p8')[" + str(
                                ad) + "].querySelector('span.numOfCont').textContent"
                        )
                        available_images = self.get_available_imgs(available_images_str)
                        # Date_published
                        try:
                            date_published_str = self.browser.execute_script(
                                "return document.querySelectorAll('div.postListItem.relative.osWhiteBg.p8')[" + str(
                                    ad) + "].querySelector('span[data-ghost=SERP-Date]').textContent"
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
                        product_output_dict['date_published'] = date_value
                        # Access ad details
                        sleep(2)
                        self.browser.get(url)
                        # Waiting page to load
                        self.check_maintenance()
                        self.check_forbidden()
                        WebDriverWait(self.browser, 20).until(
                            ec.presence_of_element_located((By.TAG_NAME, 'main'))
                        )
                        # Remove top bar
                        self.clean_top_bar()
                        check_ad_not_exist = self.browser.execute_script(
                            "return document.querySelector('span.osRedBg')"
                        )
                        if check_ad_not_exist:
                            self.browser.back()
                            continue
                        # ad Category
                        ad_category = self.browser.execute_script(
                            "return document.querySelectorAll('a.osBlack.block')[2].text"
                        )
                        product_output_dict['product_category'] = ad_category
                        # Click load more (description)
                        try:
                            self.browser.execute_script(
                                "document.querySelector('a.showMore').click()"
                            )
                        except WebDriverException:
                            pass
                        # ad Description
                        ad_description = self.browser.execute_script(
                            "return document.querySelector('div.descCont.clear p').innerText"
                        )
                        product_output_dict['product_description'] = ad_description
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
                            product_output_dict['image_1'] = images[0]
                        except IndexError:
                            product_output_dict['image_1'] = None
                        try:
                            product_output_dict['image_2'] = images[1]
                        except IndexError:
                            product_output_dict['image_2'] = None
                        try:
                            product_output_dict['image_3'] = images[2]
                        except IndexError:
                            product_output_dict['image_3'] = None
                        print('*' * 20)
                        print(product_output_dict)
                        print('*' * 20)
                        self.insert_boutique_products_output(product_output_dict)
                        # Back is performed x2 (gallery page or no gallery)
                        self.browser.back()
                        sleep(2)
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
                        if nbr_page_produit + 1 == 1:
                            continue
                        else:
                            break
                # Access stores link
                page_url = '?page=' + str(page + 1)
                shops_url = shops_url + page_url
                sleep(2)
                self.browser.get(shops_url)
        #
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
    def get_available_imgs(available_images_str):
        return int(available_images_str.replace(' ', ''))

    @staticmethod
    def get_nbr_page(nbr_page_str):
        return int(nbr_page_str.replace(' ', '').split('of')[1])

    @staticmethod
    def get_phone_number(phone_str):
        return phone_str.replace('tel:', '')

    @staticmethod
    def insert_boutique_output(boutique_output_dict):
        try:
            boutique = OpenSooqBoutique.objects.create(
                country=boutique_output_dict['country'],
                url=boutique_output_dict['url'],
                name=boutique_output_dict['name'],
                category=boutique_output_dict['category'],
                city=boutique_output_dict['city'],
                picture=boutique_output_dict['picture'],
                address=boutique_output_dict['address'],
                phone=boutique_output_dict['phone'],
                description=boutique_output_dict['description']
            )
        except IntegrityError as ex:
            print(ex)
            boutique = OpenSooqBoutique.objects.get(url=boutique_output_dict['url'])
        return boutique.id

    @staticmethod
    def insert_boutique_products_output(boutique_produits_output_dict):
        try:
            OpenSooqBoutiqueProduit.objects.create(
                boutique_id=boutique_produits_output_dict['id_boutique'],
                url=boutique_produits_output_dict['url'],
                title=boutique_produits_output_dict['title'],
                category=boutique_produits_output_dict['product_category'],
                price=boutique_produits_output_dict['price'],
                image_1=boutique_produits_output_dict['image_1'],
                image_2=boutique_produits_output_dict['image_2'],
                image_3=boutique_produits_output_dict['image_3'],
                description=boutique_produits_output_dict['product_description'],
                date_published=boutique_produits_output_dict['date_published'],
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

    help = 'Scrapping OpenSooq Shops data'

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
        stdout.write('Start processing OpenSooq Shops {}.\n'.format(str(country[0]).title()))
        self.opensooq_shop_scrapping(country)
        stdout.write('\n')

    @staticmethod
    def opensooq_shop_scrapping(country):
        """
        opensooq_shop_scrapping
        """
        # TODO title needs to be get inside the page (3 dots in the shop list...)
        bots = OpenSooqShopScrapper(country)
        bots.run()
