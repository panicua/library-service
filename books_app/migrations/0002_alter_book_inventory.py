from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="inventory",
            field=models.PositiveIntegerField(),
        ),
    ]
    