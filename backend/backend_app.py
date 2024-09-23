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
SORT_FIELDS = PUT_FIELDS + ['id', 'likes', 'comments']
database = Storage('posts.json')


def generate_unique_id(data=database.posts):
    """Generates unique post id based on highest post id in the database"""
    return max(post['id'] for post in data) + 1 if data else 1


def fetch_post_by_id(post_id, data=database.posts):
    """Returns a post found in database by its id"""
    for post in data:
        if post['id'] == post_id:
            return post


def search_posts_by_field(query, field, data=database.posts):
    """Returns a list of post, that match search criteria in a single field"""
    return [post for post in data if query.lower() in post[field].lower()] if query else []


def get_ids_from_posts(posts=database.posts):
    """Returns a set of ids for list of posts"""
    return {post['id'] for post in posts}


def validate_post_data(data):
    """Returns tuple with bool (is post data valid?)
    and errors (if bool is false) or the post data itself (if bool is True)
    """
    errors = [f'{field} is missing' for field in POST_FIELDS if field not in data or not bool(data[field].strip())]
    return (False, ", ".join(errors)) if bool(errors) else (True, data)


def generate_current_date():
    """Returns current date in YYYY-MM-DD format"""
    return datetime.datetime.now().strftime('%Y-%m-%d')


def validate_date(string):
    """Checks if provided string holds a valid date in YYYY-MM-DD format, returns bool"""
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
    """Converts date-based string into datatime object"""
    year, month, day = date_string.split('-')
    return datetime.date(int(year), int(month), int(day))


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Returns list of posts in sorted order based on request parameters.
    If one or more parameters are invalid, returns errors
    """
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
    return jsonify(sorted(posts_sorted, key=lambda item: get_sort_item(sort_key, item), reverse=descending_order))


def get_sort_item(sort_key, item):
    """Returns a string or an integer for key parameter of sorted function depending on input item's type"""
    if sort_key == 'date':
        return convert_date_string_into_datetime(item[sort_key])
    if isinstance(item.get(sort_key), str):
        return item.get(sort_key, "0").lower()
    elif isinstance(item.get(sort_key), list):
        return len(item.get(sort_key, []))
    else:
        return item.get(sort_key, 0)


@app.route('/api/posts', methods=['POST'])
def add_post():
    """Checks if request holds valid post data. Then adds a post to a database, returns added post.
    If request data is invalid, returns errors"""
    is_valid, data = validate_post_data(request.get_json())
    if not is_valid:
        return jsonify({'error': f'Bad request: {data}.'}), 400
    data['id'] = generate_unique_id()
    data['date'] = generate_current_date()
    database.append(data)
    return jsonify(data), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Deletes a post from database by post_id"""
    post = fetch_post_by_id(post_id)
    if not post:
        return jsonify({'error': f'There is no post with id {post_id}.'}), 404
    database.remove(post)
    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Updates field(s) of the post with provided information"""
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
    database.posts = database.posts
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """Returns a list of posts matching search criteria"""
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
    """Adds one like to a post with post_id"""
    post = fetch_post_by_id(post_id)
    if 'likes' in post.keys():
        post['likes'] += 1
    else:
        post['likes'] = 1
    database.posts = database.posts
    return jsonify(post), 200


@app.route('/api/posts/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """Adds a comment to a post with post_id"""
    post = fetch_post_by_id(post_id)
    comment = request.get_json()
    if 'comments' not in post:
        post['comments'] = []
    if comment.get('comment').strip():
        post['comments'].append(comment['comment'])
        database.posts = database.posts
        return jsonify(comment), 201
    else:
        return jsonify({'error': 'Bad request: expected key comment with non-empty value'}), 400


def main():
    """Runs Flask application"""
    app.run(host="0.0.0.0", port=5002, debug=True)


if __name__ == '__main__':
    main()
