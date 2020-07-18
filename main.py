import requests
import os
import os.path
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

os.chdir("C:/Users/mokko/Desktop/book-parsing")

def download_image(id_number):
    while id_number <=10:
        try:
            url = 'http://tululu.org/shots/{}.jpg'.format(id_number)
            response = requests.get(url)
            response.raise_for_status()
            filename = Path('images', sanitize_filename('{}.jpg').format(id_number))

            with open(filename, 'wb') as file:
                file.write(response.content)

        except requests.exceptions.HTTPError:
            print('The book with id {} has no cover'.format(id_number))

        id_number +=1
            

def download_book(id_number):
        while id_number <= 10:
            url = 'http://tululu.org/b{}/'.format(id_number)
            response = requests.get(url, allow_redirects=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            try:
                find_title = soup.find('h1')
                title = find_title.text.strip(':').rsplit(':')[0]
                print('\n' + 'Заголовок: ' + title)
            except AttributeError:
                'The book with id {} has no title'.format(id_number)

            try:
                find_genre = soup.find('span', class_='d_book')
                #print(find_genre)
                for tag in find_genre.find_all('a'):
                    print("{}".format(tag.text))
            except AttributeError:
                'The book with id {} has no genre'.format(id_number)  

            #try:
            #    find_cover = soup.find('div', class_='bookimage').find('a').find('img')['src']
            #    print(urljoin('http://tululu.org/', find_cover))
            #except AttributeError:
            #    'The book with id {} has no cover'.format(id_number)

            #try:
            #    for tag in soup.find_all('div', class_='texts'):
            #        print("{}".format(tag.text).split(')')[1])
            #except AttributeError:
            #    'The book with id {} has no comments'.format(id_number)

            url_to_download = "http://tululu.org/txt.php"
            payload = {'id': id_number}
            response = requests.get(url_to_download, params=payload, allow_redirects=False)
            response.raise_for_status()
            filename = Path('books', sanitize_filename('{}. {}.txt').format(id_number, title))
            print(filename)

            with open(filename, 'wb') as file:
                file.write(response.content)

            if os.stat(filename).st_size == 0:  
                print(" Removing ",filename)  
                os.remove(filename)  

            id_number += 1


def get_information_about_book(id_number):
            url = 'http://tululu.org/b{}/'.format(id_number)
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            find_title = soup.find('h1')
            title = find_title.text.strip(':').rsplit(':')[0]
            #find_cover = soup.find('div', class_='bookimage').find('img')['src']
            #print(find_cover)
            print('Заголовок: ' + title)


def main():
        download_book(1)
        #download_image(1)
        #get_information_about_book(1)


if __name__ == "__main__":
    main()