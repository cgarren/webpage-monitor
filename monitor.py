# imports
from datetime import datetime, timedelta, date
import time
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys

# set the url
URL = "https://www.bestbuy.com/site/sony-wh-1000xm4-wireless-noise-cancelling-over-the-ear-headphones-black/6408356.p?skuId=6408356"

# set the fetching interval in seconds
INTERVAL = 10


GOOGLE_OAUTH2_CREDENTIALS = 'credentials.json'
GOOGLE_SPREADSHEET_NAME = 'price_tracker'

def open_sheet(GOOGLE_OAUTH2_CREDENTIALS, GOOGLE_SPREADSHEET_NAME):
    try: 
        print('Logging into Google Sheet...')
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            GOOGLE_OAUTH2_CREDENTIALS, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(GOOGLE_SPREADSHEET_NAME).sheet1
        print('Login successful.')
        return worksheet
    except Exception as ex:
        print('Google sheet login failed with error:', ex)
        sys.exit(1)


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

def getProductTitle(url):
    soup = extractPageData(url)
    title_div = soup.find("div", {"class": "sku-title"})
    title = ""
    for tag in title_div.contents:
        if 'class' in tag.attrs and "sr-only" in tag['class']:
            continue
        title = tag.get_text()
    return title



def writeSoupToFile(soup):  # write page contents to file for data extraction or debugging
    with open("soup.html", "w") as file:
        file.write(str(soup))


def main():  # kickoff code
    while True:
        # log the starting time
        past_time = datetime.now()
        now = datetime.now()
        today = date.today()
        currentTime = now.strftime("%H:%M:%S")

        worksheet = None # set to None to force reload on first call
        ### BUSINESS LOGIC HERE ###
        print("Updated Price:", checkPriceBestBuy(URL), "Date", today, "Time", currentTime)
        print("Product Title:", getProductTitle(URL))

        # Open Google Sheet
        worksheet = open_sheet(GOOGLE_OAUTH2_CREDENTIALS, GOOGLE_SPREADSHEET_NAME)
        try:
            previous_row = len(list(filter(None , worksheet.col_values(1))))
            max_row = len(worksheet.get_all_values())
            if previous_row < max_row:
                worksheet.update_acell("A{}".format(previous_row), checkPriceBestBuy(URL))
                worksheet.update_acell("B{}".format(previous_row), today)
                worksheet.update_acell("C{}".format(previous_row), currentTime)
            else:
                data_line = [str(checkPriceBestBuy(URL)), str(today), currentTime]
                worksheet.append_row(data_line)
                print("appended row")
        except:
            print("Error writing to Google Sheet")
            worksheet = None

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