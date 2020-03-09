from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep
import re

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_details(html, base_cat_name, cat_name):
    
    stamp = {}
    
    try:
        lot_no = html.select('td')[0].get_text().strip()
        stamp['lot_no'] = lot_no
    except:
        stamp['lot_no'] = None  
        
    try:
        symbol = html.select('td')[1].get_text().strip()
        if not symbol:
            symbol = html.select('td')[1].select('img')[0].get('src')
        stamp['symbol'] = symbol
    except:
        stamp['symbol'] = None         
        
    try:
        cat_no = html.select('td')[2].get_text().strip()
        stamp['cat_no'] = cat_no
    except:
        stamp['cat_no'] = None        
    
    try:
        raw_text = html.select('td')[3].get_text().strip()
        raw_text = re.sub(' +', ' ', raw_text)
        raw_text = raw_text.replace('\r\n', ' ').replace('\n', ' ').strip()
        stamp['raw_text'] = raw_text
    except:
        stamp['raw_text'] = None
    
    try:
        price = html.select('td')[4].get_text().strip()
        price = price.replace('\r\n', ' ').replace('\n', ' ').strip()
        stamp['price'] = price
    except:
        stamp['price'] = None  
    
    stamp['currency'] = 'CAD'
    
    stamp['base_category'] = base_cat_name
    stamp['category'] = cat_name
    
    # image_urls should be a list
    images = []                    
    try:
        image_items = html.find_all('a', attrs={'target':'_blank'})
        if not len(image_items):
            image_items = html.select('.MagicZoomPlus')

        for image_item in image_items:
            img = image_item.get('href')
            if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date
    
    print(stamp)
    print('+++++++++++++')
    #sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):

    items = []

    base_cat_name = ''
    cat_name = ''

    try:
        html = get_html(url)
    except:
        return items, base_cat_name, cat_name

    try:
        for item in html.find_all('tr', attrs={'valign':'TOP'}):
            td0 = item.select('td')[0].get_text().strip()
            if (item not in items) and ('LotNo.' not in td0):
                items.append(item)
    except:
        pass
     
    try:
        base_cat_name = html.select('form h1')[0].get_text().strip()
    except:
        pass
    
    try:
        cat_name = html.select('form h1')[1].get_text().strip()
    except:
        pass
    
    shuffle(list(set(items)))
    
    return items, base_cat_name, cat_name

def get_categories():
    
    url = 'https://stampauctionnetwork.com/auctions.cfm'
   
    items = []

    try:
        html = get_html(url)
    except:
        return items

    try:
        items_cont = html.find_all('a', attrs={'name':'PricesRealized'})[0]
        for item in items_cont.parent.select('ul li a'):
            item_link = item.get('href')
            if (item_link not in items): 
                items.append(item_link)
    except: 
        pass
    
    shuffle(list(set(items)))
    
    return items

def get_base_url(url):
    
    base_url = ''
    
    parts = url.split('/')
    if parts[-1]:
        base_url = url.replace(parts[-1], '')
    
    return base_url

def get_subcategories(url):
   
    items = []
    
    try:
        html = get_html(url)
    except:
        return items
    
    base_url = get_base_url(url)

    try:
        for item in html.select('table ul > li > a'):
            item_link_temp = item.get('href')
            item_link_parts = item_link_temp.split('#')
            item_link_href = item_link_parts[0]
            if 'http' not in item_link_href:
                item_link = base_url + item_link_href
                if (item_link not in items): 
                    items.append(item_link)
    except: 
        pass

    
    shuffle(list(set(items)))
    
    return items

categories = get_categories()   
for category in categories:
    subcategories = get_subcategories(category) 
    for subcategory in subcategories:
        page_items, base_cat_name, cat_name = get_page_items(subcategory)
        for page_item in page_items:
            stamp = get_details(page_item, base_cat_name, cat_name) 
