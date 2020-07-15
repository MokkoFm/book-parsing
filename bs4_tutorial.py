import requests
from bs4 import BeautifulSoup


url = 'http://tululu.org/b1/'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('h1').find('a')
book_data = title_tag.text
print(book_data)
