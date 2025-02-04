import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import threading
import queue
import re

def response_func(query,num):
    query = query.replace(' ','+')
    url = f'https://www.amazon.com/s?k={query}&page={num}'
    headers = {'accept-encoding':'gzip, deflate, br, zstd','accept-language':'en-US,en;q=0.9','user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
    response = requests.get(url,headers=headers)
    if response.status_code==200:
        return response.text
    else:
        print('Check your connection')

def open_url(url):
    headers = {'accept-encoding':'gzip, deflate, br, zstd','accept-language':'en-US,en;q=0.9','user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
    response_data = requests.get(url,headers=headers)
    soup_2 = bs(response_data.text,'html.parser')
    return soup_2

def extract_page(query,num,result_queue):
    data_list = []
    response = response_func(query,num)
    soup = bs(response,'html.parser')
    big_box = soup.find_all('div',{'role':'listitem'})
    for box in big_box:
        link = box.find('a').get('href')
        url = f'https://www.amazon.com{link}'
        page = open_url(url)
        try:
            element = page.find(attrs={'data-asin': True})
            asin = element['data-asin']
            name_text = page.find('h1',{'id':'title'}).text
            name = re.sub(r'\s+', ' ', name_text).strip()
            regular_price = page.find('span',{'class':"a-price aok-align-center reinventPricePriceToPayMargin priceToPay"}).text
            discounted_price_ele = page.find('span',{"class":"a-size-small aok-offscreen"})
            if discounted_price_ele:
                discounted_price = discounted_price_ele.text.split(':')[1]
            else:
                discounted_price = None
            feature_ele = page.find('div',{'id':"feature-bullets"})
            if feature_ele:
                features = feature_ele.find('ul').text
            else:
                features= page.find('div',{'id':"productFactsDesktopExpander"}).find('ul').text
            image = page.find('div',{'id':"imgTagWrapperId"}).find('img').get('src')
            rating = page.find('div',{'id':"averageCustomerReviews"}).find('span',{'class':'a-size-base a-color-base'}).text
            reviews = page.find('span',{'id':"acrCustomerReviewText"}).text.replace('ratings',"")
            supplier_text = page.find('div',{'id':"bylineInfo_feature_div"}).text.replace('Visit the ',"").replace('Brand: ',"")
            supplier = re.sub(r'\s+', ' ', supplier_text).strip()
            supplier_url = page.find('div',{'id':'bylineInfo_feature_div'}).find('a').get('href')
            dict_data = {'ASIN': asin,
                        'Name':name,
                        'Price':regular_price,
                        'List Price':discounted_price,
                        'Features':features,
                        'Image':image,
                        'Rating':rating,
                        'Reviews':reviews,
                        'Supplier':supplier,
                        'Supplier_url':f'https://www.amazon.com{supplier_url}'}
            data_list.append(dict_data)
        except AttributeError:
            print('data not found')
            continue
    result_queue.put(data_list)

def extract_data(query):
    times = 8
    threads = []
    result_queue = queue.Queue()
    for i in range(times):
        thread = threading.Thread(target=extract_page,args=(query,i,result_queue))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    
    total_data = []
    while not result_queue.empty():
        total_data.extend(result_queue.get())  # Combine the data lists from all threads
    df = pd.DataFrame(total_data)
    return df

def convert_csv(df,filename):
    df.to_csv(filename)