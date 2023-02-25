# Generated by Django 2.2.16 on 2023-02-24 11:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0006_auto_20230223_1520'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Добавьте комментарий к посту', verbose_name='Комментарий')),
                ('create', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='posts.Post', verbose_name='Пост')),
            ],
            options={
                'ordering': ('-create',),
            },
        ),
        migrations.AddField(
            model_name='post',
            name='comments',
            field=models.ForeignKey(blank=True, help_text='Добавьте комментарий к посту.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Comment', verbose_name='Комментарий'),
        ),
    ]
