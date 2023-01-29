from sys import stdout
from django.core.management import BaseCommand
from selenium.webdriver import Chrome, Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from time import sleep
from jiji.models import Jiji, JijiProduit
from django.db import IntegrityError
from re import search


class JijiScrapper:

    def __init__(self, ghana):
        self.url = None
        self.browser = Chrome()
        self.start_page = None
        self.end_page = None
        self.ghana = ghana

    def setup(self):
        options = Options()
        options.add_argument("--user-data-dir=/Users/youness/Documents/webdrivers/Default/")
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.browser = Chrome(options=options)
        self.browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.browser.execute_cdp_cmd('Network.setUserAgentOverride',
                                     {"userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                   'Chrome/95.0.4638.54 Safari/537.36'}
                                     )

    def run(self):
        self.setup()
        self.pre_setup()
        # self.authenticate()
        self.get_jiji_data()

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

    def authenticate(self):
        login_url = 'https://jiji.{}/login.html'
        if self.ghana:
            self.browser.get(login_url.format('gh'))
        else:
            self.browser.get(login_url.format('ng'))
        # Waiting for button signin to show
        self.browser.execute_script(
            "document.querySelector('button.h-width-100p.h-bold').click()"
        )
        sleep(2)
        # signin_button = WebDriverWait(self.browser, 20).until(
        #     ec.presence_of_element_located((By.CSS_SELECTOR, 'button.h-width-100p.h-bold'))
        # )
        # hover = ActionChains(self.browser).move_to_element(signin_button)
        # hover.perform()
        # hover.click()
        print('Moved and clicked signin button')
        # Waiting for inputs to show
        # Email
        login_input = WebDriverWait(self.browser, 20).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'input.qa-login-field'))
        )
        login_input.send_keys("scorpion.yooy@gmail.com")
        # Password
        password_input = WebDriverWait(self.browser, 20).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'input.qa-password-field'))
        )
        password_input.send_keys("Altroo002")
        # Click login
        # login_button = WebDriverWait(self.browser, 20).until(
        #     ec.presence_of_element_located((By.CSS_SELECTOR, 'button.qa-login-submit'))
        # )
        # hover = ActionChains(self.browser).move_to_element(login_button)
        # hover.perform()
        # hover.click()
        self.browser.execute_script(
            "document.querySelector('button.qa-login-submit').click()"
        )
        sleep(3)

    def get_jiji_data(self):
        shop_urls = [
            "https://jiji.{}/vehicles",
            "https://jiji.{}/real-estate",
            "https://jiji.{}/mobile-phones-tablets",
            "https://jiji.{}/electronics",
            "https://jiji.{}/home-garden",
            "https://jiji.{}/health-and-beauty",
            "https://jiji.{}/fashion-and-beauty",
            "https://jiji.{}/hobbies-art-sport",
            "https://jiji.{}/seeking-work-cvs",
            "https://jiji.{}/services",
            "https://jiji.{}/jobs",
            "https://jiji.{}/babies-and-kids",
            "https://jiji.{}/animals-and-pets",
            "https://jiji.{}/agriculture-and-foodstuff",
            "https://jiji.{}/office-and-commercial-equipment-tools",
            "https://jiji.{}/repair-and-construction"
        ]
        for shop_url in shop_urls:
            if self.ghana:
                self.browser.get(shop_url.format('com.gh'))
            else:
                self.browser.get(shop_url.format('ng'))
            body = self.browser.find_element(By.TAG_NAME, 'body')
            WebDriverWait(self.browser, 20).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, 'div.b-advert-listing'))
            )
            while True:
                nbr_elements = self.browser.execute_script(
                    "return document.querySelector('div.b-advert-listing')"
                    ".querySelectorAll('div.b-list-advert__item-wrapper').length"
                )
                if nbr_elements == 0:
                    break
                for element in range(nbr_elements):
                    if element == 5:
                        body.send_keys(Keys.PAGE_DOWN)
                    jiji_output_dict = {
                        'name': None,
                        'phone': None,
                        'city': None,
                        'country': 'Ghana' if self.ghana else 'Nigeria'
                    }
                    jiji_product_output_dict = {
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
                    # First page
                    # - URL
                    url_str = self.browser.execute_script(
                        "return document.querySelector('div.b-advert-listing')"
                        ".querySelectorAll('div.b-list-advert__item-wrapper')[" + str(
                            element) + "].querySelector('a').href"
                    )
                    re_link_start = search('lid=', url_str)
                    re_link_end = search('cur_pos=', url_str)
                    param_to_remove = url_str[re_link_start.start():re_link_end.start()]
                    url = str(url_str).replace(param_to_remove, '')
                    jiji_product_output_dict['url'] = url
                    # Price
                    price_str = str(self.browser.execute_script(
                        "return document.querySelector('div.b-advert-listing')"
                        ".querySelectorAll('div.b-list-advert__item-wrapper')[" + str(
                            element) + "].querySelector('div.qa-advert-price').textContent.trimStart().trimEnd()"
                    ))
                    if price_str == 'Contact for price':
                        price = 0.0
                    else:
                        price = price_str.replace('₦ ', '').replace(',', '').replace('GH₵ ', '')
                    jiji_product_output_dict['price'] = price
                    # Title
                    title = self.browser.execute_script(
                        "return document.querySelector('div.b-advert-listing')"
                        ".querySelectorAll('div.b-list-advert__item-wrapper')[" + str(
                            element) + "].querySelector('h3').textContent.trimStart().trimEnd()"
                    )
                    jiji_product_output_dict['title'] = title
                    # City
                    city_str = str(self.browser.execute_script(
                        "return document.querySelector('div.b-advert-listing')"
                        ".querySelectorAll('div.b-list-advert__item-wrapper')[" + str(
                            element) + "].querySelector('span.b-list-advert__region__text')"
                                       ".textContent.trimStart().trimEnd()"
                    ))
                    city = city_str.split(',')[0]
                    jiji_output_dict['city'] = city
                    # Nbr_images
                    try:
                        available_images = int(self.browser.execute_script(
                            "return document.querySelector('div.b-advert-listing')"
                            ".querySelectorAll('div.b-list-advert__item-wrapper')"
                            "[" + str(element) + "].querySelector('span.b-list-advert__count-images')"
                                                 ".textContent.trimStart().trimEnd()"
                        ))
                    except WebDriverException:
                        available_images = 0
                    # Access ad details (new tab)
                    # Save current tab
                    current_window = self.browser.current_window_handle
                    sleep(2)
                    # Open ad details in new tab
                    self.browser.execute_script("window.open('{}')".format(str(url_str)))
                    # Get new window/tab ID
                    new_window = [window for window in self.browser.window_handles if window != current_window][0]
                    # Switch to ad details new window/tab
                    self.browser.switch_to.window(new_window)
                    # Waiting new page to load
                    WebDriverWait(self.browser, 20).until(
                        ec.presence_of_element_located((By.CSS_SELECTOR, 'ol.qa-bread-crumbs'))
                    )
                    # - Click show phone number | Exception
                    try:
                        self.browser.execute_script(
                            "document.querySelector('div.b-seller-info-wrapper')"
                            ".querySelector('a.b-show-contact').click()"
                        )
                        phone = self.browser.execute_script(
                            "return document.querySelector('div.b-seller-info-wrapper')"
                            ".querySelector('span.qa-show-contact-phone').textContent.trimStart().trimEnd()"
                        )
                    except WebDriverException:
                        phone = None
                    jiji_output_dict['phone'] = phone
                    # Description
                    description = self.browser.execute_script(
                        "return document.querySelector('span.qa-description-text').textContent.trimStart().trimEnd()"
                    )
                    jiji_product_output_dict['description'] = description
                    # Category
                    category = self.browser.execute_script(
                        "return document.querySelector('ol.qa-bread-crumbs').querySelectorAll('li')[1]"
                        ".textContent.trimStart().trimEnd()"
                    )
                    jiji_product_output_dict['category'] = category
                    # Name
                    name = self.browser.execute_script(
                        "return document.querySelector('div.b-seller-info-wrapper')"
                        ".querySelector('div.b-seller-block__name').textContent.trimStart().trimEnd()"
                    )
                    jiji_output_dict['name'] = name
                    # Date_published
                    # Taken care by the model
                    # Images x3
                    # Extract Images
                    # Check number of available images
                    images = []
                    if available_images == 0:
                        images.append(None)
                    else:
                        for image in range(available_images):
                            images.append(self.browser.execute_script(
                                "return document.querySelector('div.VueCarousel-wrapper')"
                                ".querySelectorAll('img')[" + str(image) + "].src"
                            ))
                            if len(images) == 3:
                                break
                    try:
                        jiji_product_output_dict['image_1'] = images[0]
                    except IndexError:
                        jiji_product_output_dict['image_1'] = None
                    try:
                        jiji_product_output_dict['image_2'] = images[1]
                    except IndexError:
                        jiji_product_output_dict['image_2'] = None
                    try:
                        jiji_product_output_dict['image_3'] = images[2]
                    except IndexError:
                        jiji_product_output_dict['image_3'] = None
                    jiji_id = self.insert_jiji_output(jiji_output_dict)
                    jiji_product_output_dict['id_particulier'] = jiji_id
                    self.insert_jiji_products_output(jiji_product_output_dict)
                    # close tab
                    self.browser.close()
                    # Switch to initial window/tab
                    self.browser.switch_to.window(current_window)
                    # Remove element from list
                    self.browser.execute_script(
                        "document.querySelector('div.b-advert-listing')"
                        ".querySelectorAll('div.b-list-advert__item-wrapper')[0].outerHTML = ''"
                    )
                    sleep(1)
        self.close_browser()

    @staticmethod
    def insert_jiji_output(jiji_output_dict):
        try:
            boutique = Jiji.objects.create(
                name=jiji_output_dict['name'],
                country=jiji_output_dict['country'],
                phone=jiji_output_dict['phone'],
                city=jiji_output_dict['city'],
            )
        except IntegrityError as ex:
            print(ex)
            boutique = Jiji.objects.get(phone=jiji_output_dict['phone'])
        return boutique.id

    @staticmethod
    def insert_jiji_products_output(jiji_produits_output_dict):
        try:
            JijiProduit.objects.create(
                particulier_id=jiji_produits_output_dict['id_particulier'],
                url=jiji_produits_output_dict['url'],
                title=jiji_produits_output_dict['title'],
                category=jiji_produits_output_dict['category'],
                price=jiji_produits_output_dict['price'],
                image_1=jiji_produits_output_dict['image_1'],
                image_2=jiji_produits_output_dict['image_2'],
                image_3=jiji_produits_output_dict['image_3'],
                description=jiji_produits_output_dict['description'],
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
    Scrapping Jiji data
    """

    help = 'Scrapping Jiji data'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('country', nargs='*', type=str)

        # Named (optional) arguments
        parser.add_argument(
            '--country',
            action='store_true',
            help='Scrap ghana country',
        )

    def handle(self, *args, **options):
        country = options['country']
        ghana = False
        try:
            if country[0] == 'ghana':
                ghana = True
        except IndexError:
            pass
        stdout.write(f'Start processing Jiji.\n')
        self.jiji_scrapping(ghana)
        stdout.write('\n')

    @staticmethod
    def jiji_scrapping(ghana):
        """
        jiji_scrapping
        """
        bots = JijiScrapper(ghana)
        bots.run()
