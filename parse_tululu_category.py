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

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def make_json(collection_number, page_number, last_page, url, links, json_data):
    for tag in links:
        for tag in tag.select('a'):
            book_id = urljoin(url, tag['href']).split('b')[1][:-1]
            url = 'http://tululu.org/b{}/'.format(book_id)
            try:
                response = requests.get(url, allow_redirects=False)
                response.raise_for_status()
                if response.status_code == 302:
                    print('Warning, redirect in make_json func from book with url {}!'.format(url))
                    break
            except requests.HTTPError as exception:
                raise exception

            soup = BeautifulSoup(response.text, 'lxml')
            title_selector = "h1"
            finder_title = soup.select_one(title_selector)
            title = finder_title.text.strip(':').rsplit(':')[0]
            cover_selector = "div.bookimage img"
            image_cover = [cover['src'] for cover in soup.select(cover_selector)]

            author_selector = "h1 a"
            finder_author = soup.select_one(author_selector)
            author = finder_author.text
            book_path = 'books/{}.txt'.format(book_id)

            genre_selector = "span.d_book a"
            finder_genre = soup.select(genre_selector)
            genres = ['{}'.format(genre.text) for genre in finder_genre]

            comment_selector = "div.texts"
            comments = ['{}'.format(note.text).split(')')[1] for note in soup.select(comment_selector)]

            to_json = {'title': title, 'image_src': image_cover, 'genre': genres,
                        'comments': comments, 'author': author, 'book_path': book_path}
            json_data.append(to_json)

    if last_page:
        with open("books_data.json", "w", encoding='utf-8') as my_file:
            json.dump(json_data, my_file, ensure_ascii=False)


def download_image(collection_number, page_number, last_page, url, links):
    for tag in links:
        for tag in tag.select('img'):
            image_path = urljoin(url, tag['src'])
            try:
                response = requests.get(image_path, allow_redirects=False)
                response.raise_for_status()
                if response.status_code == 302:
                    print('Warning, redirect in download image func from image with path {}!'.format(image_path))
                    break
            except requests.HTTPError as exception:
                raise exception
            image_name = urljoin(url, tag['src']).split('/')[4]
            images_path = pathlib.Path("images/")
            images_path.mkdir(parents=True, exist_ok=True)
            filename = Path('images', '{}'.format(image_name))

            with open(filename, 'wb') as file:
                file.write(response.content)


def download_book_from_collection(collection_number, page_number, last_page, url, links):
    for tag in links:
        for tag in tag.select('a'):
            book_id = urljoin(url, tag['href']).split('b')[1][:-1]
            book_url = 'http://tululu.org/b{}/'.format(book_id)
            try:
                response = requests.get(book_url, allow_redirects=False)
                response.raise_for_status()
                if response.status_code == 302:
                    print('Warning, redirect in download book func from book with url {}!'.format(book_url))
                    break
            except requests.HTTPError as exception:
                    raise exception

            soup = BeautifulSoup(response.text, 'lxml')
            finder_title = soup.select_one('h1')
            title = finder_title.text.strip(':').rsplit(':')[0]

            for data in book_id:
                url_to_download = "http://tululu.org/txt.php"
                payload = {'id': book_id}
                try:
                    response = requests.get(url_to_download, params=payload, allow_redirects=False)
                    response.raise_for_status()
                    if response.status_code == 302:
                        print('Warning, redirect in download book func from book with id {}!'.format(book_id))
                        break
                except requests.HTTPError as exception:
                    raise exception
                books_path = pathlib.Path("books/")
                books_path.mkdir(parents=True, exist_ok=True)
                filename = Path('books', sanitize_filename('{}. {}.txt').format(book_id, title))

                with open(filename, 'wb') as file:
                    file.write(response.content)

                if os.stat(filename).st_size == 0:
                    print(" Removing ", filename)
                    os.remove(filename)


def main():
    parser = argparse.ArgumentParser(description='You can download books from tululu')
    parser.add_argument('-start', '--start_page', help='You can choose first page to download books', default=1, type=int)
    parser.add_argument('-end', '--end_page', help='You can choose last page to download books', default=2, type=int)
    parser.add_argument('--skip_images', help='You can skip downloading images', action='store_const', const=True, default=False)
    parser.add_argument('--skip_txt', help='You can skip downloading books', action="store_const", const=True, default=False)
    parser.add_argument('--skip_json', help='You can skip downloading json', action='store_const', const=True, default=False)
    parser.add_argument('--dest_folder', help="You can choose destination folder for files", type=dir_path)
    args = parser.parse_args()
    
    page_number = args.start_page
    last_page = args.end_page
    collection_number = 55
    json_data = []
        
    for page in range(page_number, last_page):
        url = 'http://tululu.org/l{}/{}'.format(collection_number, page_number)
        try:
            response = requests.get(url, allow_redirects=False)
            response.raise_for_status()
            if response.status_code == 302:
                        print('Warning, redirect in main func from book with url {}!'.format(url))
                        break
        except requests.HTTPError as exception:
            raise exception
        soup = BeautifulSoup(response.text, 'lxml')
        selector = "div.bookimage"
        links = soup.select(selector)

        if args.dest_folder:
            os.chdir(args.dest_folder)

        if not args.skip_images:
            download_image(collection_number, page_number, last_page, url, links)

        if not args.skip_txt:
            download_book_from_collection(collection_number, page_number, last_page, url, links)

        if not args.skip_json:
            make_json(collection_number, page_number, last_page, url, links, json_data)

        #page_number +=1


if __name__ == "__main__":
    main()
