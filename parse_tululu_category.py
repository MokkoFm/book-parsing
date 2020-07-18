import requests
import os
import os.path
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json
import pprint

os.chdir("C:/Users/mokko/Desktop/book-parsing")


def make_json(collection_number, page_number):
    while page_number <= 1:
        url = 'http://tululu.org/l{}/{}'.format(collection_number, page_number)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        find_links = soup.find_all('div', class_='bookimage')
        data = []

        for tag in find_links:
            for url_book in tag.find_all('a'):
                id_of_book = urljoin('http://tululu.org/',
                                     url_book['href']).split('b')[1][:-1]
                url = 'http://tululu.org/b{}/'.format(id_of_book)
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                find_title = soup.find('h1')
                title = find_title.text.strip(':').rsplit(':')[0]
                cover = soup.find('div', class_='bookimage').find('img')['src']
                find_author = soup.find('h1').find('a')
                author = find_author.text
                book_path = 'books/{}.txt'.format(id_of_book)
                find_genre = soup.find('span', class_='d_book')
                genres = []
                for genre in find_genre.find_all('a'):
                    genres.append('{}'.format(genre.text))

                comments = []
                for tag in soup.find_all('div', class_='texts'):
                    comment = '{}'.format(tag.text).split(')')[1]
                    comments.append(comment)

                to_json = {'title': title, 'image_src': cover, 'genre': genres,
                           'comments': comments, 'author': author, 'book_path': book_path}
                data.append(to_json)

        with open("books_data.json", "w", encoding='utf-8') as my_file:
            json.dump(data, my_file, ensure_ascii=False)

        with open('books_data.json', encoding="utf8") as file:
            data = file.read()
            json_data = json.loads(data)
            pprint.pprint(json_data)

        page_number += 1


def download_image(collection_number, page_number):
    while page_number <= 1:
        url = 'http://tululu.org/l{}/{}'.format(collection_number, page_number)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        find_image_links = soup.find_all('div', class_='bookimage')

        for tag in find_image_links:
            for url_image in tag.find_all('img'):
                download_image = urljoin(url, url_image['src'])
                response = requests.get(download_image, allow_redirects=False)
                response.raise_for_status()
                image_name = urljoin(url, url_image['src']).split('/')[4]
                filename = Path('images', '{}'.format(image_name))

                with open(filename, 'wb') as file:
                    file.write(response.content)

        page_number += 1


def download_book_from_collection(collection_number, page_number):
    while page_number <= 1:
        url = 'http://tululu.org/l{}/{}'.format(collection_number, page_number)
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        find_links = soup.find_all('div', class_='bookimage')

        for tag in find_links:
            for url_book in tag.find_all('a'):
                links_from_category = urljoin(
                    'http://tululu.org/', url_book['href'])
                id_of_book = urljoin('http://tululu.org/',
                                     url_book['href']).split('b')[1][:-1]
                url_of_book = 'http://tululu.org/b{}/'.format(id_of_book)
                response = requests.get(url_of_book, allow_redirects=False)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                find_title = soup.find('h1')
                title = find_title.text.strip(':').rsplit(':')[0]

                for data in id_of_book:
                    url_to_download = "http://tululu.org/txt.php"
                    payload = {'id': id_of_book}
                    response = requests.get(
                        url_to_download, params=payload, allow_redirects=False)
                    response.raise_for_status()
                    filename = Path('books', sanitize_filename(
                        '{}. {}.txt').format(id_of_book, title))

                    with open(filename, 'wb') as file:
                        file.write(response.content)

                    if os.stat(filename).st_size == 0:
                        print(" Removing ", filename)
                        os.remove(filename)

        page_number += 1


def main():
    make_json(55, 1)
    #download_book_from_collection(55, 1)
    #download_image(55, 1)


if __name__ == "__main__":
    main()
