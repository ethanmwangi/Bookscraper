import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import json

url = "https://books.toscrape.com/"

def getProducts():
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    products = []

    for book in soup.select('.product_pod')[:10]:
        title = book.h3.a['title']
        price = book.find('p', class_='price_color').text[1:]

        try:
            priceFloat = float(price)
        except:
            print(f"Could not convert price: {price}")
            priceFloat = 0.0

        products.append({'name': title, 'price': priceFloat})
    
    return products


def convertCurrency(amount):
    conversionRate = 175.50  
    return round(amount * conversionRate, 2)


def main():
    products = getProducts()

    for product in products:
        product['price_kes'] = convertCurrency(product['price'])

    with open('product.json', 'w') as jsonFile:
        json.dump(products, jsonFile, indent=4)

    tableData = [[product['name'], f"£{product['price']:.2f}", f"KSh {product['price_kes']:.2f}"] for product in products]
    headers = ["Product Name", "Price (GBP)", "Price (KES)"]
    print(tabulate(tableData, headers=headers, tablefmt='grid'))

main()