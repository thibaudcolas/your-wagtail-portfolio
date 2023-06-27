from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0006_author"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpage",
            name="authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, to="blog.author"
            ),
        ),
    ]
