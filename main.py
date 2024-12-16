import requests
from bs4 import BeautifulSoup
import pandas as pd
import re






data = []

special_characters = r'^[^?;:!.,()]+'

def from_other(url_new):
    try:
        book_url = f"https://books.toscrape.com/catalogue/{url_new}"
        response = requests.get(book_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        stock = soup.find('th', string="Availability").find_next('td').text.strip()
        tax = soup.find('th', string="Tax").find_next('td').text.strip().replace('Â', '') 
        review = soup.find('th', string="Number of reviews").find_next('td').text.strip().replace('Â', '') 
        category = soup.find('ul', class_="breadcrumb").find_next('li').find_next('li').find_next('li').text.strip()
        print(book_url)
        amount = re.findall(r'\d+', stock)
        return amount[0] , tax , review , category
    except Exception as e:
        print(f"Error fetching details for book: {e}")
        return None, None, None, None

it_has_next_page = True


new_url = "page-1.html"

while it_has_next_page:
    try:
        url = f"https://books.toscrape.com/catalogue/{new_url}"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.findAll("article", class_="product_pod")
        pages = soup.find('li', class_="next")

        for book in books:
            try:
                a_tag = book.find('a', title=True)
                title = None

                if a_tag and 'title' in a_tag.attrs:
                    title = re.match(special_characters, a_tag['title']).group(0)

                price = book.find('p', class_="price_color").text.strip().replace('Â', '')  
                stars = book.find('p', class_="star-rating")["class"][1]
                relative_url = book.h3.a['href']

                amount, tax, review, category = from_other(relative_url)

                if amount is None or tax is None or review is None or category is None:
                    continue
                match stars:
                    case "One":
                        rating = 1
                    case "Two":
                        rating = 2  
                    case "Three":
                        rating = 3
                    case "Four":
                        rating = 4
                    case "Five":
                        rating = 5

                data.append({
                    'Title': title or 'Unknown',
                    'Price': price,
                    'Rating': rating,
                    'Amount + Tax': f'{amount}+{tax}',
                    'Reviews': review,
                    'Category': category
                })
            except Exception as e:
                print(f"Error processing book: {e}")

        if pages:
            new_url = pages.find('a')['href']
        else:
            it_has_next_page = False
    except Exception as e:
        print(f"Error fetching page: {e}")
        it_has_next_page = False

df = pd.DataFrame(data)
print(df)
