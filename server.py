import json
import os
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def render_page(template, books, page_name):
    chunked_books = chunked(books, 2, strict=False)
    rendered_page = template.render(books=chunked_books)
    with open(page_name, 'w', encoding='utf-8') as file:
        file.write(rendered_page)


def rebuild():
    page_name = 'index'
    folder_name = 'pages'
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    with open("meta_data.json", "r", encoding="utf-8") as books_file:
        books = json.load(books_file)

    chunked_books = chunked(books, 10, strict=False)
    for i, ten_books in enumerate(chunked_books, 1):
        page_path = folder_name + '/' + page_name + str(i) + '.html'
        render_page(template, ten_books, page_path)

    # render_page(template, books, 'index.html')

    print('Site rebuild')

rebuild()

server = Server()
server.watch('template.html', rebuild)
server.serve(root='.', port=8000)