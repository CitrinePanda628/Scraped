import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

data = []

special_characters = r'^[^?;:!.,()]+'

def from_other(url_new):

    book_url = f"https://books.toscrape.com/{url_new}"
    response = requests.get(book_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(book_url)
    stock = soup.find('th', string="Availability").find_next('td').text.strip()
    tax = soup.find('th', string="Tax").find_next('td').text.strip().replace('Â', '') 
    review = soup.find('th', string="Number of reviews").find_next('td').text.strip().replace('Â', '') 
    category = soup.find('ul', class_="breadcrumb").find_next('li').find_next('li').find_next('li').text.strip()
    amount = re.findall(r'\d+', stock)

    return amount[0] , tax , review , category



it_has_next_page = True
url = "https://books.toscrape.com/"




response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
books = soup.findAll("article", class_="product_pod")
pages = soup.find('li', class_="next"  )
it_has_next_page = True

for book in books:

    page = pages.find('a')['href']
    title = re.match(r'^[^?;:!.,()]+', book.find('a', title=True).get('title')).group(0)
    # title = (book.h3.a["title"]).split(special_characters)[0]
    price = book.find('p', class_="price_color").text.strip().replace('Â', '')  
    stars = book.find('p', class_="star-rating")["class"][1]
    relative_url = book.h3.a['href']

    amount, tax, review, category  = from_other(relative_url)

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
        'Title': title,
        'Price': price,
        'Rating': rating,
        'Amount + Tax' : f'{amount}+{tax}',
        'Reviews' : review,
        'Category' : category
    })

    # if page != False:
            
    #     url = f"https://books.toscrape.com/{page}"
    # else:
    #     it_has_next_page = False






df = pd.DataFrame(data)

print(df)
