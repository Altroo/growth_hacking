from sys import stdout
from django.core.management import BaseCommand
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
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
from urllib.parse import urlparse, parse_qs


class AvitoBoutiqueScrapper:
    def __init__(self):
        self.url = 'https://www.avito.ma/fr/boutiques/maroc/'
        self.name = None
        self.browser = None

    def setup(self):
        options = Options()
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.browser = Chrome(executable_path='/Users/youness/Documents/webdrivers/chromedriver',
                              options=options)

    def run(self):
        self.setup()
        self.browser.get(self.url)
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
        # Pagination max page
        nbr_page = int(self.browser.execute_script(
            "return document.querySelector('div.pagination ul.d-flex').querySelectorAll('li a')[7].text"
        ))
        # Nomber of elements by page
        nbr_elements = self.browser.execute_script(
            "return document.querySelector('div.listing.listing-thumbs.panel-main')"
            ".querySelectorAll('div.item.li-hover').length"
        )
        for page in range(nbr_page):
            for element in range(nbr_elements):
                boutique_output_dict = {
                    'url': None,
                    'name': None,
                    'short_description': None,
                    'category': None,
                    'city': None,
                    'picture': None,
                    'address': None,
                    'phone': None,
                    'web_site': None,
                    'long_description': None,
                }
                # Name
                WebDriverWait(self.browser, 20).until(
                    ec.presence_of_element_located((By.ID, 'shop_link'))
                )
                name = self.browser.execute_script(
                    "return document.querySelector('div.listing.listing-thumbs.panel-main')"
                    ".querySelectorAll('div.item.li-hover')[" + str(
                        element) + "].querySelector('a#shop_link').textContent"
                )
                boutique_output_dict['name'] = name
                # Short description
                short_description = self.browser.execute_script(
                    "return document.querySelector('div.listing.listing-thumbs.panel-main')"
                    ".querySelectorAll('div.item.li-hover')[" + str(
                        element) + "].querySelector('div.clean_links.nohistory.fs12.wxxl').textContent"
                )
                boutique_output_dict['short_description'] = short_description
                # Category
                boutique_category = str(self.browser.execute_script(
                    "return document.querySelector('div.listing.listing-thumbs.panel-main')"
                    ".querySelectorAll('div.item.li-hover')[" + str(element) + "].querySelector('small').textContent"
                )).replace('\n', '')
                boutique_output_dict['category'] = boutique_category
                # City
                city = self.browser.execute_script(
                    "return document.querySelector('div.listing.listing-thumbs.panel-main')"
                    ".querySelectorAll('div.item.li-hover')[" + str(
                        element) + "].querySelectorAll('small')[1].textContent"
                )
                boutique_output_dict['city'] = city
                # img path
                try:
                    picture = self.browser.execute_script(
                        "return document.querySelector('div.listing.listing-thumbs.panel-main')"
                        ".querySelectorAll('div.image-and-nb.w140')[" + str(element) + "].querySelector('img').src"
                    )
                except WebDriverException:
                    picture = None
                boutique_output_dict['picture'] = picture
                # Navigate action (access store)
                store_link = self.browser.execute_script(
                    "return document.querySelector('div.listing.listing-thumbs.panel-main')"
                    ".querySelectorAll('div.item.li-hover')[" + str(element) + "].querySelector('a#shop_link').href"
                )
                # Access store details
                self.browser.get(store_link)
                # URL
                boutique_output_dict['url'] = self.browser.current_url
                # Address
                try:
                    address = str(self.browser.execute_script(
                        "return document.querySelector('div.mtl.mbs').textContent"
                    )).replace('Adresse', '').replace('\n', '')
                    boutique_output_dict['address'] = address
                except WebDriverException:
                    boutique_output_dict['address'] = None
                # Hover over phone element
                element = WebDriverWait(self.browser, 20).until(
                    ec.presence_of_element_located((By.ID, 'phonenum_footer_btn'))
                )
                # element_to_hover_over = self.browser.find_element(By.ID, 'phonenum_footer_btn')
                hover = ActionChains(self.browser).move_to_element(element)
                hover.perform()
                sleep(1)
                # Phone
                phone_url = self.browser.execute_script(
                    "return document.querySelector('img.AdPhonenum').src"
                )
                response = requests.get(phone_url)
                phone_img = Image.open(BytesIO(response.content))
                self.process_image(phone_img)
                phone_number = image_to_string(Image.open(MEDIA_ROOT + '/avito/temp/tel0.jpg'),
                                               config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789/',
                                               lang='eng')
                boutique_output_dict['phone'] = str(phone_number).replace('\n\x0c', '')
                # Website
                try:
                    web_site = self.browser.execute_script(
                        "return document.querySelector('a.visit-us').href"
                    )
                except WebDriverException:
                    web_site = None
                boutique_output_dict['web_site'] = web_site
                # Long description
                long_description = str(self.browser.execute_script(
                    "return document.querySelector('div.mlm').textContent"
                )).replace('\n', '')
                boutique_output_dict['long_description'] = long_description
                # print('*' * 100 + ' BOUTIQUE ' + '*' * 100)
                # print(boutique_output_dict)
                id_boutique = self.insert_boutique_output(boutique_output_dict)
                # Get products infos
                # Check if products exists
                first_time = True
                first_page_href_link = None
                while True:
                    if first_time:
                        first_page_href_link = self.browser.execute_script(
                            "return document.querySelector('div.pagination.text-center.mt-2')"
                            ".querySelectorAll('li')[0].querySelector('a').href"
                        )
                    else:
                        parsed_url = urlparse(first_page_href_link)
                        # query = {'ca': ['5', '5'], 'id': ['237', '237', '237'], 'o': ['1']}
                        query = parse_qs(parsed_url.query)
                        # Increment page from old page number
                        old_page_number = int(query['o'][0])
                        page_number = old_page_number + 1
                        # Construct new page url query
                        result_start = search('https', first_page_href_link)
                        result_end = search('&o=', first_page_href_link)
                        url_start = first_page_href_link[result_start.start():result_end.end()]
                        next_page_link = str(url_start) + str(page_number)
                        self.browser.get(next_page_link)
                        # Override first page link with next page link
                        first_page_href_link = next_page_link
                        sleep(2)
                    try:
                        products_length = self.browser.execute_script(
                            "return document.querySelector('div.listing.listing-thumbs')"
                            ".querySelectorAll('div.item.li-hover').length"
                        )
                    except WebDriverException:
                        products_length = 0
                    if products_length > 0:
                        clicked = 0
                        for i in range(products_length):
                            # with id boutique
                            product_output_dict = {'id_boutique': id_boutique, 'url': None, 'title': None,
                                                   'product_category': None, 'price': 0, 'image_1': None,
                                                   'image_2': None, 'image_3': None, 'product_description': None,
                                                   'date_published': None}
                            product = WebDriverWait(self.browser, 10).until(
                                ec.presence_of_element_located((By.CSS_SELECTOR, 'a.li-card'))
                            )
                            click_action = ActionChains(self.browser).move_to_element(product)
                            click_action.perform()
                            # Extract Date published
                            date_str = self.browser.execute_script(
                                "return document.querySelector('div.listing.listing-thumbs')"
                                ".querySelectorAll('div.item.li-hover')[" + str(
                                    i) + "].querySelector('span.age-text').textContent"
                            )
                            if "Aujourd'hui" in date_str:
                                date_value = date.today().strftime('%Y-%m-%d')
                            elif "Hier" in date_str:
                                date_value = date.today() - timedelta(days=1)
                            else:
                                date_value = self.date_parser(date_str[0:-6])
                            product_output_dict['date_published'] = date_value
                            # Clicked product item
                            self.browser.execute_script(
                                "document.querySelector('div.listing.listing-thumbs')"
                                ".querySelectorAll('div.item.li-hover')[" + str(
                                    i) + "].querySelector('a.li-card').click()"
                            )
                            # URL
                            product_output_dict['url'] = self.browser.current_url
                            # Explicit await
                            WebDriverWait(self.browser, 10).until(
                                ec.presence_of_element_located((By.TAG_NAME, 'h1'))
                            )
                            # Extract Title
                            title = self.browser.execute_script(
                                "return document.querySelector('h1').textContent"
                            )
                            product_output_dict['title'] = title
                            # Extract Category
                            product_category = self.browser.execute_script(
                                "return document.querySelector('span.dVPTCB').textContent"
                            )
                            product_output_dict['product_category'] = product_category
                            # Extract Price
                            try:
                                price = int(str(self.browser.execute_script(
                                    "return document.querySelector('p.dUNDMm').textContent"
                                )).replace('DH', '').replace('\u202f', ''))
                                product_output_dict['price'] = price
                            except WebDriverException:
                                product_output_dict['price'] = 0
                            # Extract Images
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
                            # Click load more if exist (description)
                            try:
                                self.browser.execute_script(
                                    "document.querySelector('button.sc-ij98yj-1.biVnBx').click()"
                                )
                            except WebDriverException:
                                pass
                            # Extract Description
                            product_description = self.browser.execute_script(
                                "return document.querySelector('p.sc-ij98yj-0.ekgmnS').textContent"
                            )
                            product_output_dict['product_description'] = product_description
                            # print('*' * 100 + ' PRODUITS BOUTIQUE ' + '*' * 100)
                            # print(product_output_dict)
                            self.insert_boutique_products_output(product_output_dict)
                            clicked += 1
                            # Back button
                            self.browser.back()
                            if clicked == 3:
                                break
                    first_time = False
                    # sleep(2)
                    # next_arrow = self.browser.execute_script(
                    #    "return document.querySelector('i.ri-arrow-right-s-line.pagination-arrows')"
                    # )
                    try:
                        WebDriverWait(self.browser, 20).until(
                            ec.presence_of_element_located((By.CSS_SELECTOR,
                                                            'i.ri-arrow-right-s-line.pagination-arrows'))
                        )
                    except TimeoutException:
                        break
                sleep(1)
                # Return to the main page
                self.browser.get(self.url)
                id_boutique += 1
                sleep(1)
            # https://www.avito.ma/fr/boutiques/maroc/?o=2
            self.browser.get('https://www.avito.ma/fr/boutiques/maroc/?o=' + str(page + 2))
        self.close_browser()

    @staticmethod
    def insert_boutique_output(boutique_output_dict):
        try:
            boutique = Boutique.objects.create(
                url=boutique_output_dict['url'],
                name=boutique_output_dict['name'],
                short_description=boutique_output_dict['short_description'],
                category=boutique_output_dict['category'],
                city=boutique_output_dict['city'],
                picture=boutique_output_dict['picture'],
                address=boutique_output_dict['address'],
                phone=boutique_output_dict['phone'],
                web_site=boutique_output_dict['web_site'],
                long_description=boutique_output_dict['long_description']
            )
        except IntegrityError as ex:
            print(ex)
            boutique = Boutique.objects.get(url=boutique_output_dict['url'])
        return boutique.id

    @staticmethod
    def insert_boutique_products_output(boutique_produits_output_dict):
        try:
            Produit.objects.create(
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

    @staticmethod
    def month_str_to_date(month_str):
        return {
            'Jan': '01',
            'Fév': '02',
            'Mar': '03',
            'Avr': '04',
            'Mai': '05',
            'Juin': '06',
            'Juil': '07',
            'Aoû': '08',
            'Sept': '09',
            'Oct': '10',
            'Nov': '11',
            'Déc': '12',
        }.get(month_str, '01')

    def date_parser(self, date_value):
        days = date_value[0:2]
        month_str = search(r"Jan|Fév|Mar|Avr|Mai|Juin|Juil|Aoû|Sept|Oct|Nov|Déc", date_value.strip()).group(0)
        month = self.month_str_to_date(month_str)
        return "{}-{}-{}".format(date.today().year, month, days)

    @staticmethod
    def process_image(im):
        i = 0
        mypalette = im.getpalette()
        try:
            while 1:
                im.putpalette(mypalette)
                new_im = Image.new("RGB", im.size)
                new_im.paste(im)
                new_im.save(MEDIA_ROOT + '/avito/temp/tel' + str(i) + '.jpg')
                i += 1
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        image = Image.open(MEDIA_ROOT + '/avito/temp/tel0.jpg')
        new_image = image.resize((200, 25))
        inverted = ImageOps.invert(new_image)
        inverted.save(MEDIA_ROOT + '/avito/temp/tel0.jpg')
        image = Image.open(MEDIA_ROOT + '/avito/temp/tel0.jpg')
        image_enhanced = ImageEnhance.Sharpness(image).enhance(3)
        image_enhanced.save(MEDIA_ROOT + '/avito/temp/tel0.jpg')
        ImageOps.expand(Image.open(MEDIA_ROOT + '/avito/temp/tel0.jpg'), border=300,
                        fill='black').save(MEDIA_ROOT + '/avito/temp/tel0.jpg')

    def close_browser(self):
        try:
            self.browser.close()
        except WebDriverException as e:
            print('Cannot close browser : {} '.format(e.msg))


class Command(BaseCommand):
    """
    Scrapping Avito Boutique data
    """

    help = 'Scrapping Avito Boutique data'

    def handle(self, *args, **options):
        stdout.write(f'Start processing Avito Boutique.\n')
        self.avito_boutique_scrapping()
        stdout.write('\n')

    @staticmethod
    def avito_boutique_scrapping():
        """
        avito_boutique_scrapping
        """
        avito_scrapper = AvitoBoutiqueScrapper()
        avito_scrapper.run()
