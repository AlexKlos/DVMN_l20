import json
import os
import shutil
import textwrap
import threading

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def render_page(template, books, page_path, current_page, total_pages):
    number_of_columns = 2
    chunked_books = chunked(books, number_of_columns, strict=False)
    rendered_page = template.render(books=chunked_books, 
                                    current_page=current_page, 
                                    total_pages=total_pages)
    with open(page_path, 'w', encoding='utf-8') as file:
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

    number_of_rows = 10
    shift_to_count_the_number_of_pages = number_of_rows - 1
    total_pages = (len(books) + shift_to_count_the_number_of_pages) // number_of_rows
    chunked_books = chunked(books, number_of_rows, strict=False)
    for i, ten_books in enumerate(chunked_books, 1):
        page_path = folder_name + '/' + page_name + str(i) + '.html'
        render_page(template, ten_books, page_path, i, total_pages)

    print('Site rebuild')


rebuild()

server = Server()
server.watch('template.html', rebuild)
server.serve(root='.', port=8000)