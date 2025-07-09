import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def rebuild():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    template = env.get_template('template.html')

    with open("meta_data.json", "r", encoding="utf-8") as books_file:
        books = json.load(books_file)

    chunked_books = chunked(books, 2, strict=False)
    rendered_page = template.render(books=chunked_books)

    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(rendered_page)

    print('Site rebuild')

rebuild()

server = Server()
server.watch('template.html', rebuild)
server.serve(root='.', port=8000)