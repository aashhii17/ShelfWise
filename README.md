# Shelfwise Library Management

A Django website based on the original `p1.py` console program. It supports browsing and searching books, adding books, issuing books for seven days, tracking active loans, overdue indicators, and returns.

## Run it

```powershell
cd "C:\Users\sande\OneDrive\Desktop\python\library_management"
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser. The first migration automatically loads the 20 books from `p1.py`.

Optional administrator account:

```powershell
python manage.py createsuperuser
```

Then visit http://127.0.0.1:8000/admin/.
# ShelfWise
