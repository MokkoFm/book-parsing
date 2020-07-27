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


def make_json(collection_number, page_number, last_page, url, links):
    data = []
    for tag in links:
        for url_book in tag.select('a'):
            id_of_book = urljoin(url, url_book['href']).split('b')[1][:-1]
            url = 'http://tululu.org/b{}/'.format(id_of_book)
            try:
                response = requests.get(url, allow_redirects=False)
                response.raise_for_status()
            except requests.HTTPError as exception:
                print(exception)
            soup = BeautifulSoup(response.text, 'lxml')
            title_selector = "h1"
            finder_title = soup.select_one(title_selector)
            title = finder_title.text.strip(':').rsplit(':')[0]
            cover_selector = "div.bookimage img"
            for cover in soup.select(cover_selector):
                covers = cover['src']

            author_selector = "h1 a"
            finder_author = soup.select_one(author_selector)
            author = finder_author.text
            book_path = 'books/{}.txt'.format(id_of_book)

            genre_selector = "span.d_book a"
            finder_genre = soup.select(genre_selector)
            genres = []
            for genre in finder_genre:
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

    page_number += 1


def download_image(collection_number, page_number, last_page, url, links):
    for tag in links:
        for url_image in tag.select('img'):
            image_path = urljoin(url, url_image['src'])
            try:
                response = requests.get(image_path, allow_redirects=False)
                response.raise_for_status()
            except requests.HTTPError as exception:
                print(exception)
            image_name = urljoin(url, url_image['src']).split('/')[4]
            filename = Path('images', '{}'.format(image_name))

            with open(filename, 'wb') as file:
                file.write(response.content)

    page_number += 1


def download_book_from_collection(collection_number, page_number, last_page, url, links):
    for tag in links:
        for url_book in tag.select('a'):
            id_of_book = urljoin(url, url_book['href']).split('b')[1][:-1]
            url_of_book = 'http://tululu.org/b{}/'.format(id_of_book)
            try: 
                response = requests.get(url_of_book, allow_redirects=False)
                response.raise_for_status()
            except requests.HTTPError as exception:
                print(exception)
            soup = BeautifulSoup(response.text, 'lxml')
            finder_title = soup.select_one('h1')
            title = finder_title.text.strip(':').rsplit(':')[0]

            for data in id_of_book:
                url_to_download = "http://tululu.org/txt.php"
                payload = {'id': id_of_book}
                try:
                    response = requests.get(url_to_download, params=payload, allow_redirects=False)
                    response.raise_for_status()
                except requests.HTTPError as exception:
                    print(exception)
                filename = Path('books', sanitize_filename('{}. {}.txt').format(id_of_book, title))

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
    parser.add_argument('--skip_images', help='You can skip downloading images', action='store_const', const=True, default=False)
    parser.add_argument('--skip_txt', help='You can skip downloading books', action="store_const", const=True, default=False)
    parser.add_argument('--skip_json', help='You can skip downloading json', action='store_const', const=True, default=False)
    parser.add_argument('--dest_folder', help="You can choose destination folder for files", action='store_const', const=True, default=False)
    args = parser.parse_args()
    
    page_number = args.start_page
    last_page = args.end_page
    collection_number = 55
    url = 'http://tululu.org/l{}/{}'.format(collection_number, page_number)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    selector = "div.bookimage"
    links = soup.select(selector)
        
    while page_number <= last_page:
        if args.dest_folder:
            path = input('Please, write your destination folder for getting files')
            os.chdir(path)
            make_json(collection_number, page_number, last_page, url, links)
            download_book_from_collection(collection_number, page_number, last_page, url, links)
            download_image(collection_number, page_number, last_page, url, links)

        if args.skip_images:
            make_json(collection_number, page_number, last_page, url, links)
            download_book_from_collection(collection_number, page_number, last_page, url, links)

        if args.skip_txt:
            make_json(collection_number, page_number, last_page, url, links)
            download_image(collection_number, page_number, last_page, url, links)

        if args.skip_json:
            download_book_from_collection(collection_number, page_number, last_page, url, links)
            download_image(collection_number, page_number, last_page, url, links)

        if not args.skip_images and not args.skip_txt and not args.skip_json and not args.dest_folder:
            make_json(collection_number, page_number, last_page, url, links)
            download_book_from_collection(collection_number, page_number, last_page, url, links)
            download_image(collection_number, page_number, last_page, url, links)


if __name__ == "__main__":
    main()
