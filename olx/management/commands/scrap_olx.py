from sys import stdout
from django.core.management import BaseCommand
from selenium.webdriver import Chrome, Keys, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from time import sleep
from opensooq.models import OpenSooqParticulier, OpenSooqParticulierProduit
from django.db import IntegrityError
from datetime import date, timedelta


class OlxScrapper:

    def __init__(self):
        self.url = None
        self.browser = None
        self.start_page = None
        self.end_page = None

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
        self.get_olx_data()

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

    def get_olx_data(self):
        shops_url = "https://www.olx.co.za/"
        self.browser.get(shops_url)
        nbr_elements = self.browser.execute_script(
            "return document.querySelector('ul.rl3f9.AueO0').querySelectorAll('li[data-aut-id=itemBox]').length"
        )
        for element in range(nbr_elements):
            # body = self.browser.execute_script("return document.querySelector('body')")
            body = self.browser.find_element(By.TAG_NAME, 'body')
            # sleep(2)
            body.send_keys(Keys.PAGE_DOWN)
            # sleep(10)
            # body.send_keys(Keys.PAGE_DOWN)
            # sleep(1)
            # body.send_keys(Keys.PAGE_DOWN)
            # js click
            self.browser.execute_script("document.querySelector('button[data-aut-id=btnLoadMore]').click()")
            # # selenium click
            # load_more = WebDriverWait(self.browser, 20).until(
            #     ec.presence_of_element_located((By.CSS_SELECTOR, 'button[data-aut-id=btnLoadMore]'))
            # )
            # hover = ActionChains(self.browser).move_to_element(load_more)
            # hover.perform()
            # sleep(5)
            # hover.click()
            # sleep(2)
            # URL
            # document.querySelector('ul.rl3f9.AueO0').querySelectorAll('li[data-aut-id=itemBox]')[0].querySelector('a').href
            # Price => 'R 215,000' (Remove R & replace , with .)
            # document.querySelector('ul.rl3f9.AueO0').querySelectorAll('li[data-aut-id=itemBox]')[0].querySelector('span[data-aut-id=itemPrice]').textContent
            # Title
            # document.querySelector('ul.rl3f9.AueO0').querySelectorAll('li[data-aut-id=itemBox]')[0].querySelector('span[data-aut-id=itemTitle]').textContent
            # City => 'Johannesburg, Johannesburg' split by , & take the second
            # document.querySelector('ul.rl3f9.AueO0').querySelectorAll('li[data-aut-id=itemBox]')[0].querySelector('span[data-aut-id=item-location]').textContent
            # Date_published => 'Oct 06', 'Today', '2-7 days ago', '', '',
            # document.querySelector('ul.rl3f9.AueO0').querySelectorAll('li[data-aut-id=itemBox]')[0].querySelector('span.zLvFQ').textContent
            # Access url in a new tab
            # Switch to new tab
            #
        self.close_browser()

    @staticmethod
    def insert_olx_output(particulier_output_dict):
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
    def insert_olx_products_output(particulier_produits_output_dict):
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


# # save current tab
# current_window = self.browser.current_window_handle
# # open link in new tab
# self.browser.execute_script("window.open('https://www.google.com/')")
# # Get new window/tab ID
# new_window = [window for window in self.browser.window_handles if window != current_window][0]
# # Switch to new window/tab
# self.browser.switch_to.window(new_window)
# self.browser.get('https://www.google.com/')
# sleep(10)
# # close tab
# self.browser.close()
# # Switch to initial window/tab
# self.browser.switch_to.window(current_window)
# sleep(10)

class Command(BaseCommand):
    """
    Scrapping Olx data
    """

    help = 'Scrapping Olx data'

    def handle(self, *args, **options):
        stdout.write(f'Start processing Olx.\n')
        self.olx_scrapping()
        stdout.write('\n')

    @staticmethod
    def olx_scrapping():
        """
        olx_scrapping
        """
        bots = OlxScrapper()
        bots.run()
