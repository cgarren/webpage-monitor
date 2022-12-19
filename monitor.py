# imports
from datetime import datetime, timedelta, date
import time
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import smtplib as smtp
from email.message import EmailMessage
import json

# set the url
URL = "https://www.bestbuy.com/site/sony-wh-1000xm4-wireless-noise-cancelling-over-the-ear-headphones-black/6408356.p?skuId=6408356"

# set the fetching interval in seconds
INTERVAL = 10

# sends an email regardless of price change if set to True
TEST_EMAIL = True

# list of email addresses to send to
RECEIVING_ADDRESSES = ['']

# credentials file name
CREDENTIALS_FILE = 'credentials.json'

# name of Google sheet to write to
GOOGLE_SPREADSHEET_NAME = 'price_tracker'


def open_sheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(GOOGLE_SPREADSHEET_NAME).sheet1
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


def getProductTitleBestBuy(url):  # extract title for Best Buy page contents
    soup = extractPageData(url)
    title_div = soup.find("div", {"class": "sku-title"})
    title = ""
    for tag in title_div.contents:
        if 'class' in tag.attrs and "sr-only" in tag['class']:
            continue
        title = tag.get_text()
    return title


# send email with price and link to product when it changes
def sendEmail(product_name, product_price):
    connection = smtp.SMTP_SSL('smtp.gmail.com', 465)

    msg = EmailMessage()
    msg['Subject'] = 'Price change for ' + product_name
    msg.set_content('The price for ' + product_name +
                    ' has changed to ' + product_price + '!' + '\nLink: ' + URL)

    with open('credentials.json', 'r') as credentials_file:
        data = json.load(credentials_file)
        connection.login(data['sending_email'], data['sending_email_password'])
        connection.send_message(
            from_addr=data['sending_email'], to_addrs=RECEIVING_ADDRESSES, msg=msg)
    connection.close()


# Compare old and new prices to see if they are different
def didPriceChange(worksheet, current_product_price):
    max_row = len(worksheet.get_all_values())
    if worksheet.cell(max_row, 2).value != current_product_price:
        return True
    else:
        return False


# Update spreadsheet with new values
def updateSpreadsheet(worksheet, current_product_price, current_product_title, today, currentTime, url):
    previous_row = len(list(filter(None, worksheet.col_values(1))))
    max_row = len(worksheet.get_all_values())

    # Check if spreadsheet is empty
    if previous_row < max_row:
        worksheet.update_acell("A{}".format(
            previous_row), current_product_title)
        worksheet.update_acell("B{}".format(
            previous_row), current_product_price)
        worksheet.update_acell("C{}".format(previous_row), today)
        worksheet.update_acell("D{}".format(previous_row), currentTime)
        worksheet.update_acell("E{}".format(previous_row), url)
    else:
        data_line = [str(current_product_title), str(
            current_product_price), str(today), currentTime, url]
        worksheet.append_row(data_line)


def main():  # kickoff code
    current_product_title = getProductTitleBestBuy(URL)
    print("Product:", current_product_title)

    while True:
        # log the starting time
        past_time = datetime.now()
        now = datetime.now()
        today = date.today()
        currentTime = now.strftime("%H:%M:%S")

        worksheet = None  # set to None to force reload on first call

        current_product_price = checkPriceBestBuy(URL)

        print("Updated Price:", current_product_price,
              "at", currentTime, today)

        # Open Google Sheet
        worksheet = open_sheet()

        try:
            # Check if price has changed
            if didPriceChange(worksheet, current_product_price) or TEST_EMAIL:
                sendEmail(current_product_title, current_product_price)
                print("Email sent")
        except:
            print("Error sending email")

        try:
            # Update spreadsheet with new values
            updateSpreadsheet(worksheet, current_product_price,
                              current_product_title, today, currentTime, URL)
            print("Spreadsheet updated")
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
