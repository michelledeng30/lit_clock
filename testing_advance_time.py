import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import re
# import nltk
# from nltk.tokenize import sent_tokenize
# nltk.download('punkt')

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
    # regexp12 = '1[0-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?|[1-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?'
    # regexp24 = '24:00|2[0-3]:[0-5][0-9]|1[0-9]:[0-5][0-9]|[0-9]:[0-5][0-9]'
    # regexp = re.compile(regexp12+'|'+regexp24)
    
    result = re.findall(regexp, content)
    return result

def get_sentence_index(sentences, match):
    for i in range(len(sentences)):
        index = sentences[i].find(match)
        if index != -1:
            return i
    return -1

def split_text(text):
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov)"
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def handle_long_text(text_str, matches):
    quotes = []
    sentences = split_text(text_str)
    for match in matches:
        sentence_index = get_sentence_index(sentences, match)
        start = 0 if sentence_index - 3 < 0 else sentence_index - 3
        end = len(sentences) - 1 if sentence_index + 3 > len(sentences) else sentence_index + 3
        sentence_array = sentences[start:end+1]
        quote = ' '.join(sentence_array)
        quotes.append(quote)
    return quotes

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
            text_str = text.text
            matches = find_times(text_str)
            if matches:
                times.extend(matches)
                if len(text_str) > 500:
                    quotes.extend(handle_long_text(text_str, matches))
                else:
                    quote = text_str
                    quotes.extend([quote]*len(matches))
            
            page_numbers.extend([page]*len(matches))
            

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

    # print('titles', len(titles), 'times', len(times), 'pg', len(page_numbers), 'quote', len(quotes))
    return pd.DataFrame(book_dict1)

def test_func():
    df = scrape_book('https://gemibook.com/2435425-beach-read')

    df['TIME24'] = pd.to_datetime(df['TIME24'], infer_datetime_format=True).dt.time
    df = df.sort_values(by="TIME24")
    return df

test_func().to_csv('test-time-1.csv', index=None)