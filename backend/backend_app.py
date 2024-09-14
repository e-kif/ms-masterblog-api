from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def generate_unique_id(data=POSTS):
    return max(post['id'] for post in data) + 1 if data else 1


def fetch_post_by_id(post_id, data=POSTS):
    for post in data:
        if post['id'] == post_id:
            return post


def validate_post_data(data):
    fields = ['title', 'content']
    errors = [f'{field} is missing' for field in fields if field not in data or not bool(data[field].strip())]
    return (False, ", ".join(errors)) if bool(errors) else (True, data)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    is_valid, data = validate_post_data(request.get_json())
    if not is_valid:
        return jsonify({'error': f'Bad request: {data}'}), 400
    data['id'] = generate_unique_id()
    POSTS.append(data)
    return jsonify(data), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
