import csv
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from pathlib import Path
from datetime import datetime
import time

# assume 2.5% property tax
# assume 1% PMI rate
# approximation for PMI assumes 88% of total value
# assume down payment is 5%


def calculate_intial_interest_payment(*, house_price, mortgage_rate, down_payment):
    """function to determine the total interest to be payed on the very first monthly payment"""
    if down_payment / house_price < 0.20:
        mortgage_rate += 0.01
    interest = (house_price - down_payment) * mortgage_rate
    return round(interest, 2)


def calculate_taxes(*, house_price, tax_rate):
    """function to calculate total yearly tax burden"""
    return round(tax_rate * house_price, 2)


def calculate_monthly_home_ownership_rent(*, interest, taxes):
    """function to calculate the total amount monthly rent paid for owning a home"""
    return round((interest + taxes)/12, 2)


def rent_cost_comparison(*, owner_rent, renter_rent):
    """function to compare the cost of ownership to cost of rent"""
    return round(owner_rent/renter_rent, 2)


def store_in_csv(*, file, data_tuple, mode):
    """ function to write all the data to a csv"""
    with open(file, mode, encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        if mode == 'w':
            headers = ('Date', 'City', 'Neighborhood', 'Average House Price',
                       'Average Rent Price', 'Morgtage Rate', 'Homeownership Rent', "Homeownership Rent/Average Rent Price")
            writer.writerow(headers)
        writer.writerow(data_tuple)


chrome_driver_path = "C:\development\chromedriver_win32\chromedriver.exe"

service = Service(chrome_driver_path)
op = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=op)

response = requests.get(
    "https://www.rentcafe.com/average-rent-market-trends/us/tx/austin/")

response_text = response.text

rent_soup = BeautifulSoup(response_text, "html.parser")

rents = rent_soup.find(
    id="MarketTrendsAverageRentTable").find_all(['td', 'th'])

target_hood = None
price = None
for item in rents:
    if target_hood:
        rent_price = int(item.text.strip("$").replace(",", ""))
        break
    if "Windsor Park" in item:
        target_hood = item
print(f"Rent for {target_hood.text} = {rent_price}")

driver.get(
    "https://www.freddiemac.com/pmms")

mortgage_rate_element = driver.find_element(
    By.CLASS_NAME, "mortgage-rate-widget__rate-value")

mortgage_rate = round(float(mortgage_rate_element.text.strip("%"))/100, 4)

driver.get(
    "https://www.realtor.com/realestateandhomes-search/Windsor-Park_Austin_TX/overview")

time.sleep(5)

house_price_element = driver.find_element(
    By.CLASS_NAME, "home-value-stat-value")

house_price = int(house_price_element.text.strip('$').strip('K')) * 1000

print(
    f"Average house price for {target_hood.text} = {house_price} and the mortgage rate is {mortgage_rate}")


initial_interest = calculate_intial_interest_payment(
    house_price=house_price, mortgage_rate=mortgage_rate, down_payment=(mortgage_rate * 0.1))

annual_taxes = calculate_taxes(house_price=house_price, tax_rate=0.025)

monthly_ownership_cost = calculate_monthly_home_ownership_rent(
    interest=initial_interest, taxes=annual_taxes)

cost_comparison = rent_cost_comparison(
    owner_rent=monthly_ownership_cost, renter_rent=rent_price)

data_tuple = datetime.now().strftime(
    '%m/%d/%Y'), "Austin", target_hood.text, house_price, rent_price, mortgage_rate, monthly_ownership_cost, cost_comparison

path_to_file = 'rent_data.csv'
path = Path(path_to_file)

if path.is_file():
    store_in_csv(file=path, data_tuple=data_tuple, mode='a')
else:
    store_in_csv(file=path, data_tuple=data_tuple, mode='w')
