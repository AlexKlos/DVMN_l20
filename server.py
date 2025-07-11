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
    chunked_books = chunked(books, 2, strict=False)
    rendered_page = template.render(books=chunked_books, 
                                    current_page=current_page, 
                                    total_pages=total_pages)
    with open(page_path, 'w', encoding='utf-8') as file:
        file.write(rendered_page)


def serve_txt_files():
    class TxtAsHtmlHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            path = unquote(self.path.lstrip("/"))
            if path.endswith(".txt") and os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()

                html = textwrap.dedent(f"""\
                    <!DOCTYPE html>
                    <html lang="ru">
                    <head>
                      <meta charset="utf-8">
                      <title>{path}</title>
                    </head>
                    <body>
                      <pre>{text}</pre>
                    </body>
                    </html>
                """)

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html.encode("utf-8"))))
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            else:
                super().do_GET()

    server = HTTPServer(('localhost', 8000), TxtAsHtmlHandler)
    server.serve_forever()


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

    total_pages = (len(books) + 9) // 10
    chunked_books = chunked(books, 10, strict=False)
    for i, ten_books in enumerate(chunked_books, 1):
        page_path = folder_name + '/' + page_name + str(i) + '.html'
        render_page(template, ten_books, page_path, i, total_pages)

    print('Site rebuild')


rebuild()

livereload_server = Server()
livereload_server.watch('template.html', rebuild)
threading.Thread(target=livereload_server.serve, kwargs={'port': 35729}, daemon=True).start()
serve_txt_files()