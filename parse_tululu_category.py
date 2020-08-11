import requests
import os
import os.path
from pathlib import Path
import pathlib
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json
import pprint
import argparse
import sys
from time import sleep


class RedirectException(Exception):
    pass


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def check_response(response):
    response.raise_for_status()
    if response.status_code == 302:
        raise RedirectException('Warning, redirect!')


def make_json(last_page, json_data, book_id, response, soup):
    title_selector = soup.select_one("h1")
    title_text = title_selector.text
    title_for_json = title_text.strip(':').rsplit(':')[0]
    cover_selector = "div.bookimage img"
    image_cover = [cover['src'] for cover in soup.select(cover_selector)]
    author_title = soup.select_one("h1 a")
    author = author_title.text
    book_path = 'books/{}.txt'.format(book_id)
    genre_selector = soup.select("span.d_book a")
    genres = [genre.text for genre in genre_selector]
    comment_selector = "div.texts"
    comments = [comment.text.split(')')[1]
                for comment in soup.select(comment_selector)]
    to_json = {'title': title_for_json, 'image_src': image_cover, 'genre': genres,
               'comments': comments, 'author': author, 'book_path': book_path}
    json_data.append(to_json)


def download_image(image_url, response):
    image_name = image_url.split('/')[4]
    images_path = pathlib.Path("images/")
    images_path.mkdir(parents=True, exist_ok=True)
    filename = Path('images', '{}'.format(image_name))

    with open(filename, 'wb') as file:
        file.write(response.content)


def download_book(book_id, response, soup):
    finder_title = soup.select_one('h1')
    title_text = finder_title.text
    title = title_text.strip(':').rsplit(':')[0]
    url_to_download = "http://tululu.org/txt.php"
    payload = {'id': book_id}
    try:
        response = requests.get(
            url_to_download, params=payload, allow_redirects=False)
        check_response(response)
    except RedirectException as error:
        print(error)

    books_path = pathlib.Path("books/")
    books_path.mkdir(parents=True, exist_ok=True)
    filename = Path('books', sanitize_filename(
        '{}. {}.txt').format(book_id, title))

    with open(filename, 'wb') as file:
        print('Download', filename)
        file.write(response.content)

    if os.stat(filename).st_size == 0:
        print("Empty file! Removing... ", filename)
        os.remove(filename)


def make_parser_args():
    parser = argparse.ArgumentParser(
        description='You can download books from tululu')
    parser.add_argument('-start', '--start_page',
                        help='Choose first page', default=1, type=int)
    parser.add_argument('-end', '--end_page',
                        help='Choose last page', default=3, type=int)
    parser.add_argument('--skip_images', help='Skip downloading images',
                        action='store_const', const=True, default=False)
    parser.add_argument('--skip_txt', help='Skip downloading books',
                        action="store_const", const=True, default=False)
    parser.add_argument('--skip_json', help='Skip downloading json',
                        action='store_const', const=True, default=False)
    parser.add_argument('--dest_folder',
                        help="Choose destination folder", type=dir_path)
    args = parser.parse_args()
    return args


def main():
    args = make_parser_args()
    page_number = args.start_page
    last_page = args.end_page
    collection_number = 55
    json_data = []

    for current_page in range(page_number, last_page):
        try:
            url = 'http://tululu.org/l{}/{}'.format(
                collection_number, current_page)
            response = requests.get(url, allow_redirects=False)
            check_response(response)
            collection_soup = BeautifulSoup(response.text, 'lxml')
            selector = "div.bookimage"
            books_info = collection_soup.select(selector)

            if args.dest_folder:
                os.chdir(args.dest_folder)

            for tag in books_info:
                for book in tag.select('a'):
                    book_href = urljoin(url, book['href'])
                    book_id = book_href.split('b')[1][:-1]
                    book_url = 'http://tululu.org/b{}/'.format(book_id)
                    try:
                        response = requests.get(book_url, allow_redirects=False)
                        check_response(response)
                    
                    except RedirectException as error:
                        print(error)
                        

                    soup = BeautifulSoup(response.text, 'lxml')                        
                    if not args.skip_txt:
                        download_book(book_id, response, soup)

                    if not args.skip_json:
                        make_json(last_page, json_data, book_id, response, soup)
                    
                for book in tag.select('img'):
                    image_url = urljoin(url, book['src'])
                    try:
                        response = requests.get(image_url, allow_redirects=False)
                        check_response(response)
                    except RedirectException as error:
                        print(error)

                    if not args.skip_images:
                        download_image(image_url, response)

            if last_page:
                with open("books_data.json", "w", encoding='utf-8') as my_file:
                    json.dump(json_data, my_file, ensure_ascii=False)

        except requests.HTTPError as error:
            sys.stderr.write("Fatal error with URL\n", error)
            continue

        except requests.ConnectionError as error:
            sys.stderr.write("Fatal error with connection\n", error)
            sleep(10)
            continue

        except RedirectException as error:
            print(error)


if __name__ == "__main__":
    main()
