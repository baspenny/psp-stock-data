import requests
from bs4 import BeautifulSoup
import pandas as pd
import pandas_gbq
from datetime import date

today = date.today()

from stock_markets import aex


# import ch
# import extra

def get_stock_listings_list(markets):
    stock_listings = []

    for market in markets:
        for stock_listing in market.stock_listings:
            stock_listings.append(stock_listing)

    return stock_listings


def get_data(stock_listings):
    stock_data = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"}

    dividend_amount_raw = 0
    dividend_amount = 0
    dividend_percentage = 0
    dividend_score = 0

    for stock_listing in stock_listings:
        print("Get data for:" + stock_listing.get("name"))

        price_score = 0

        price_page = requests.get(stock_listing.get("stock_price_url"), headers=headers)
        price_content = BeautifulSoup(price_page.content, "html.parser")

        # price_data_raw = price_content.find(id="consensusdetail")
        #     # .contents
        # price_current = round(float(str(price_data_raw[2].contents[0].contents[3].contents[1].contents[0].contents[
        #                                    0]).replace("\n", "").strip().replace(".","").replace(",",".")), 2)
        # price_target = round(float(str(price_data_raw[2].contents[0].contents[4].contents[1].contents[0].contents[
        #                                   0]).replace("\n", "").strip().replace(".","").replace(",",".")), 2)

        price_current = round(float(price_content.find(
            id="ctl00_ctl00_ctl00_ContentPlaceHolder1_LeftContent_Content_lblKoers"
               "").contents[0].replace("€\xa0", "").replace(",", "").replace(".", "")), 2) / 100

        if price_content.find(id="ctl00_ctl00_ctl00_ContentPlaceHolder1_LeftContent_Content_lblKoersDoel").contents:
            price_target = round(float(price_content.find(
                id="ctl00_ctl00_ctl00_ContentPlaceHolder1_LeftContent_Content_lblKoersDoel").contents[0].replace(
                "€\xa0", "").replace(",", "").replace(".", "")), 2) / 100
        else:
            price_target = price_current

        price_potential = round(((price_target / price_current) * 100) - 100, 2)

        if price_potential >= 40:
            price_score = 4
        elif price_potential >= 30 and price_potential < 40:
            price_score = 4
        elif price_potential >= 20 and price_potential < 30:
            price_score = 3
        elif price_potential >= 10 and price_potential < 20:
            price_score = 2
        elif price_potential >= 5 and price_potential < 10:
            price_score = 1
        elif price_potential < 0:
            price_score = -1

        if stock_listing.get("dividend_url") != 'n/a':
            dividend_page = requests.get(stock_listing.get("dividend_url"))
            dividend_content = BeautifulSoup(dividend_page.content, "html.parser")
            # .contents[2].contents[3]
            # if dividend_content.find(class_="payment-value").contents[0] != 'N/A':
            #     dividend_amount_raw = dividend_content.find(class_="payment-value").contents[0]
            # if dividend_content.find_all("span", {"class": "payment-value"}):

            if dividend_content.find_all("span", {"class": "payment-value"})[0].contents[0] != 'N/A':
                dividend_amount_raw = dividend_content.find_all("span", {"class": "payment-value"})[0].contents[0]
                dividend_amount = float(dividend_amount_raw.replace('€', '').replace('$', '').strip().replace('.',
                                                                                                              '').replace(
                    ',', '.'))
                dividend_percentage = round((dividend_amount / price_current) * 100, 2)

        if dividend_percentage >= 4:
            dividend_score = 5
        elif dividend_percentage >= 3 and dividend_percentage < 4:
            dividend_score = 4
        elif dividend_percentage >= 2 and dividend_percentage < 3:
            dividend_score = 3
        elif dividend_percentage >= 1 and dividend_percentage < 2:
            dividend_score = 2
        elif dividend_percentage > 0 and dividend_percentage < 1:
            dividend_score = 1

        total_score = price_score + dividend_score

        profit_potential_amount = round(float(price_target - price_current) + float(dividend_amount), 2)
        profit_potential_percentage = round((float(price_potential) + float(dividend_percentage)) / 100, 2)

        # Find different source
        sector = ""
        stock_market = ""
        if dividend_content.find(class_="tag-link"):
            sector = dividend_content.find(class_="tag-link").contents[0]
        if dividend_content.find(class_="category-link"):
            stock_market = dividend_content.find(class_="category-link").contents[0]

        stock_info = {
            "date": today,
            "stock_market": str(stock_market),
            "name": stock_listing.get("name"),
            "owned_amount": stock_listing.get("owned"),
            "current_price": price_current,
            "price_target": price_target,
            "price_potential": price_potential,
            "dividend": dividend_amount,
            "dividend_percentage": dividend_percentage,
            "price_score": price_score,
            "dividend_score": dividend_score,
            "total_score": total_score,
            "profit_potential_a": profit_potential_amount,
            "profit_potential_p": profit_potential_percentage,
            "sector": sector
        }

        # print(stock_info)
        stock_data.append(stock_info)

    return stock_data


def push_data(stock_data):
    stock_df = pd.DataFrame.from_dict(stock_data, orient='columns')
    pandas_gbq.to_gbq(
        stock_df,
        "stock_listings.scoring_overview",
        project_id="stock-intelligence-001",
        if_exists='append'
    )


if __name__ == '__main__':
    # request_json = request.get_json(silent=True)
    # markets = request_json['markets']

    markets = [aex]

    stock_listings = get_stock_listings_list(markets)
    stock_data = get_data(stock_listings)
    push_data(stock_data)

    print(stock_data)
