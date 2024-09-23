from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import datetime
import re
from storage import Storage

SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POST_FIELDS = ['title', 'content', 'author']
PUT_FIELDS = POST_FIELDS + ['date']
SORT_FIELDS = PUT_FIELDS + ['id', 'likes']
database = Storage('posts.json')


def generate_unique_id(data=database.posts):
    return max(post['id'] for post in data) + 1 if data else 1


def fetch_post_by_id(post_id, data=database.posts):
    for post in data:
        if post['id'] == post_id:
            return post


def search_posts_by_field(query, field, data=database.posts):
    return [post for post in data if query.lower() in post[field].lower()] if query else []


def get_ids_from_posts(posts=database.posts):
    return {post['id'] for post in posts}


def validate_post_data(data):
    errors = [f'{field} is missing' for field in POST_FIELDS if field not in data or not bool(data[field].strip())]
    return (False, ", ".join(errors)) if bool(errors) else (True, data)


def generate_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def validate_date(string):
    date_pattern = re.compile("\d{4}-\d{2}-\d{2}")
    if not date_pattern.match(string):
        return False
    date_parts = string.split('-')
    try:
        date = datetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
        if date > datetime.date.today():
            raise ValueError
    except ValueError:
        return False
    return True


def convert_date_string_into_datetime(date_string):
    year, month, day = date_string.split('-')
    return datetime.date(int(year), int(month), int(day))


@app.route('/api/posts', methods=['GET'])
def get_posts():
    params = ['sort', 'direction']
    for key in request.args:
        if key not in params:
            return jsonify({'error': f'Bar request: unexpected key {key}'})
    sort_key = request.args.get('sort')
    sort_direction = request.args.get('direction')
    if not sort_key and not sort_direction:
        return jsonify(database.posts)
    errors = []
    if sort_key not in [None] + SORT_FIELDS:
        errors.append(f'not supported sort argument {sort_key}')
    if sort_direction not in (None, 'asc', 'desc'):
        errors.append(f'not supported direction argument {sort_direction}')
    if errors:
        return jsonify({'error': f'Bad request: {", ".join(errors)}'}), 400
    if not sort_key:
        sort_key = 'id'
    posts_sorted = database.posts[:]
    descending_order = sort_direction == 'desc'
    return (jsonify(sorted(posts_sorted,
                           key=lambda item: convert_date_string_into_datetime(item[sort_key]),
                           reverse=descending_order))
            if sort_key == 'date'
            else jsonify(sorted(posts_sorted, key=lambda item: item.get(sort_key, 0).lower() if isinstance(item.get(sort_key, 0), str) else item.get(sort_key, 0), reverse=descending_order)))


@app.route('/api/posts', methods=['POST'])
def add_post():
    is_valid, data = validate_post_data(request.get_json())
    if not is_valid:
        return jsonify({'error': f'Bad request: {data}.'}), 400
    data['id'] = generate_unique_id()
    data['date'] = generate_current_date()
    database.posts.append(data)
    database.update_storage_file(database.posts)
    return jsonify(data), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = fetch_post_by_id(post_id)
    if not post:
        return jsonify({'error': f'There is no post with id {post_id}.'}), 404
    database.posts.remove(post)
    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = fetch_post_by_id(post_id)
    if not post:
        return jsonify({'error': f'post with id {post_id} not found.'}), 404
    put_data = request.get_json()
    if not set(put_data.keys()).intersection(set(PUT_FIELDS)):
        return jsonify({'error': 'Bad request. Input JSON should contain one of the following fields: '
                                 f'{", ".join(PUT_FIELDS)}'}), 400
    for key in put_data.keys():
        if key not in PUT_FIELDS:
            return jsonify({'error': f'Bad request: unknown property {key}'})
        if put_data.get(key):
            post[key] = request.get_json()[key]
    database.update_storage_file(database.posts)
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    posts_ids = set()
    queries = []
    for key in request.args:
        if key not in PUT_FIELDS:
            return jsonify({'error': f'Bad request: unexpected key {key}'}), 400
    for field in PUT_FIELDS:
        query = request.args.get(field)
        if query:
            posts = search_posts_by_field(query, field)
            queries.append(query)
            if posts and len(queries) == 1 and not posts_ids:
                posts_ids = get_ids_from_posts(posts)
            elif posts_ids:
                posts_ids = posts_ids.intersection(get_ids_from_posts(posts))
    return [fetch_post_by_id(post_id) for post_id in set(posts_ids)]


@app.route('/api/posts/<int:post_id>/like')
def like_post(post_id):
    post = fetch_post_by_id(post_id)
    if 'likes' in post.keys():
        post['likes'] += 1
    else:
        post['likes'] = 1
    database.update_storage_file(database.posts)
    return jsonify(post), 200


@app.route('/api/posts/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    post = fetch_post_by_id(post_id)
    comment = request.get_json()
    if 'comments' not in post:
        post['comments'] = []
    if comment.get('comment').strip():
        post['comments'].append(comment['comment'])
        database.update_storage_file(database.posts)
        return jsonify(comment), 201
    else:
        return jsonify({'error': 'Bad request: expected key comment with non-empty value'}), 400



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
