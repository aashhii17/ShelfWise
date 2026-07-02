from django.db import migrations


BOOKS = [
    ("Python Crash Course, 3rd Edition", "Eric Matthes", 2019),
    ("Fluent Python, 2nd Edition", "Luciano Ramalho", 2022),
    ("Automate the Boring Stuff with Python, 3rd Edition", "Al Sweigart", 2025),
    ("Effective Python, 3rd Edition", "Brett Slatkin", 2024),
    ("Head First Python, 2nd Edition", "Paul Barry", 2016),
    ("Programming Python", "Mark Lutz", 2010),
    ("Core Java, Volume I: Fundamentals, 13th Edition", "Cay S. Horstmann", 2024),
    ("Effective Java, 3rd Edition", "Joshua Bloch", 2018),
    ("Head First Java, 3rd Edition", "Kathy Sierra, Bert Bates, Trisha Gee", 2022),
    ("Java: The Complete Reference, 13th Edition", "Herbert Schildt, Dr. Danny Coward", 2024),
    ("The Java Programming Language, 3rd Edition", "Ken Arnold, James Gosling, David Holmes", 2000),
    ("The C++ Programming Language, 4th Edition", "Bjarne Stroustrup", 2013),
    ("Effective C++, 3rd Edition", "Scott Meyers", 2005),
    ("The Design and Evolution of C++", "Bjarne Stroustrup", 1994),
    ("The Annotated C++ Reference Manual", "Margaret A. Ellis, Bjarne Stroustrup", 1990),
    ("Programming: C++ Principles and Practice", "Bjarne Stroustrup", 2024),
    ("Introduction to Data Science: Data Wrangling and Visualization with R", "Rafael A. Irizarry", None),
    ("Doing Data Science", "Rachel Schutt, Cathy O'Neil", 2013),
    ("Data Science", "John Kelleher, Brendan Tierney", 2018),
    ("Data Science and Analytics with Python", "Various", None),
]


def seed_books(apps, schema_editor):
    Book = apps.get_model("library", "Book")
    Book.objects.bulk_create([Book(title=t, author=a, year=y) for t, a, y in BOOKS], ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [("library", "0001_initial")]
    operations = [migrations.RunPython(seed_books, migrations.RunPython.noop)]
