from re import search

link_str = "https://jiji.ng/ibadan/cars/honda-odyssey-2008-ex-l-gray-ynyul8riiGSTWS9j2MmPmlJc.html?cur_pos=7&pos=7&ads_count=169909&ads_per_page=20&page=1"
re_link_start = search('lid=', link_str)
re_link_end = search('cur_pos=', link_str)
print(link_str[re_link_start.start():re_link_end.start()])
# link = link_str.split('.html')[0]
# print(link)
