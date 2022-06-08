import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import os

url = 'https://books.toscrape.com/'
response = requests.get(url)

contents = response.text

with open('Bookswebpage.html', 'w') as f:
    f.write(contents)

doc = BeautifulSoup(contents, 'html.parser')

def get_book_titles(doc):
    Book_title_tags = doc.find_all('h3')
    Book_titles = []
    for tags in Book_title_tags:
        Book_titles.append(tags.text)
    return (Book_title_tags, Book_titles)

title_tags, book_titles = get_book_titles(doc)


def get_book_price(doc):
    Book_price_tags = doc.find_all('p', class_='price_color')
    Book_price = []
    for tags in Book_price_tags:
        Book_price.append(tags.text.replace('Â', ''))
    return Book_price

# print(get_book_price(doc))

def get_stock_availability(doc):
    Book_stock_tags = doc.find_all('p', class_ = 'instock availability')
    Book_stock = []
    for tags in Book_stock_tags:
        Book_stock.append(tags.text.strip())
    return Book_stock

# print(get_stock_availability(doc))

def get_book_url(Book_title_tags):
    Book_url = []
    for article in Book_title_tags:
        for link in article.find_all('a', href=True):
            url = link['href']
            links = 'https://books.toscrape.com/' + url
            if links not in Book_url:
                Book_url.append(links)
    return Book_url

# print(get_book_url(title_tags))

def get_doc(url):
    response = requests.get(url)
    doc = BeautifulSoup(response.text, 'html.parser')
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(response))
    return doc

def scrape_multiple_pages(n):
    URL = 'http://books.toscrape.com/catalogue/page-'
    titles, prices, stocks_avail, urls = [], [], [], []

    for page in range(1, n+1):
        doc = get_doc(URL + str(page) + '.html')
        title_tags, book_titles = get_book_titles(doc)
        titles.extend(book_titles)
        prices.extend(get_book_price(doc))
        stocks_avail.extend(get_stock_availability(doc))
        urls.extend(get_book_url(title_tags))

    book_dict1 = {
        'TITLE': titles,
        'PRICE': prices,
        'STOCK AVAILABILITY': stocks_avail,
        'URL': urls
    }
    return pd.DataFrame(book_dict1)

scrape_multiple_pages(5).to_csv('test.csv', index=None)


## gemi books
def get_book_tags(doc):
    Book_tags = doc.find_all('h3')
    return Book_tags

def get_book_titles(doc):
    Book_tags = get_book_tags(doc)
    Book_titles = []
    for article in Book_tags:
        link = article.find('a')
        if link:
            Book_titles.append(article.text)
    return Book_titles

def get_book_urls(doc):
    Book_tags = get_book_tags(doc)
    Book_urls = []
    for article in Book_tags:
        for link in article.find_all('a', href=True):
            url = link['href']
            links = 'https://gemibook.com/' + url
            if links not in Book_urls:
                Book_urls.append(links)
    return Book_urls

def get_books(doc):
    Book_tags = get_book_tags(doc)
    Book_titles = get_book_titles(doc)
    Book_urls = get_book_urls(doc)

    book_dict1 = {
        'TITLE': Book_titles,
        'URL': Book_urls
    }
    return pd.DataFrame(book_dict1)
