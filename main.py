import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor

session = requests.Session()

data = []

special_characters = r'^[^?;:!.()]+'  

def from_other(url_new):
    try:
        book_url = f"https://books.toscrape.com/catalogue/{url_new}"
        response = session.get(book_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        stock = soup.find('th', string="Availability").find_next('td').text.strip()
        tax = soup.find('th', string="Tax").find_next('td').text.strip().replace('Â', '') 
        category = soup.find('ul', class_="breadcrumb").find_all('li')[2].text.strip()
        amount = re.findall(r'\d+', stock)
        return amount[0], tax, category
    except Exception as e:
        print(f"Error fetching details for book: {e}")
        return None, None, None


def scrape_book(book):
    try:
        a_tag = book.find('a', title=True)
        title = None
        if a_tag and 'title' in a_tag.attrs:
            title = re.match(special_characters, a_tag['title']).group(0)

        price = book.find('p', class_="price_color").text.strip().replace('Â', '')  
        stars = book.find('p', class_="star-rating")["class"][1]
        relative_url = book.h3.a['href']

        amount, tax, category = from_other(relative_url)

        if amount is None or tax is None or category is None:
            return None  

        rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}.get(stars, 0)

        return {
            'Title': title or 'Unknown',
            'Price': f'{price} +{tax}',
            'Rating': rating,
            'Amount': amount,
            'Category': category
        }

    except Exception as e:
        print(f"Error processing book: {e}")
        return None


url = 'https://books.toscrape.com/catalogue/page-1.html'


it_has_next_page = True


while it_has_next_page:
    try:

        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.findAll("article", class_="product_pod")
        pages = soup.find('li', class_="next")

        if pages:
            next_page_url = pages.find('a')['href']
            url = f'https://books.toscrape.com/catalogue/{next_page_url}' 
        else:
            it_has_next_page = False  

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(scrape_book, books))

        data.extend(filter(None, results))

    except Exception as e:
        print(f"Error fetching the page: {e}")
        it_has_next_page = False


df = pd.DataFrame(data)
print(df)
# df.to_csv('books_data.csv', index=False)

