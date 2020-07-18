import requests
from bs4 import BeautifulSoup


url = 'http://tululu.org/b1/'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
find_author = soup.find('h1').find('a')
author = title_tag.text

find_title = soup.find('h1')
