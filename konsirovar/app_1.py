import uuid
import psycopg2
from psycopg2 import extras, Error
from flask import Flask, jsonify, request
from flask_cors import CORS

BOOKS = []

def db_get():
    global BOOKS
    global error
    BOOKS = []
    error = ''
    try:
        pg = psycopg2.connect("""
            host=localhost
            dbname=postgres
            user=postgres
            password=kos120675
            port=5432
        """)

        cursor = pg.cursor()
        cursor = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("SELECT * FROM books")
        result = cursor.fetchall()

    except (Exception, Error) as error:

        print(f'DB ERROR: {error}')

    finally:
        if pg:
            cursor.close
            pg.close
            print("Соединение с PostgreSQL закрыто")

    for row in result:
        BOOKS.append(dict(row))


db_get()


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# def remove_book(book_id):
#     for book in BOOKS:
#         if book['id'] == book_id:

#             BOOKS.remove(book)

#             return True
#     return False

def db_delete(book_id):
    global BOOKS
    # global db_get
    try:
        pg = psycopg2.connect("""
            host=localhost
            dbname=postgres
            user=postgres
            password=kos120675
            port=5432
        """)

        cursor = pg.cursor()
        cursor = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(f"DELETE FROM books WHERE id=$${str(book_id)}$$")
        pg.commit()

        check_db = True
    
    except (Exception, Error) as error:
        check_db = False

    finally:
        if pg:
            cursor.close
            pg.close
            if not check_db:
                res = f'Ошибка подключения к базе данных: '
            else:
                res = f'Книга удалена!'

    db_get()

    return res


def db_add(data):
    global BOOKS
    # global db_get
    try:
        pg = psycopg2.connect("""
            host=localhost
            dbname=postgres
            user=postgres
            password=kos120675
            port=5432
        """)
        cursor = pg.cursor()

        new_id = uuid.uuid4().hex
        books_to_write = (new_id, data.get('title'), data.get('author'), data.get('read'))

        cursor.execute(f"INSERT INTO books(id, title, author, read) VALUES {books_to_write}")
        pg.commit()

        check_db = True

    except (Exception, Error) as error:
        check_db = False


    finally:
        if pg:
            cursor.close
            pg.close
            if not check_db:
                res = f'Ошибка подключения к базе данных:'
            else:
                res = f'Книга добавлена!'

    db_get()
    return res

def db_update(data, id):
    global BOOKS
    # global db_get
    db_delete(id)
    try:
        pg = psycopg2.connect("""
            host=localhost
            dbname=postgres
            user=postgres
            password=kos120675
            port=5432
        """)
        cursor = pg.cursor()

        new_id = uuid.uuid4().hex
        books_to_write = (id, data.get('title'), data.get('author'), data.get('read'))

        cursor.execute(f"INSERT INTO books(id, title, author, read) VALUES {books_to_write}")
        pg.commit()

        check_db = True

    except (Exception, Error) as error:
        check_db = False


    finally:
        if pg:
            cursor.close
            pg.close
            if not check_db:
                res = f'Ошибка подключения к базе данных: '
            else:
                res = f'Книга добавлена!'

    db_get()
    return res

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/books', methods=['GET', 'POST'])
def all_books():
    global BOOKS
    global db_get

    response_object = {'status': 'success'}

    if request.method == 'POST':
        post_data = request.get_json()

        add_message = db_add(post_data)

        response_object['message'] = add_message
    else:
        response_object['books'] = BOOKS
    return jsonify(response_object)


@app.route('/books/<book_id>', methods=['PUT', 'DELETE'])
def single_book(book_id):
    global BOOKS
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        # remove_book(book_id)
        db_update(post_data, book_id)
        # BOOKS.append({
        #     'id': book_id,
        #     'title': post_data.get('title'),
        #     'author': post_data.get('author'),
        #     'read': post_data.get('read')
        # })
        response_object['message'] = 'Book updated!'
    if request.method == 'DELETE':
        db_delete(book_id)
        # remove_book(book_id)
        response_object['message'] = 'Book removed!'

    return jsonify(response_object)


if __name__ == '__main__':
    app.run()