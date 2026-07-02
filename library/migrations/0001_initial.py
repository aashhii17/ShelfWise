from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=250, unique=True)),
                ("author", models.CharField(max_length=250)),
                ("year", models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={"ordering": ["title"]},
        ),
        migrations.CreateModel(
            name="Loan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("borrower_name", models.CharField(max_length=120)),
                ("borrower_id", models.CharField(max_length=50)),
                ("issued_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("due_date", models.DateField()),
                ("returned_at", models.DateTimeField(blank=True, null=True)),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="loans", to="library.book")),
            ],
            options={"ordering": ["-issued_at"]},
        ),
    ]
