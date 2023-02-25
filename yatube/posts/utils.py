from django.core.paginator import Paginator

# Константа обозначает количество постов в выборке.
NUMBER_OF_POSTS = 10


def get_paginator(request, posts):
    """
    Добавим дополнительную функцию, которая
    разделит посты между страницами.
    По 10 постов на каждую.
    """
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
