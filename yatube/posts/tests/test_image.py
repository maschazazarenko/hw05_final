import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from ..models import Group, Post
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="NoName")
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='testslug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост для теста',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_image_on_page(self):
        """Проверяем, что картинка появляется на следующих страницах:
        главной, страннице групп, в профайле автора"""
        templates = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.post.author}),
        )
        for page in templates:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                test_image = response.context["page_obj"][0]
                self.assertEqual(test_image.image, self.post.image)

    def test_image_in_post_detail_page(self):
        """Картинка передается на страницу post_detail."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        test_image = response.context["post"]
        self.assertEqual(test_image.image, self.post.image)

    def test_create_post_with_image(self):
        """
        Проверим, что запись с картинкой
        сохранится в базе данных.
        """
        posts_count = Post.objects.count()
        test_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='image.gif',
            content=test_image,
            content_type='image/gif'
        )
        new_post = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=new_post,
            follow=True
        )
        test = Post.objects.first()
        self.assertRedirects(response, reverse(
            "posts:profile", kwargs={"username": self.post.author})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(test.image.name.endswith(
            new_post["image"].name)
        )
