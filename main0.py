import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor


def get_date(url):
    try:
        session = requests.Session()
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        dob = soup.find(class_='author-born-date').text.strip()
        return dob
    except Exception as e:
        print(f'Error With Getting Date: {e}')
        return None


def main_page(quote):
    try:
        cat = []  
        string = quote.find(class_='text').text.strip()
        author = quote.find(class_='author').text.strip()
        link = quote.find('a', href=True)['href'].lstrip('/')

        dob = get_date(f'https://quotes.toscrape.com/{link}')

        tags = quote.find_all('a', class_='tag')
        for tag in tags:
            category = tag.text.strip()
            cat.append(category)

        data.append({
            'string': string,
            'author': author,
            'tags': cat,
            'DOB': dob
        })
    except Exception as e:
        print(f"Error processing quote: {e}")


url = 'https://quotes.toscrape.com/'
session = requests.Session()
data = []

it_has_next_page = True

while it_has_next_page:
    try:
        print(f"Fetching page: {url}")
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        quotes = soup.findAll(class_='quote')

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(main_page, quotes)  

        next_button = soup.find('li', class_='next')
        if next_button:
            next_link = next_button.find('a', href=True)
            url = f'https://quotes.toscrape.com/{next_link["href"]}'
        else:
            it_has_next_page = False

    except Exception as e:
        print(f"Error fetching page: {e}")
        it_has_next_page = False  

df = pd.DataFrame(data)
df.to_json('quotes_data.json', orient='records', lines=True)

print("Data saved as quotes_data.json")