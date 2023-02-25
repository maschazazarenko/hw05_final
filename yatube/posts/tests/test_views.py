from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Follow, Post
from ..forms import PostForm
from django.core.cache import cache
from http import HTTPStatus


User = get_user_model()


class PostPagesTests(TestCase):
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
            text='Пост для теста',
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом.
        Проверим, что пост содержит автора, текст, группу.
        Проверим что id поста соответствует тестируемому объекту."""
        response = self.authorized_client.get(reverse("posts:index"))
        test = response.context["page_obj"][0]
        context = {
            self.user: test.author,
            self.post.text: test.text,
            self.group: test.group,
            self.post.id: test.id,
        }
        for reverse_name, response in context.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response, reverse_name)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug}))
        for post in response.context["page_obj"]:
            self.assertEqual(post.group, self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username}))
        for post in response.context["page_obj"]:
            self.assertEqual(post.author, self.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}))
        post_id = response.context["post"].id
        self.assertEqual(post_id, self.post.id)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        test_form = response.context.get('form')
        self.assertIsInstance(test_form, PostForm)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        test_form = response.context.get('form')
        self.assertIsInstance(test_form, PostForm)
        self.assertTrue(response.context['is_edit'])

    def test_check_cache(self):
        """Проверка кеша."""
        response = self.authorized_client.get(reverse("posts:index"))
        test_cache = response.content
        Post.objects.get(id=1).delete()
        response2 = self.authorized_client.get(reverse("posts:index"))
        test_cache2 = response2.content
        self.assertEqual(test_cache, test_cache2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='testslug',
            description='Тестовое описание группы',
        )
        fake_post: list = []
        for i in range(15):
            fake_post.append(Post(
                author=cls.user,
                text=f'Пост для теста {i}',
                group=cls.group)
            )
        Post.objects.bulk_create(fake_post)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_first_page_contains_ten_records(self):
        """Проверим, что количество постов на главной странице равно 10"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_five_records(self):
        """Проверим, что количество постов на второй странице равно 5"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)


class GroupViewsTest(TestCase):
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
            text='Пост для теста',
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_check_display_of_posts_in_group(self):
        """
        Проверим, что пост появился на главной странице,
        странице выбранной группы и в профайле пользователя.
        """
        pages = {
            reverse("posts:index"): Post.objects.get(group=self.post.group),
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in pages.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                pages = response.context["page_obj"]
                self.assertIn(expected, pages)

    def test_check_group_not_in_mistake_group_list_page(self):
        """Проверяем чтобы созданный Пост с группой не попап в чужую группу."""
        pages = {
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in pages.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                pages = response.context["page_obj"]
                self.assertNotIn(expected, pages)


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user")
        cls.author = User.objects.create_user(username="author")
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост для теста'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_autorized_user_can_follow(self):
        """
        Проверим, что авторизированный пользователь может подписаться
        на избранного автора.
        """
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse("posts:profile_follow",
                    kwargs={"username": self.author.username})
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.author).exists()
        )

    def test_autorized_user_can_unfollow(self):
        """
        Проверим, что авторизированный пользователь может отписаться
        от избранного автора.
        """
        author = self.user
        Follow.objects.create(user=self.user, author=author)
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse("posts:profile_unfollow",
                    kwargs={"username": author.username})
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=author).exists()
        )

    def test_new_post_appear_on_follower_page(self):
        """Новая запись пользователя появляется в ленте у фолловеров."""
        self.post = Post.objects.create(
            text="Привет, фолловеры!", author=self.author
        )
        Follow.objects.create(author=self.author, user=self.user)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(response.context["page_obj"][0], self.post)

    def test_new_post_does_not_appear_on_follower_page(self):
        """Новая запись пользователя не появляется в ленте не фолловеров."""
        self.post = Post.objects.create(
            text="Привет, фолловеры!", author=self.author
        )
        Follow.objects.create(author=self.author, user=self.user)
        self.second_user = User.objects.create_user(
            username="username",
        )
        self.authorized_client.force_login(self.second_user)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), 0)
