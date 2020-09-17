import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    with open("static/books.json", "r", encoding="utf8") as file:
        books_json = file.read()
    books = json.loads(books_json)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')

    book_pages = list(chunked(books, 10))
    pages_amount = len(book_pages)
    for page_number, page in enumerate(book_pages):
        rendered_page = template.render(
            books=page,
            pages_amount=pages_amount,
            page_number=page_number + 1)
        with open('pages/index{}.html'.format(page_number + 1),
                  'w', encoding="utf8") as file:
            file.write(rendered_page)

        if page_number == 0:
            with open('pages/index.html', 'w', encoding="utf8") as file:
                file.write(rendered_page)


on_reload()
server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
