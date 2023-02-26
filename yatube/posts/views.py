from django.shortcuts import get_object_or_404, redirect, render
from .models import Follow, Group, Post, User
from .forms import CommentForm, PostForm
from django.contrib.auth.decorators import login_required
from posts.utils import get_paginator
from django.views.decorators.cache import cache_page


CACHE_TiMEOUT = 20


@cache_page(CACHE_TiMEOUT, key_prefix="index_page")
def index(request):
    """
    Отображение главной страницы блога. Переменная "Post"
    выводит выборку последних 10 записей, фильтрация по дате, по убыванию.
    Сделаем выборку по авторам и группам.
    """
    posts = Post.objects.select_related('author', 'group')
    page_obj = get_paginator(request, posts)
    context = {
        'posts': posts,
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """
    Отображение всех записей выбранной группы. Переменная "Post"
    выводит выборку последних 10 записей, фильтрация по дате, по убыванию.
    Сделаем выборку по авторам.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = get_paginator(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context, slug)


def profile(request, username):
    """
    Отображение записей конкретного автора.
    Так же показывает количество записей этого автора.
    Выведем на страницу по 10 записей.
    """
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_paginator(request, posts)
    following = author.following.exists()
    context = {
        'following': following,
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """
    Выводит подробную информацию о выбранном посте.
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """
    Позволяет зарегистрированному пользователю
    делать собственные записи.
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {
        'form': form
    }
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
        return render(request, 'posts/create_post.html', context)
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """
    Позволяет зарегистрированному пользователю
    редактировать собственные записи.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    """
    Позволяет зарегистрированному пользователю
    оставлять коментарии к записям.
    """
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница с лентой пользователя."""
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_paginator(request, posts)
    context = {
        'title': "Избранные посты",
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Система подписки на автора."""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:follow_index")


@login_required
def profile_unfollow(request, username):
    """Система отписки от автора."""
    author = get_object_or_404(User, username=username)
    author.following.filter(user=request.user).delete()
    return redirect("posts:follow_index")
