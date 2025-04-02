"""
Local Value

A tool to web-scrape and display real state value data for my region (from the website zapimoveis.com.br)
Author: Alex Mees (https://github.com/alexmeessrg)
DAte: 27/03/2025
License: MIT
Version: 0.1
Dependencies: Beatiful Soup, Selenium, Plotly, Geopy 

At this moment you need to manually search the page and past the link below. Beware: site structure might change over time.
"""


#Standard OS libraries
import time
import random
import json
from typing import List, Dict
import re

#Local libraries

#Third party libraries
from bs4 import BeautifulSoup #static page scrapper
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from geopy.geocoders import Nominatim
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo


url = "https://www.zapimoveis.com.br/venda/imoveis/rs+porto-alegre/?transacao=venda&onde=,Rio%20Grande%20do%20Sul,Porto%20Alegre,,,,,city,BR%3ERio%20Grande%20do%20Sul%3ENULL%3EPorto%20Alegre,-30.036818,-51.208989,&itl_id=1000072&itl_name=zap_-_botao-cta_buscar_to_zap_resultado-pesquisa&origem=busca-recente"


""" 
Rotate user agents to reduce chance of detection
Provided list are desktop user agents. Updated in 27/03/2025 from [www.useragents.me]
"""
user_agent_file_path = 'data/user_agents_list.json'

with open(user_agent_file_path, 'r') as file:
    ua_data = json.load(file)

user_agents_list = [entry['ua'] for entry in ua_data]

"""
Proxy Addresses list to reduce chance of detection
"""
proxies_list = [
    "47.251.122.81:8888",
    "139.59.1.14:80",
    "51.84.106.225:20202",
    "56.124.107.85:20202",
    "56.155.45.176:20202",
    "51.44.174.195:20201",
    "56.155.36.111:20201",
    "13.60.253.212:20202",
    "51.84.68.241:20202",
    "65.49.14.150:3128",
    "50.223.246.237:80",
    "50.174.7.159:80",
    "50.207.199.87:80",
    "32.223.6.94:80",
    "128.199.202.122:8080",
    "15.235.10.31:28003",
    "8.218.14.185:1088",
    "20.27.14.220:8561",
    "65.49.14.168:3128",
    "20.78.118.91:8561",
    "50.207.199.80:80",
    "50.207.199.83:80",
    "50.174.7.153:80",
    "50.202.75.26:80",
    "50.169.37.50:80",
    "50.239.72.18:80",
    "50.175.212.66:80",
    "50.217.226.47:80",
    "50.239.72.16:80",
    "50.239.72.19:80",
    "50.217.226.40:80",
    "50.221.74.130:80",
    "190.58.248.86:80",
    "203.115.101.51:82",
    "50.175.212.74:80",
    "50.207.199.82:80",
    "50.174.7.152:80",
    "51.158.105.94:31826",
    "66.191.31.158:80",
    "113.160.132.195:8080",
    "179.96.28.58:80",
    "103.249.86.48:3128",
    "65.49.2.199:3128",
    "49.51.245.200:13001",
    "43.153.118.253:13001",
    "49.51.179.85:13001",
    "27.79.245.82:16000",
    "43.135.178.216:13001",
    "170.106.153.126:13001",
    "43.135.130.124:13001",
    "49.51.33.115:13001",
    "43.135.154.71:13001",
    "43.130.17.73:13001",
    "170.106.193.214:13001",
    "43.135.137.152:13001",
    "43.130.11.212:13001",
    "49.51.179.77:13001",
    "43.130.57.165:13001",
    "43.153.99.175:13001",
    "54.37.214.253:8080",
    "83.217.23.35:8090",
    "43.154.134.238:50001"
]


def get_random_headers_and_proxy():
    headers = {
        'User-Agent': random.choice(user_agents_list)
    }
    proxy = {
        'http': random.choice(proxies_list),
        'https': random.choice(proxies_list)
    }
    return headers, proxy

# Additional header decorations:
header_decorations = {
    'referer': 'https://www.scrapingcourse.com/ecommerce/',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'accept-encoding': 'gzip, deflate, br',
    'sec-ch-device-memory': '8',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-platform': "Windows",
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-ch-viewport-width': '792'
}


headers, proxy = get_random_headers_and_proxy()

random_keys = random.sample(list(header_decorations.keys()),4)
subset_decorations = {key: header_decorations[key] for key in random_keys}

headers.update(subset_decorations) #add just some of header decorations for further variation.

print (headers)



user_agent = random.choice(user_agents_list)

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless=new')
chrome_options.add_argument((f'user-agent={user_agent}'))
#, proxies=proxy?

driver = webdriver.Chrome(options=chrome_options)

driver.set_window_size(1920,1080) #set size even in headless mode to fix scrolling issues

delay = random.uniform(5,9) #random time to wait to avoid detection
print(f'Waiting: {delay} seconds...')
driver.implicitly_wait(delay)

driver.get(url)

last_height = driver.execute_script("return document.body.scrollHeight")
print (last_height)
max_scrolls = 20 #stops from scrolling forever if something goes wrong
current_scrolls = 1

while True:
    """
    1) scrolling too fast all the way down to the page footer might not trigger the lazy loader.
    2) scrolling height might be unchanged between two or three steps if next content has not yet been loaded. In some cases Last Height = New Height even if not hitting the last part of the page. You could reduce the rate
    of scrolling (less scroll per iteration or longer wait) but that just takes forever.
    """
    
    print("--- SIMULATING SCROLLING DOWN ---")
    
    ActionChains(driver).scroll_by_amount(0,int(450)).perform()

    delay = random.uniform(2.5,4.5) #randomize wait time
    time.sleep(delay) #wait for content to load

    #stop on maximum scrolls
    current_scrolls += 1
    if (current_scrolls >= max_scrolls):
        print ("Stopped Scrolling - reached max scrolling")
        break

soup = BeautifulSoup(driver.page_source, 'html.parser')

driver.quit()

uniqueIDs = soup.find_all('a', class_="ListingCard_result-card__Pumtx")

print (f"Number of Results: {len(uniqueIDs)}")

collected_data = []

for listing in uniqueIDs:
    
    #Link to listing
    link = listing.get("href") #link to property
    id = listing.get("data-id") #unique ID

    #listing price
    price = listing.find('div', {"data-cy": "rp-cardProperty-price-txt"})
    if price:
        try:
            price = price.find('p')
            price = price.get_text(strip=True) 
            price = re.sub(r'\D', '', price)
            price = int(price)
        except ValueError:
            price = -1
            print("Can't convert [price].")
        

    #approximate address
    address = listing.find("p", {"data-cy": "rp-cardProperty-street-txt"})
    address = address.get("title") if address else "NotAvailable"

    #Area
    area = listing.find("li", {"data-cy": "rp-cardProperty-propertyArea-txt"})
    area = area.get_text(strip=True) if area else "NotAvailable"    
    
    this_listing = {"Price": price, "Area": area, "Link": link, "Address": address, "ID": id}
    collected_data.append(this_listing)

# Function to geocode an address
def geocode_address(address):
    geolocator = Nominatim(user_agent="address_geocoder") #this have maximum of 1 request per second for free users.
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

for data in collected_data:
    addr = str(data["Address"])
    addr = addr + ', Porto Alegre/RS'
    lat, lon = geocode_address(addr)
    data["Latitude"] = lat
    data["Longitude"] = lon
    time.sleep(1) #Nonimatin has a maximum request of 1 per second. Maybe it can be pushed a bit more?

addresses = [prop["Address"] for prop in collected_data]
prices = [prop["Price"] for prop in collected_data]
areas = [prop["Area"] for prop in collected_data]
latitudes = [prop["Latitude"] for prop in collected_data]
longitudes = [prop["Longitude"] for prop in collected_data]
ids = [prop["ID"] for prop in collected_data]

pin_sizes = [15]*len(areas)
color_scales = (px.colors.sequential.RdBu)*len(areas)
colors = prices
c_min = [300000] * len(areas)
c_max = [2000000] * len(areas)

data = {'Address': addresses,
        'Price': prices,
        'Area': areas,
        'Latitude': latitudes,
        'Longitude': longitudes,
        'PinSize': pin_sizes,
        'Colors': prices,
        'Id': ids
        }

fig = px.scatter_map(data, lat='Latitude', lon='Longitude', text='Address',
                     hover_name='Address', hover_data={'Price': True, 'Area': True, 'Id': True},
                     title="Geographically Located Properties", map_style="open-street-map", zoom=10,
                    size='PinSize',color='Price',color_continuous_scale=px.colors.sequential.RdBu,range_color=[200000,2000000])


pyo.plot(fig)
