import json
import os
import shutil

from dotenv import load_dotenv
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
    page_name = os.getenv('PAGE_NAME', 'index')
    folder_name = os.getenv('FOLDER_NAME', 'pages')
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    with open(os.getenv('DATA_FILE', 'meta_data.json'), 'r', encoding='utf-8') as books_file:
        books = json.load(books_file)

    number_of_rows = 10
    shift_to_count_the_number_of_pages = number_of_rows - 1
    total_pages = (len(books) + shift_to_count_the_number_of_pages) // number_of_rows
    chunked_books = chunked(books, number_of_rows, strict=False)
    for page_index, ten_books in enumerate(chunked_books, 1):
        page_path = folder_name + '/' + page_name + str(page_index) + '.html'
        render_page(template, ten_books, page_path, page_index, total_pages)


def main():
    load_dotenv()

    rebuild()

    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.', port=8000)


if __name__ == '__main__':
    main()