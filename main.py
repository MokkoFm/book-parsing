import requests
import os
import os.path
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

os.chdir("C:/Users/mokko/Desktop/book-parsing")


def download_books(id_number):
        while id_number <= 10:
            url = 'http://tululu.org/b{}/'.format(id_number)
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            find_title = soup.find('h1')
            title = find_title.text.strip(':').rsplit(':')[0]
            
            url_to_download = "http://tululu.org/txt.php"
            payload = {'id': id_number}
            response = requests.get(url_to_download, params=payload, allow_redirects=False)
            response.raise_for_status()
            filename = Path('books', sanitize_filename('{}. {}.txt').format(id_number, title))

            with open(filename, 'wb') as file:
                file.write(response.content)

            id_number += 1


def get_information_about_book(id_number):
        url = 'http://tululu.org/b{}/'.format(id_number)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        find_title = soup.find('h1')
        title = find_title.text.rsplit('::')
        find_author = soup.find('h1').find('a')
        author = find_author.text
        print(title)

def main():
        download_books(1)
        #get_information_about_book(1)


if __name__ == "__main__":
    main()