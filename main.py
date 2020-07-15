import requests
import os
import os.path
from pathlib import Path

os.chdir("C:/Users/mokko/Desktop/book-parsing")
id_number = 1

while id_number <= 10:
    payload = {'id': id_number}
    url = "http://tululu.org/txt.php"
    response = requests.get(url, params=payload, allow_redirects=False)
    response.raise_for_status()
    filename = Path('books', 'id{}.txt'.format(id_number))

    with open(filename, 'wb') as file:
        file.write(response.content)

    id_number += 1
