import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    with open("books.json", "r", encoding="utf8") as file:
        books_json = file.read()
    books = json.loads(books_json)
    chunked_books = list(chunked(books, 2))
    for couple in chunked_books[:1]:
        for book in couple:
            print(book)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')
    rendered_page = template.render(books=chunked_books)
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


on_reload()
server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
