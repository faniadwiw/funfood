# Generated by Django 5.1.2 on 2024-12-10 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funfood_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.TextField(help_text='Separate each ingredient with a newline.'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='steps',
            field=models.TextField(help_text='Separate each step with a newline.'),
        ),
    ]
