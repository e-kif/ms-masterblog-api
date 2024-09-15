from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

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

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "content": "This is the third post."},
    {"id": 4, "title": "Fourth post", "content": "Another post."},
    {"id": 5, "title": "Fifth post", "content": "This is the post number five."},
]


def generate_unique_id(data=POSTS):
    return max(post['id'] for post in data) + 1 if data else 1


def fetch_post_by_id(post_id, data=POSTS):
    for post in data:
        if post['id'] == post_id:
            return post


def search_posts_by_field(query, field, data=POSTS):
    return [post for post in data if query.lower() in post[field].lower()] if query else []


def get_ids_from_posts(posts):
    return {post['id'] for post in posts}


def validate_post_data(data):
    fields = ['title', 'content']
    errors = [f'{field} is missing' for field in fields if field not in data or not bool(data[field].strip())]
    return (False, ", ".join(errors)) if bool(errors) else (True, data)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_key = request.args.get('sort')
    sort_direction = request.args.get('direction')
    if not sort_key and not sort_direction:
        return jsonify(POSTS)
    errors = []
    if sort_key not in (None, 'title', 'content'):
        errors.append(f'not supported sort argument {sort_key}')
    if sort_direction not in (None, 'asc', 'desc'):
        errors.append(f'not supported direction argument {sort_direction}')
    if errors:
        return jsonify({'error': f'Bad request: {", ".join(errors)}'}), 400
    if not sort_key:
        sort_key = 'id'
    posts_sorted = POSTS[:]
    descending_order = sort_direction == 'desc'
    return jsonify(sorted(posts_sorted, key=lambda item:item[sort_key], reverse=descending_order))


@app.route('/api/posts', methods=['POST'])
def add_post():
    is_valid, data = validate_post_data(request.get_json())
    if not is_valid:
        return jsonify({'error': f'Bad request: {data}.'}), 400
    data['id'] = generate_unique_id()
    POSTS.append(data)
    return jsonify(data), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = fetch_post_by_id(post_id)
    if not post:
        return jsonify({'error': f'There is no post with id {post_id}.'}), 404
    POSTS.remove(post)
    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = fetch_post_by_id(post_id)
    if not post:
        return jsonify({'error': f'post with id {post_id} not found.'}), 404
    fields = ['title', 'content']
    put_data = request.get_json()
    for key in put_data.keys():
        if key in fields:
            for field in fields:
                if put_data.get(field):
                    post[field] = request.get_json()[field]
            return jsonify(post), 200
    return jsonify({'error': 'Bad request. Input JSON should contain one of the following fields: '
                             f'{", ".join(fields)}'}), 400


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title')
    content = request.args.get('content')
    title_ids = get_ids_from_posts(search_posts_by_field(title, 'title'))
    content_ids = get_ids_from_posts(search_posts_by_field(content, 'content'))
    if not title:
        title_ids = content_ids
    elif not content:
        content_ids = title_ids
    return [fetch_post_by_id(post_id) for post_id in title_ids.intersection(content_ids)]


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
