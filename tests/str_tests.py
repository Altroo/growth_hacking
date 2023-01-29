# from re import findall
# nbr_pages_str = """ 1-30 de 389 résultats résultat
#                                 | 1-13 pages"""
# nbr_page = int(nbr_pages_str.split(' | ')[1].split('-')[1].replace(' pages', ''))
# print(nbr_page)
# print(type(nbr_page))

# number_imgs = "de 16"
# number_imgs = int(str(number_imgs.replace('de ', '')))
# print(number_imgs)
# print(type(number_imgs))

# price_str = "1\xa0650\xa0000"
# price = str(price_str).replace('\xa0', '')
# print(int(price))

# price_str = "85 000 DH".replace(' ', '')
# price_str_2 = "0.0".replace(' ', '')
#
# price = findall(r'\d+', price_str)
# price_2 = findall(r'\d+', price_str_2)
# #
# #
# print(type(price))
# print(price)
# print(type(price_2))
# print(price_2)
# # import math
# #
# # number_of_ads = 10127
# # print(math.ceil(number_of_ads / 20))
# # print(number_of_ads / 20)
#
# url_str = 'https://www.marocannonces.com/categorie/15/Auto-Moto{}'
# url_str_2 = 'https://www.marocannonces.com/categorie/15/Auto-Moto{}'
#
# first_url = url_str.format('/1.html')
# next_url = url_str.format('/{}.html'.format('2'))
# print(first_url)
# print(next_url)

available_imgs = "1 / 6"
print(available_imgs[-1])
