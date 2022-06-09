import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import re

# helper function to get info from main book page
# input: URL for the book page in gemibooks.com
# output: book title, book author, number of chapters/pages, url to 1st page
def get_book_info(URL):
    response = requests.get(URL)
    contents = response.text
    with open('Bookswebpage.html', 'w') as f:
        f.write(contents)
    doc = BeautifulSoup(contents, 'html.parser')

    title_tag = doc.find('a', class_='sn-link-color sn-list-header-h1')
    title = title_tag.text

    author_tag = doc.find('h5', class_=None)
    author_tag_next = author_tag.find('a')
    author = author_tag_next.text

    list_all = doc.find_all('div', class_='card-body row')
    
    page_urls = []
    for sub_list in list_all:
        page_tags = sub_list.find_all('a', href=True)
        for page_tag in page_tags:
            page_url = 'https://www.allfreenovel.com/' + page_tag['href']
            page_urls.append(page_url)

    return title, author, page_urls

get_book_info('https://www.allfreenovel.com/Book/Details/16395/The-Invisible-Life-of-Addie-LaRue')

# helper function that gets the page from url
# input: page url
# output: page document
def get_doc(url):
    response = requests.get(url)
    doc = BeautifulSoup(response.text, 'html.parser')
    if response.status_code != 200:
        print('url didn\'t work', url)
        return None
        # raise Exception('Failed to load page {}'.format(response))
    return doc

# helper function that finds all times using regex
# input: book content to search through
# output: all matches of the time in an array
def find_times(content):
    # regexp = '(24:00|2[0-3]:[0-5][0-9]|1[0-9]:[0-5][0-9]|[0-9]:[0-5][0-9])'
    regexp12 = '1[0-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?|[1-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?'
    regexp24 = '24:00|2[0-3]:[0-5][0-9]|1[0-9]:[0-5][0-9]|[0-9]:[0-5][0-9]'
    regexp = re.compile(regexp12+'|'+regexp24)
    result = re.findall(regexp, content)
    return result

# sub helper function that gets the index of the sentence containing the given time
# input: sentence array, match (time)
# output: index of the sentence containing the time, else -1
def get_sentence_index(sentences, match):
    for i in range(len(sentences)):
        index = sentences[i].find(match)
        if index != -1:
            return i
    return -1

# sub helper function that splits a paragraph into sentences
# input: paragraph string
# output: array of sentences
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

# helper function that shortens quotes if the text is too long
# input: text chunk, array of time matches
# output: array of shortened quotes with length = len(matches)
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


# main function that scrapes a book for times
# input: url to main page of book
# output: DataFrame with times, book info, and quotes
def scrape_book(URL):
    title, author, urls = get_book_info(URL)
    num_pages = len(urls)
    
    times = []
    page_numbers = []
    quotes = []
    for i in range(num_pages):
        page_url = urls[i]
        doc = get_doc(page_url)
        if doc == None:
            print('error retrieving website', title, i, page_url)
            continue
        contents = doc.find_all('p', class_='storyText')
        if contents == None:
            print('no contents', title, i, page_url)
            continue
        for text in contents:
            text_str = text.text
            matches = find_times(text_str)
            if matches:
                times.extend(matches)
                if len(text_str) > 500:
                    quotes.extend(handle_long_text(text_str, matches))
                else:
                    quote = text_str
                    quotes.extend([quote]*len(matches))
            
            page_numbers.extend([i+1]*len(matches))
            

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
    print(book_dict1)

    return pd.DataFrame(book_dict1)

def test_func():
    df = scrape_book('https://www.allfreenovel.com/Book/Details/16395/The-Invisible-Life-of-Addie-LaRue')

    df['TIME24'] = pd.to_datetime(df['TIME24'], infer_datetime_format=True, errors='coerce').dt.time
    df = df.sort_values(by="TIME24")
    df = df.drop_duplicates(subset=['QUOTE'], keep=False)
    return df

# test_func().to_csv('test-allnovels-1.csv', index=None)


# main function that scrapes a number of books
# opens a csv file containing links to the book urls
# returns a sorted DataFrame of all found time matches
def scrape_main():
    with open('allnovels.csv') as f:
        urls = [line.rstrip() for line in f]
    
    dfs = []

    for url in urls:
        if url:
            df = scrape_book(url)
            dfs.append(df)
        else:
            print('error at url ', url)

    dfs = pd.concat(dfs)

    dfs['TIME24'] = pd.to_datetime(dfs['TIME24'], infer_datetime_format=True).dt.time
    dfs = dfs.sort_values(by="TIME24")
    dfs = dfs.drop_duplicates(subset=['QUOTE'], keep=False)
    dfs['PAGE NUMBER'] = dfs['PAGE NUMBER'].astype(int)
    return dfs

scrape_main().to_csv('allnovels-1.csv', index=None)


