from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post, User
from django.urls import reverse
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='testslug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост для теста'
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse("posts:index"): 'posts/index.html',
            reverse("posts:group_list", kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse("posts:profile", kwargs={'username': self.user}):
            'posts/profile.html',
            reverse("posts:post_detail", kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse("posts:post_create"): 'posts/create_post.html',
            reverse("posts:post_edit", kwargs={'post_id': self.post.id}):
            'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_accsess_urls_for_guest_client(self):
        """
        Доступ неавторизованному пользователю на главную страницу,
        страницу группы, страницу пользователя и детали поста.
        """
        pages = {
            reverse("posts:index"): 'posts/index.html',
            reverse("posts:group_list", kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse("posts:profile", kwargs={'username': self.user}):
            'posts/profile.html',
            reverse("posts:post_detail", kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
        }
        for page in pages:
            response = self.guest_client.get(page)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_accsess_post_create_for_authorized_client(self):
        """
        Доступ авторизованному пользователю
        на страницу создания новой записи.
        """
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_accsess_comment_for_authorized_client(self):
        """
        Проверим, что при попытке написать комментарий,
        неавторизированный пользователь перенаправится на страницу входа.
        """
        response = self.guest_client.get(
            reverse("posts:add_comment", kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, f"/auth/login/?next=/posts/{self.post.id}/comment/"
        )

    def test_error_uri_returns_404(self):
        """Проверим, что страница 404 отдаст кастомный шаблон."""
        response = self.client.get('/post/test')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
