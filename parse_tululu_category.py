import requests
import os
import os.path
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json
import pprint
import argparse


os.chdir("C:/Users/mokko/Desktop/book-parsing")


def make_json(collection_number, page_number, last_page):
    while page_number <= last_page:
        url = 'http://tululu.org/l{}/{}'.format(collection_number, page_number)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        selector = "div.bookimage"
        find_links = soup.select(selector)
        data = []

        for tag in find_links:
            for url_book in tag.select('a'):
                id_of_book = urljoin('http://tululu.org/',
                                     url_book['href']).split('b')[1][:-1]
                url = 'http://tululu.org/b{}/'.format(id_of_book)
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                title_selector = "h1"
                find_title = soup.select_one(title_selector)
                title = find_title.text.strip(':').rsplit(':')[0]
                cover_selector = "div.bookimage img"
                for cover in soup.select(cover_selector):
                    covers = cover['src']

                author_selector = "h1 a"
                find_author = soup.select_one(author_selector)
                author = find_author.text
                book_path = 'books/{}.txt'.format(id_of_book)

                genre_selector = "span.d_book a"
                find_genre = soup.select(genre_selector)
                genres = []
                for genre in find_genre:
                    genres.append('{}'.format(genre.text))

                comment_selector = "div.texts"
                comments = []
                for note in soup.select(comment_selector):
                    comment = '{}'.format(note.text).split(')')[1]
                    comments.append(comment)

                to_json = {'title': title, 'image_src': covers, 'genre': genres,
                           'comments': comments, 'author': author, 'book_path': book_path}
                data.append(to_json)

        with open("books_data.json", "w", encoding='utf-8') as my_file:
            json.dump(data, my_file, ensure_ascii=False)

        with open('books_data.json', encoding="utf8") as file:
            data = file.read()
            json_data = json.loads(data)
            pprint.pprint(json_data)

        page_number += 1


def download_image(collection_number, page_number, last_page):
    while page_number <= last_page:
        url = 'http://tululu.org/l{}/{}'.format(collection_number, page_number)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        selector = "div.bookimage"
        find_image_links = soup.select(selector)

        for tag in find_image_links:
            for url_image in tag.select('img'):
                download_image = urljoin(url, url_image['src'])
                response = requests.get(download_image, allow_redirects=False)
                response.raise_for_status()
                image_name = urljoin(url, url_image['src']).split('/')[4]
                filename = Path('images', '{}'.format(image_name))

                with open(filename, 'wb') as file:
                    file.write(response.content)

        page_number += 1


def download_book_from_collection(collection_number, page_number, last_page):
    while page_number <= last_page:
        url = 'http://tululu.org/l{}/{}'.format(collection_number, page_number)
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        selector = "div.bookimage"
        find_links = soup.select(selector)

        for tag in find_links:
            for url_book in tag.select('a'):
                links_from_category = urljoin(
                    'http://tululu.org/', url_book['href'])
                id_of_book = urljoin('http://tululu.org/',
                                     url_book['href']).split('b')[1][:-1]
                url_of_book = 'http://tululu.org/b{}/'.format(id_of_book)
                print(url_of_book)
                response = requests.get(url_of_book, allow_redirects=False)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                find_title = soup.select_one('h1')
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
    parser = argparse.ArgumentParser(description='You can download books from tululu')
    parser.add_argument('-start', '--start_page', help='You can choose first page to download books', default=1, type=int)
    parser.add_argument('-end', '--end_page', help='You can choose last page to download books', default=2, type=int)
    args = parser.parse_args()
    page_number = args.start_page
    last_page = args.end_page

    #make_json(55, page_number, last_page)
    #download_book_from_collection(55, page_number, last_page)
    download_image(55, page_number, last_page)

    return last_page


if __name__ == "__main__":
    main()
