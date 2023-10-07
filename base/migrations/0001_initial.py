# Generated by Django 4.2.2 on 2023-08-11 12:57

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NavigationSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "twitter_url",
                    models.URLField(blank=True, verbose_name="Twitter URL"),
                ),
                ("github_url", models.URLField(blank=True, verbose_name="GitHub URL")),
                (
                    "mastodon_url",
                    models.URLField(blank=True, verbose_name="Mastodon URL"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
