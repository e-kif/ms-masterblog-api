import datetime
from backend.backend_app import (validate_post_data,
                                 generate_unique_id,
                                 fetch_post_by_id,
                                 search_posts_by_field,
                                 get_ids_from_posts,
                                 validate_date,
                                 convert_date_string_into_datetime,
                                 POST_FIELDS)

POSTS = [
    {'id': 1, 'title': 'post one', 'content': '001'},
    {'id': 2, 'title': 'post two', 'content': '002'},
    {'id': 3, 'title': 'post tree', 'content': '003'}
]


def test_validate_post_data():
    assert validate_post_data({'title': '1', 'content': '2', 'author': '3'})[0]
    assert validate_post_data({'title': '1', 'content': '2', 'author': '3'})[1] == {'title': '1',
                                                                                    'content': '2',
                                                                                    'author': '3'}
    assert not validate_post_data({'titles': '1', 'content': '2', 'author': '3'})[0]
    assert not validate_post_data({'title': '1', 'contents': '2', 'author': '3'})[0]
    assert not validate_post_data({'title': '', 'content': '2', 'author': '3'})[0]
    assert not validate_post_data({'title': '1', 'contents': '', 'author': '3'})[0]
    assert not validate_post_data({'title': '1', 'content': '2', 'autor': '3'})[0]
    assert not validate_post_data({'title': '1', 'content': '2', 'auttor': ''})[0]


def test_generate_unique_id():
    posts = [{'id': 35}, {'id': 1442}, {'id': 1}]
    assert generate_unique_id(posts) == 1443
    assert generate_unique_id([]) == 1


def test_fetch_post_by_id():
    assert fetch_post_by_id(1, POSTS) == {'id': 1, 'title': 'post one', 'content': '001'}
    assert fetch_post_by_id(3, POSTS) == {'id': 3, 'title': 'post tree', 'content': '003'}
    assert fetch_post_by_id(4, POSTS) is None
    assert fetch_post_by_id(2, []) is None


def test_search_posts_by_field():
    posts = [
        {'title': 'Title1', 'id': 1, 'content': 'first post'},
        {'title': 'Title11', 'id': 2, 'content': 'second post'},
        {'title': 'Title22', 'id': 3, 'content': 'third post'},
        {'title': 'Title2', 'id': 4, 'content': 'fourth post'},
        {'title': 'Title23', 'id': 5, 'content': 'fifth post'},
        {'title': 'Title19', 'id': 6, 'content': 'sixth post'},
    ]
    assert search_posts_by_field('1', 'title', posts) == [{'title': 'Title1',
                                                           'id': 1,
                                                           'content': 'first post'},
                                                          {'title': 'Title11',
                                                           'id': 2,
                                                           'content': 'second post'},
                                                          {'title': 'Title19',
                                                           'id': 6,
                                                           'content': 'sixth post'}]
    assert search_posts_by_field('4', 'title', []) == []
    assert search_posts_by_field('23', 'title', posts) == [{'title': 'Title23',
                                                            'id': 5,
                                                            'content': 'fifth post'}]
    assert search_posts_by_field('second', 'content', posts) == [{'title': 'Title11',
                                                                  'id': 2,
                                                                  'content': 'second post'}]
    assert search_posts_by_field('fi', 'content', posts) == [{'title': 'Title1',
                                                              'id': 1,
                                                              'content': 'first post'},
                                                             {'title': 'Title23',
                                                              'id': 5,
                                                              'content': 'fifth post'}]
    assert search_posts_by_field('', 'title', posts) == []


def test_get_ids_from_posts():
    assert get_ids_from_posts([{'id': 1}, {'id': 2}]) == {1, 2}
    assert get_ids_from_posts([]) == set()
    assert get_ids_from_posts([{'id': 5}]) == {5}


def test_validate_date():
    assert not validate_date('2025-12-02')
    assert validate_date('2024-09-05')
    assert not validate_date('2024.01.02')
    assert not validate_date('31-12-2012')
    assert not validate_date('2024-02-30')
    assert not validate_date('2023-14-04')
    assert not validate_date('2023-1-04')
    assert not validate_date('2023-01-00')


def test_convert_date_string_into_datetime():
    assert convert_date_string_into_datetime('2024-03-05') == datetime.date(2024, 3, 5)
