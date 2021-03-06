import requests
import os
import os.path
from pathlib import Path
import pathlib
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json
import argparse
import sys
from time import sleep
import urllib.request
import time


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


def serialize_book(book_id, soup, filename):
    title_selector = soup.select_one("h1")
    title_text = title_selector.text
    title_for_json = title_text.strip(':').rsplit(':')[0].strip()
    dirname = os.path.dirname(__file__)
    image_path = os.path.join(dirname, filename)
    book_path = os.path.join(
        dirname, "media/books/{}. {}.txt".format(
            book_id, title_for_json))
    author_title = soup.select_one("h1 a")
    author = author_title.text
    genre_selector = soup.select("span.d_book a")
    genres = [genre.text for genre in genre_selector]
    comment_selector = "div.texts"
    comments = [comment.text.split(')')[1]
                for comment in soup.select(comment_selector)]
    to_json = {'title': title_for_json, 'image_src': image_path,
               'genre': genres, 'comments': comments,
               'author': author, 'book_path': book_path}
    return to_json


def download_image(image_url, image_name):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    images_path = pathlib.Path("media/images/")
    images_path.mkdir(parents=True, exist_ok=True)
    if image_name == 'nopic.gif':
        filename = os.path.join('media/images/{}'.format(str(image_name)))
    else:
        filename = os.path.join(
            'media/images/{}'.format(timestr + '-' + str(image_name)))
    image = urllib.request.urlopen(image_url)

    with open(filename, 'wb') as file:
        content = image.read()
        file.write(content)
    return filename


def download_book(book_id, response, soup):
    finder_title = soup.select_one('h1')
    title_text = finder_title.text
    title = title_text.strip(':').rsplit(':')[0].strip()
    url_to_download = "http://tululu.org/txt.php"
    payload = {'id': book_id}
    try:
        response = requests.get(
            url_to_download, params=payload, allow_redirects=False)
        check_response(response)
    except RedirectException as error:
        print(error)

    books_path = pathlib.Path("media/books/")
    books_path.mkdir(parents=True, exist_ok=True)
    filename = os.path.join('media/books/{}'.format(
        sanitize_filename('{}. {}.txt').format(book_id, title)))

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
                        help='Choose last page', default=5, type=int)
    parser.add_argument('--skip_images', help='Skip downloading images',
                        action='store_true', default=False)
    parser.add_argument('--skip_txt', help='Skip downloading books',
                        action="store_true", default=False)
    parser.add_argument('--skip_json', help='Skip downloading json',
                        action='store_true', default=False)
    parser.add_argument('--dest_folder',
                        help="Choose destination folder", type=dir_path)
    args = parser.parse_args()
    return args


def find_books(collection_number, current_page):
    try:
        url = 'http://tululu.org/l{}/{}'.format(
            collection_number, current_page)
        response = requests.get(url, allow_redirects=False)
        check_response(response)
    except RedirectException as error:
        print(error)
    collection_soup = BeautifulSoup(response.text, 'lxml')
    selector = "div.bookimage"
    books = collection_soup.select(selector)
    return books, url


def get_book_url(url, book):
    book_href = urljoin(url, book['href'])
    book_id = book_href.split('b')[1][:-1]
    book_url = 'http://tululu.org/b{}/'.format(book_id)
    try:
        response = requests.get(
            book_url, allow_redirects=False)
        check_response(response)
        soup = BeautifulSoup(response.text, 'lxml')
    except RedirectException as error:
        print(error)
    return book_id, response, soup


def write_json_file(last_page, json_data):
    if last_page:
        with open("static/books.json", "w", encoding='utf-8') as my_file:
            json.dump(json_data, my_file, ensure_ascii=False)


def main():
    args = make_parser_args()
    page_number = args.start_page
    last_page = args.end_page
    collection_number = 55
    json_data = []

    for current_page in range(page_number, last_page):
        try:
            books, url = find_books(collection_number, current_page)
            if args.dest_folder:
                os.chdir(args.dest_folder)

            for tag in books:
                for book in tag.select('img'):
                    image_url = urljoin(url, book['src'])
                    image_name = image_url.split('/')[-1]
                    if not args.skip_images:
                        try:
                            filename = download_image(image_url, image_name)
                        except requests.HTTPError:
                            sys.stderr.write("Error with URL\n")
                            continue
                        except requests.ConnectionError:
                            sys.stderr.write("Error with connection\n")
                            sleep(30)
                            continue
                        except requests.TimeoutError:
                            sys.stderr.write("Timeout error\n")
                            sleep(30)
                            continue

                for book in tag.select('a'):
                    book_id, response, soup = get_book_url(url, book)
                    if not args.skip_txt:
                        try:
                            download_book(book_id, response, soup)
                        except requests.HTTPError:
                            sys.stderr.write("Error with URL\n")
                            continue
                        except OSError:
                            sys.stderr.write("Impossible filename\n")
                            continue
                        except requests.ConnectionError:
                            sys.stderr.write("Error with connection\n")
                            sleep(30)
                            continue
                        except requests.TimeoutError:
                            sys.stderr.write("Timeout error\n")
                            sleep(30)
                            continue

                    if not args.skip_json:
                        try:
                            to_json = serialize_book(book_id, soup, filename)
                            json_data.append(to_json)
                        except UnboundLocalError:
                            sys.stderr.write("Image_src - no information\n")
                            exit()

            write_json_file(last_page, json_data)

        except RedirectException as error:
            print(error)
        except requests.HTTPError:
            sys.stderr.write("Error with URL\n")
            continue
        except requests.ConnectionError:
            sys.stderr.write("Error with connection\n")
            sleep(30)
            continue


if __name__ == "__main__":
    main()
