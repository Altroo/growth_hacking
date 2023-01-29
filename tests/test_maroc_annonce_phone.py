from io import BytesIO

import requests
from PIL import Image, ImageEnhance
from growth_hacking.settings import MEDIA_ROOT
from pytesseract import image_to_string


def process_image(im):
    im.save(MEDIA_ROOT + '/maroc_annonce/temp/tel0.jpg')
    image = Image.open(MEDIA_ROOT + '/maroc_annonce/temp/tel0.jpg')
    image_enhanced = ImageEnhance.Sharpness(image).enhance(3)
    image_enhanced.save(MEDIA_ROOT + '/maroc_annonce/temp/tel0.jpg')


# 0704210687
# ImageOps = None, inverted = None
# response = requests.get("https://www.marocannonces.com/phone_number.php?phone=MDcwLTQyMS0wNjg3")

# 0672304822
# ImageOps = None/200, inverted = None
# response = requests.get("https://www.marocannonces.com/phone_number.php?phone=MDY3LTIzMC00ODIy")
# 2000
# response = requests.get("https://www.marocannonces.com/phone_number.php?phone=MjAwMA==")
# 0632905427
response = requests.get("https://www.marocannonces.com/phone_number.php?phone=MDYzLTI5MC01NDI3")
phone_img = Image.open(BytesIO(response.content))
process_image(phone_img)
phone_number = image_to_string(Image.open(MEDIA_ROOT + '/maroc_annonce/temp/tel0.jpg'),
                                               config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789/',
                                               lang='eng')
phone_number = phone_number.lstrip().rstrip()
print(phone_number)
print(len(phone_number))
