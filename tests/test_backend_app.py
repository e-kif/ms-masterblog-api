import pytest
from backend.backend_app import (validate_post_data,
                                 generate_unique_id,
                                 fetch_post_by_id)


POSTS = [
        {'id': 1, 'title': 'post one', 'content': '001'},
        {'id': 2, 'title': 'post two', 'content': '002'},
        {'id': 3, 'title': 'post tree', 'content': '003'}
    ]


def test_validate_post_data():
    assert validate_post_data({'title': 'title', 'content': 'content'}) == True
    assert validate_post_data({'titles': 'title', 'content': 'content'}) == False
    assert validate_post_data({'title': 'title', 'contents': 'content'}) == False
    assert validate_post_data({'title': '', 'content': 'content'}) == False
    assert validate_post_data({'title': 'title', 'contents': ''}) == False


def test_generate_unique_id():
    posts = [{'id': 35}, {'id': 1442}, {'id': 1}]
    assert generate_unique_id(posts) == 1443
    assert generate_unique_id([]) == 1


def test_fetch_post_by_id():
    assert fetch_post_by_id(1, POSTS) == {'id': 1, 'title': 'post one', 'content': '001'}
    assert fetch_post_by_id(3, POSTS) == {'id': 3, 'title': 'post tree', 'content': '003'}
    assert fetch_post_by_id(4, POSTS) is None
    assert fetch_post_by_id(2, []) is None
