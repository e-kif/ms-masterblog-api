from flask import Flask, jsonify
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


def validate_post_data(data=POSTS):
    return 'title' in data and bool(data['title']) and 'content' in data and bool(data['content'])


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
