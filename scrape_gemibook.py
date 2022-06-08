import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import re

url = 'https://gemibook.com/'
response = requests.get(url)
contents = response.text

with open('Bookswebpage.html', 'w') as f:
    f.write(contents)

doc = BeautifulSoup(contents, 'html.parser')

def get_book_info(URL):
    response = requests.get(URL)
    contents = response.text
    with open('Bookswebpage.html', 'w') as f:
        f.write(contents)
    doc = BeautifulSoup(contents, 'html.parser')

    title_tag = doc.find('h3', class_='title')
    title = title_tag.text

    author_tag = doc.find('a', itemprop='author')
    author = author_tag.text

    all_ul = doc.find_all('ul', class_='list-chapter')
    num = 0
    for ul in all_ul:
        num += len(ul.find_all('li'))

    link = doc.find('a', class_='btn btn-primary btn-sm', href=True)
    url = 'https://gemibook.com' + link['href']
    
    return title, author, num, url

def get_doc(url):
    response = requests.get(url)
    doc = BeautifulSoup(response.text, 'html.parser')
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(response))
    return doc

def find_times(content):
    # regexp = '(24:00|2[0-3]:[0-5][0-9]|1[0-9]:[0-5][0-9]|[0-9]:[0-5][0-9])'
    regexp12 = '1[0-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?|[1-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?'
    regexp24 = '24:00|2[0-3]:[0-5][0-9]|1[0-9]:[0-5][0-9]|[0-9]:[0-5][0-9]'

    regexp = re.compile(regexp12+'|'+regexp24)
    result = re.findall(regexp, content)
    return result

def scrape_book(URL):
    title, author, pages, url = get_book_info(URL)
    index = url.find('p-1')
    start_url = url[:index]
    book_num = url[index+4:]
    
    times = []
    page_numbers = []
    quotes = []

    for page in range(1, pages+1):
        page_url = start_url + 'p-' + str(page) + '-' + str(int(book_num)+page-1)
        doc = get_doc(page_url)
        content = doc.find('div', class_='chapter-content')
        texts = content.find_all('p')
        for text in texts:
            matches = find_times(str(text.text))
            times.extend(matches)
            page_numbers.extend([page]*len(matches))
            quotes.extend([text.text]*len(matches))

    titles = [title] * len(times)
    authors = [author] * len(times)
    book_dict1 = {
        'TIME24': times,
        'TITLE': titles,
        'AUTHOR': authors,
        'TIMES': times,
        'PAGE NUMBER': page_numbers,
        'QUOTE': quotes
    }

    return pd.DataFrame(book_dict1)

def test_func():
    df = scrape_book('https://gemibook.com/2435427-the-martian')

    df['TIME24'] = pd.to_datetime(df['TIME24'], infer_datetime_format=True).dt.time
    df = df.sort_values(by="TIME24")
    return df

test_func().to_csv('test-4.csv', index=None)


def scrape_main():
    with open('gemibooks_urls_test.csv') as f:
        urls = [line.rstrip() for line in f]
    
    dfs = []

    for url in urls:
        df = scrape_book(url)
        dfs.append(df)

    dfs = pd.concat(dfs)

    dfs['TIME24'] = pd.to_datetime(dfs['TIME24'], format="%H:%M").dt.time
    dfs = dfs.sort_values(by="TIME24")
    dfs = dfs.drop_duplicates(subset=['QUOTE'], keep='first')
    return dfs

scrape_main().to_csv('main-test-5.csv', index=None)

# scrape_book('https://gemibook.com/2435427-the-martian').to_csv('themartian2.csv', index=None)


