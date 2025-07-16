import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def scrape_books(url="https://books.toscrape.com/catalogue/page-2.html"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.select(".product_pod")

        data = []
        for book in books[:10]:  # Limit to 10
            title = book.h3.a["title"]
            price_text = book.select_one(".price_color").text
            price_cleaned = price_text.replace("£", "").replace("Â", "").strip()
            price = float(price_cleaned)
            data.append({"title": title, "price_gbp": price})
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def convert_prices(data, from_currency="GBP", to_currency="KES"):
    try:
        response = requests.get(f"https://v6.exchangerate-api.com/v6/c31a21e4d24ea147df9d6594/pair/{from_currency}/{to_currency}")
        rate = response.json()["conversion_rate"]

        for item in data:
            item["price_converted"] = round(item["price_gbp"] * rate, 2)
        return data, rate
    except Exception as e:
        print(f"Currency conversion failed: {e}")
        return data, None
def display_table(data):
    df = pd.DataFrame(data)
    df = df.sort_values(by="price_converted", ascending=False)  # Sort by converted price, highest first
    print(df[["title", "price_gbp", "price_converted"]].to_markdown(index=False))

def save_data(data, format="csv"):
    df = pd.DataFrame(data)
    df = df.sort_values(by="price_converted", ascending=False)  # Sort before saving
    if format == "csv":
        df.to_csv("converted_prices.csv", index=False)
    elif format == "json":
        with open("converted_prices.json", "w") as f:
            json.dump(df.to_dict(orient="records"), f, indent=2)

def display_table(data):
    df = pd.DataFrame(data)
    print(df[["title", "price_gbp", "price_converted"]].to_markdown(index=False))

books = scrape_books()
converted_books, rate = convert_prices(books, "GBP", "KES")
if rate:
    print(f"Conversion Rate: 1 GBP = {rate} KES")
    display_table(converted_books)
    save_data(converted_books, format="csv")