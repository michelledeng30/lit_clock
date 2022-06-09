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

    title_tag = doc.find('h3', class_='title')
    title = title_tag.text

    author_tag = doc.find('a', itemprop='author')
    author = author_tag.text

    all_ul = doc.find_all('ul', class_='list-chapter')
    page_urls = []
    for ul in all_ul:
        page_tags = ul.find_all('li')
        for page_tag in page_tags:
            page_link = page_tag.find('a', href=True)
            page_url = 'https://gemibook.com' + page_link['href']
            page_urls.append(page_url)
    
    return title, author, page_urls

get_book_info('https://gemibook.com/231064-the-hobbit')
get_book_info('https://gemibook.com/2435427-the-martian')

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
def find_numeric_times(content):
    # regexp = '(24:00|2[0-3]:[0-5][0-9]|1[0-9]:[0-5][0-9]|[0-9]:[0-5][0-9])'
    regexp12 = '1[0-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?|[1-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?'
    regexp24 = '24:00|2[0-3]:[0-5][0-9]|1[0-9]:[0-5][0-9]|[0-9]:[0-5][0-9]'
    regexp = re.compile(regexp12+'|'+regexp24)
    result = re.findall(regexp, content)
    return result


# helper function that finds all times using regex
# input: book content to search through
# output: all matches of the time in an array
def find_nonnumeric_times(content):

    re_onetonineteen = '(?:[Oo]ne|[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ee]leven|[Tt]welve|[Tt]hirteen|[Ff]ourteen|[Ff]ifteen|[Ss]ixteen|[Ss]eventeen|[Ee]ighteen|[Nn]ineteen)'
    re_first = '(?:[Qq]uarter|[Hh]alf|[Oo]ne|[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ee]leven|[Tt]welve|[Tt]hirteen|[Ff]ourteen|[Ff]ifteen|[Ss]ixteen|[Ss]eventeen|[Ee]ighteen|[Nn]ineteen)'
    re_last = '(?:[Oo]ne|[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ee]leven|[Tt]welve|[Mm]idnight|\s[Nn]oon)'
    regexp1 = '(?:[Tt]wenty|[Tt]hirty|[Ff]orty|[Ff]ifty)' + '[-\s]' + re_onetonineteen + '\s?-?(?:minute\s|minutes\s)?' + '(?:past|after|to|before)\s?' + re_last
    regexp2 = re_first + '\s?-?(?:minute\s|minutes\s)' + '(?:past|after|to|before)\s?' + re_last
    regexp3 = '(?:[Hh]alf|[Qq]uarter)\s' + '(?:past|after|to|before)\s?' + re_last
    regexp4 = '[a-zA-Z0-9]+\so\'clock'
    regexp5 = '[Mm]idnight|\s[Nn]oon'

    regexp = regexp1 + '|' + regexp2 + '|' + regexp3 + '|' + regexp4 + '|' + regexp5

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

map_hour = {
    '0': ['0', 'zero', 'Zero', 'midnight', 'Midnight'],
    '1': ['1', 'one', 'One'],
    '2': ['2', 'two', 'Two'],
    '3': ['3', 'three', 'Three'],
    '4': ['4', 'four', 'Four'],
    '5': ['5', 'five', 'Five'],
    '6': ['6', 'six', 'Six'],
    '7': ['7', 'seven', 'Seven'],
    '8': ['8', 'eight', 'Eight'],
    '9': ['9', 'nine', 'Nine'],
    '10': ['10', 'ten', 'Ten'],
    '11': ['11', 'eleven', 'Eleven'],
    '12': ['12', 'twelve', 'Twelve', 'noon', 'Noon']
}

map_minute = {
    '0': ['0', 'zero', 'Zero'],
    '1': ['1', 'one', 'One'],
    '2': ['2', 'two', 'Two'],
    '3': ['3', 'three', 'Three'],
    '4': ['4', 'four', 'Four'],
    '5': ['5', 'five', 'Five'],
    '6': ['6', 'six', 'Six'],
    '7': ['7', 'seven', 'Seven'],
    '8': ['8', 'eight', 'Eight'],
    '9': ['9', 'nine', 'Nine'],
    '10': ['10', 'ten', 'Ten'],
    '11': ['11', 'eleven', 'Eleven'],
    '12': ['12', 'twelve', 'Twelve'],
    '13': ['13', 'thirteen', 'Thirteen'],
    '14': ['14', 'fourteen', 'Fourteen'],
    '15': ['15', 'fifteen', 'Fifteen', 'quarter', 'Quarter'],
    '16': ['16', 'sixteen', 'Sixteen'],
    '17': ['17', 'seventeen', 'Seventeen'],
    '18': ['18', 'eighteen', 'Eighteen'],
    '19': ['19', 'nineteen', 'Nineteen'],
    '20': ['20', 'twenty', 'Twenty'],
    '21': ['21', 'twenty-one', 'Twenty-one'],
    '22': ['22', 'twenty-two', 'Twenty-two'],
    '23': ['23', 'twenty-three', 'Twenty-three'],
    '24': ['24', 'twenty-four', 'Twenty-four'],
    '25': ['25', 'twenty-five', 'Twenty-five'],
    '26': ['26', 'twenty-six', 'Twenty-six'],
    '27': ['27', 'twenty-seven', 'Twenty-seven'],
    '28': ['28', 'twenty-eight', 'Twenty-eight'],
    '29': ['29', 'twenty-nine', 'Twenty-nine'],
    '30': ['30', 'thirty', 'Thirty', 'half', 'Half'],
    '31': ['31', 'thirty-one', 'Thirty-one'],
    '32': ['32', 'thirty-two', 'Thirty-two'],
    '33': ['33', 'thirty-three', 'Thirty-three'],
    '34': ['34', 'thirty-four', 'Thirty-four'],
    '35': ['35', 'thirty-five', 'Thirty-five'],
    '36': ['36', 'thirty-six', 'Thirty-six'],
    '37': ['37', 'thirty-seven', 'Thirty-seven'],
    '38': ['38', 'thirty-eight', 'Thirty-eight'],
    '39': ['39', 'thirty-nine', 'Thirty-nine'],
    '40': ['40', 'forty', 'Forty'],
    '41': ['41', 'forty-one', 'Forty-one'],
    '42': ['42', 'forty-two', 'Forty-two'],
    '43': ['43', 'forty-three', 'Forty-three'],
    '44': ['44', 'forty-four', 'Forty-four'],
    '45': ['45', 'forty-five', 'Forty-five'],
    '46': ['46', 'forty-six', 'Forty-six'],
    '47': ['47', 'forty-seven', 'Forty-seven'],
    '48': ['48', 'forty-eight', 'Forty-eight'],
    '49': ['49', 'forty-nine', 'Forty-nine'],
    '50': ['50', 'fifty', 'Fifty'],
    '51': ['51', 'fifty-one', 'Fifty-one'],
    '52': ['52', 'fifty-two', 'Fifty-two'],
    '53': ['53', 'fifty-three', 'Fifty-three'],
    '54': ['54', 'fifty-four', 'Fifty-four'],
    '55': ['55', 'fifty-five', 'Fifty-five'],
    '56': ['56', 'fifty-six', 'Fifty-six'],
    '57': ['57', 'fifty-seven', 'Fifty-seven'],
    '58': ['58', 'fifty-eight', 'Fifty-eight'],
    '59': ['59', 'fifty-nine', 'Fifty-nine'],
}

def get_key(val, mapping):
    for key in mapping:
        if val in mapping[key]:
            return key
    return -1

def change_format(times):
    converted = []
    for time in times:
        words = time.split()
        if 'o\'clock' in time:
            hour = time.replace(' o\'clock', '')
            hour_key = get_key(hour, map_hour)
            if hour_key == -1:
                print('couldn\'t find ', time, hour)
                return
            converted.append(hour_key + ':00')
        
        
        elif 'past' in words or 'after' in words:
            hour = words[len(words)-1]
            hour_key = get_key(hour, map_hour)
            if hour_key == -1:
                print('couldn\'t find ', time, hour)
                return
            minute = words[0]
            min_key = get_key(minute, map_minute)
            if min_key == -1:
                print('couldn\'t find ', time, minute)
                return
           
            converted.append(hour_key + ':' + min_key)
        
        elif 'to' in words or 'before' in words:
            hour_plusone = words[len(words)-1]
            hour_plusone_key = get_key(hour_plusone, map_hour)
            if hour_plusone_key == -1:
                print('couldn\'t find ', time, hour_plusone)
                return
        
            hour_key = '12' if hour_plusone_key == '1' else str((int(hour_plusone_key)-1)%12)

            minute = words[0]
            min_opp_key = get_key(minute, map_minute)
            if min_opp_key == -1:
                print('couldn\'t find ', time, minute)
                return

            min_key = str(60 - int(min_opp_key))
            converted.append(hour_key + ':' + min_key)
        
        elif len(words) == 1:
            hour_key = get_key(words[0], map_hour)
            converted.append(hour_key + ':00')
        else:
            converted.append('00:00')
            print('did not match', time)
    return converted

# main function that scrapes a book for times
# input: url to main page of book
# output: DataFrame with times, book info, and quotes
def scrape_book(URL):
    title, author, urls = get_book_info(URL)
    num_pages = len(urls)
    
    times = []
    times24 = []
    page_numbers = []
    quotes = []
    for i in range(num_pages):
        page_url = urls[i]
        doc = get_doc(page_url)
        if doc == None:
            print('error retrieving website', title, i, page_url)
            continue
        content = doc.find('div', class_='chapter-content')
        if content == None:
            print('no content', title, i, page_url)
            continue
        texts = content.find_all('p')
        for text in texts:
            text_str = text.text
            numeric_matches = find_numeric_times(text_str)
            nonnumeric_matches = find_nonnumeric_times(text_str)
            if numeric_matches:
                times.extend(numeric_matches)
                times24.extend(numeric_matches)
                if len(text_str) > 500:
                    quotes.extend(handle_long_text(text_str, numeric_matches))
                else:
                    quote = text_str
                    quotes.extend([quote]*len(numeric_matches))
            if nonnumeric_matches:
                times.extend(nonnumeric_matches)
                times24.extend(change_format(nonnumeric_matches))
                if len(text_str) > 500:
                    quotes.extend(handle_long_text(text_str, nonnumeric_matches))
                else:
                    quote = text_str
                    quotes.extend([quote]*len(nonnumeric_matches))
            
            page_numbers.extend([i+1]*(len(numeric_matches)+len(nonnumeric_matches)))
            

    titles = [title] * len(times)
    authors = [author] * len(times)
    book_dict1 = {
        'TIME24': times24,
        'TITLE': titles,
        'AUTHOR': authors,
        'TIMES': times,
        'PAGE NUMBER': page_numbers,
        'QUOTE': quotes
    }

    return pd.DataFrame(book_dict1)

def test_func():
    df = scrape_book('https://gemibook.com/2435427-the-martian')

    df['TIME24'] = pd.to_datetime(df['TIME24'], infer_datetime_format=True, errors='coerce').dt.time
    df = df.sort_values(by="TIME24")
    return df

test_func().to_csv('gemibooks-1.csv', index=None)
# .to_csv('test-4.csv', index=None)

# main function that scrapes a number of books
# opens a csv file containing links to the book urls
# returns a sorted DataFrame of all found time matches
def scrape_main():
    with open('gemibook_urls.csv') as f:
        urls = [line.rstrip() for line in f]
    
    dfs = []

    for url in urls:
        if url:
            df = scrape_book(url)
            dfs.append(df)
        else:
            print('error at url ', url)

    dfs = pd.concat(dfs)

    dfs['TIME24'] = pd.to_datetime(dfs['TIME24'], infer_datetime_format=True, errors='coerce').dt.time
    dfs = dfs.sort_values(by="TIME24")
    dfs = dfs.drop_duplicates(subset=['QUOTE'], keep=False)
    dfs['PAGE NUMBER'] = dfs['PAGE NUMBER'].astype(int)
    return dfs

# scrape_main().to_csv('main-test-time-1.csv', index=None)
# scrape_book('https://gemibook.com/2435427-the-martian').to_csv('themartian2.csv', index=None)
