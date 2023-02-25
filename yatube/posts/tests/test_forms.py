from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Comment, Group, Post

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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новую запись."""
        posts_count = Post.objects.count()
        new_post = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=new_post,
            follow=True
        )
        self.assertRedirects(response, reverse(
            "posts:profile", kwargs={"username": self.post.author})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text=new_post.get('text'),
            group=self.group.id).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись."""
        new_post = {
            'text': 'Изменили текст, Работает?',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.id}),
            data=new_post,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(Post.objects.filter(
            text=new_post.get('text'),
            group=self.group.id).exists()
        )

    def test_comment_correct_context(self):
        """Проверим, что комментарий создается в базе данных."""
        comments_count = Comment.objects.count()
        test_comment = {
            "text": "Проверим комменты"
        }
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
            data=test_comment,
            follow=True
        )
        self.assertRedirects(response, reverse(
            "posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(Comment.objects.filter(
            text=test_comment.get('text')).exists()
        )
