# imports
from datetime import datetime, timedelta
import time
import requests
from bs4 import BeautifulSoup

# set the url
URL = "https://www.bestbuy.com/site/sony-wh-1000xm4-wireless-noise-cancelling-over-the-ear-headphones-black/6408356.p?skuId=6408356"

# set the fetching interval in seconds
INTERVAL = 10


def extractPageData(url):  # get beutiful soup data from url
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"
    }
    page = requests.get(url, headers=headers)
    return BeautifulSoup(page.content, "html.parser")


def checkPriceBestBuy(url):  # extract price for Best Buy page contents
    soup = extractPageData(url)
    price_div = soup.find("div", {"class": "priceView-customer-price"})
    price = ""
    for tag in price_div.contents:
        if 'class' in tag.attrs and "sr-only" in tag['class']:
            continue
        price = tag.get_text()
    return price


def writeSoupToFile(soup):  # write page contents to file for data extraction or debugging
    with open("soup.html", "w") as file:
        file.write(str(soup))


def main():  # kickoff code
    while True:
        # log the starting time
        past_time = datetime.now()

        ### BUSINESS LOGIC HERE ###
        print("Updated Price:", checkPriceBestBuy(URL))

        # sleep for the interval
        time_delta = datetime.now() - past_time
        if time_delta < timedelta(seconds=INTERVAL):
            time.sleep(INTERVAL)
        else:
            sleep_time = (
                time_delta - timedelta(seconds=INTERVAL)).total_seconds()
            time.sleep(sleep_time)


if __name__ == "__main__":
    main()
