import requests
from bs4 import BeautifulSoup

# URL = "https://www.bestbuy.com/site/bose-quietcomfort-45-wireless-noise-cancelling-over-the-ear-headphones-triple-black/6471291.p?skuId=6471291"
URL = "https://www.bestbuy.com/site/sony-wh-1000xm4-wireless-noise-cancelling-over-the-ear-headphones-black/6408356.p?skuId=6408356"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
price = soup.find("div", {"class": "priceView-customer-price"})
for tag in price.contents:
    if 'class' in tag.attrs and "sr-only" in tag['class']:
        continue
    print(tag.get_text())

# with open("bestbuy.html", "w") as file:
#     file.write(str(soup))
