import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

with open("books.json", "r", encoding="utf8") as file:
    books_json = file.read()

books = json.loads(books_json)
print(books[0]["image_src"])

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html'])
)
template = env.get_template('index.html')

rendered_page = template.render(
    book_title=books[0]["title"],
    book_author=books[0]["author"],
    book_img=books[0]["image_src"]
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)
