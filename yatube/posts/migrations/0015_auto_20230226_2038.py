# Generated by Django 2.2.16 on 2023-02-26 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coments', to='posts.Post', verbose_name='Пост'),
        ),
    ]